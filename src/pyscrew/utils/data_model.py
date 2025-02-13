"""
Core data model for screw operation analysis.

This module implements a hierarchical data structure for analyzing screw operations:

ScrewDataset
    └── ScrewRun (multiple)
        └── ScrewStep (multiple)
            └── Measurements (time, torque, angle, gradient) + "step" to track measurement origin

The data comes from two sources:
1. JSON files: Contain measurement data and step information
2. CSV file: Contains metadata and classification information

Key Classes:
    - ScrewDataset: Main interface for loading and filtering screw operation data
    - ScrewRun: Represents one complete screw operation with multiple steps
    - ScrewStep: Represents one step in a screw operation with measurements

Field Definitions:
    - JsonFields: Field names used in JSON measurement files
    - CsvFields: Field names used in CSV label file
"""

import json
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Union

import pandas as pd

from pyscrew.utils.config_schema import ConfigSchema
from pyscrew.utils.logger import get_logger


@dataclass
class JsonFields:
    """
    Constants for field names in the JSON files containing screw operation data.
    These classes define the naming conventions used in the raw JSON data files
    from the screw driving control.

    Note: The string values (e.g. "id code", "time values") are pre-defined by
    the screw driving control and cannot be changed. Our constant names use a
    more consistent style.
    """

    @dataclass
    class Run:
        """
        Run-level metadata fields in the JSON.
        These fields describe the overall properties of a complete screw operation run.

        Attributes:
            DATE: Date when the run was performed
            RESULT: Overall result from the screw driving control ("OK"/"NOK")
            DMC: Machine-defined identification code for each workpiece
            STEPS: Collection of tightening steps in the run
        """

        ID: str = "cycle"
        DATE: str = "date"
        RESULT_VALUE: str = "result"
        WORKPIECE_ID: str = "id code"
        STEPS: str = "tightening steps"

    @dataclass
    class Step:
        """
        Step-level metadata fields in the JSON.
        These fields describe individual steps within a screw operation run.

        Attributes:
            ID: Cycle identifier for the step
            NAME: Name identifier as set in screw driving control
            TYPE: Type classification (simply "standard")
            RESULT: Result status ("OK"/"NOK")
            QUALITY: Quality assessment code
            GRAPH: Measurement data dictionary
        """

        NAME: str = "name"
        STEP_TYPE: str = "step type"  # dont just use type as it is a reserved keyword
        RESULT_VALUE: str = "result"
        QUALITY_CODE: str = "quality code"
        GRAPH: str = "graph"

    @dataclass
    class Measurements:
        """
        Measurement field names in the JSON graph data.
        These are the keys used in the GRAPH dictionary for each measurement type.

        Attributes:
            TIME: Time measurements (0.0012s increments)
            TORQUE: Torque measurements
            ANGLE: Angle measurements (0.25° amplitude)
            GRADIENT: Gradient measurements

        Note:
            "angleRed values" and "torqueRed values" exist but are always [0,...,0]
            and are not used in processing.
        """

        TIME: str = "time values"
        TORQUE: str = "torque values"
        ANGLE: str = "angle values"
        GRADIENT: str = "gradient values"
        # Added with the unpacking steps
        STEP: str = "step values"
        CLASS: str = "class values"


@dataclass
class CsvFields:
    """
    Constants for field names in the labels CSV file.
    These fields connect the JSON measurement data with metadata about runs
    and provide classification information.

    Attributes:
        ID: Unique identifier for each run
        FILE_NAME: Links to corresponding JSON file
        CLASS_VALUE: Scenario-specific classification label
        RESULT_VALUE: Result from screw program ("OK"/"NOK")
        WORKPIECE_ID: Data matrix code identifying the workpiece
        WORKPIECE_USAGE: Number of times this workpiece has been used
        WORKPIECE_LOCATION: Screw position in workpiece (0 or 1)
    """

    # Identifier fields
    RUN_ID: str = "run_id"  # aka "cycle" in the json data
    FILE_NAME: str = "file_name"

    # Value fields
    CLASS_VALUE: str = "class_value"
    RESULT_VALUE: str = "result_value"

    # Workpiece-related fields
    WORKPIECE_ID: str = "workpiece_id"
    WORKPIECE_USAGE: str = "workpiece_usage"
    WORKPIECE_LOCATION: str = "workpiece_location"

    @dataclass
    class DatasetFields:
        """
        Constants for field names in the dataset.
        These fields are used to access the processed data from the ScrewDataset.

        TODO: While currently not in use, this class finally moves away from the
        space-based naming convention of the json files to a more consistent
        underscore-based style. Will be added to the pipeline in the future.
        """

        TIME_VALUES: str = "time_values"
        TORQUE_VALUES: str = "torque_values"
        ANGLE_VALUES: str = "angle_values"
        GRADIENT_VALUES: str = "gradient_values"
        CLASS_VALUES: str = "class_labels"


logger = get_logger(__name__)


class ScrewStep:
    """
    Represents a single step in a screw operation run.

    This class encapsulates all data and metadata for one step of a multi-step
    screw operation. It handles both the step's descriptive metadata and its
    measurement time series data. Usually, a four-step screw operation consists
    of four of these. In case of an error during tightening, less steps are recorded.

    Args:
        step_data: Dictionary containing step metadata and measurements
        step_number: Sequential number of this step in the run

    Attributes:
        id: Step cycle identifier from screw program
        step_number: Position in sequence of steps (0-indexed)
        name: Identifier name of the step
        step_type: Classification of step type (typically "standard")
        result: Result status ("OK" or "NOK")
        quality_code: Quality assessment code
        time: List of time measurements in 0.0012s increments
        torque: List of torque measurements
        angle: List of angle measurements (0.25° amplitude)
        gradient: List of gradient measurements

    Raises:
        ValueError: If any required fields are missing in step_data

    Example:
        >>> step_data = {
        ...     "cycle": "1",
        ...     "name": "Step 1",
        ...     "step type": "standard",
        ...     "result": "OK",
        ...     "quality code": "A1",
        ...     "graph": {
        ...         "time values": [0.0, 0.0012, 0.0024],
        ...         "torque values": [1.0, 1.5, 2.0],
        ...         "angle values": [0.0, 0.25, 0.5],
        ...         "gradient values": [0.0, 0.1, 0.2]
        ...     }
        ... }
        >>> step = ScrewStep(step_data, step_number=0)
    """

    def __init__(
        self,
        step_data: Dict[str, Any],
        step_number: int,
    ):
        try:
            # Step metadata
            self.step_number = step_number
            # Use direct dictionary access to raise KeyError if missing
            self.name = step_data[JsonFields.Step.NAME]
            self.step_type = step_data[JsonFields.Step.STEP_TYPE]
            self.result = step_data[JsonFields.Step.RESULT_VALUE]
            self.quality_code = step_data[JsonFields.Step.QUALITY_CODE]

            # Get measurement data as lists from "graph" in the json file
            graph_data = step_data[JsonFields.Step.GRAPH]
            self.time = graph_data[JsonFields.Measurements.TIME]
            self.torque = graph_data[JsonFields.Measurements.TORQUE]
            self.angle = graph_data[JsonFields.Measurements.ANGLE]
            self.gradient = graph_data[JsonFields.Measurements.GRADIENT]

        except KeyError as e:
            raise ValueError(f"Required field missing in step data: {str(e)}")

    def get_values(self, measurement_name: str) -> List[float]:
        """
        Retrieve the list of values for a specific measurement type.

        Each step records multiple types of measurements (time, torque, angle, gradient)
        taken during the screw operation. This method provides access to these
        measurements by name.

        Args:
            measurement_name: Name of the measurement type to retrieve.
                Must be one of the constants defined in JsonFields.Measurements:
                - TIME: Time values in 0.0012s increments
                - TORQUE: Torque measurements
                - ANGLE: Angle measurements (0.25° amplitude)
                - GRADIENT: Gradient measurements

        Returns:
            List of float values for the requested measurement type

        Raises:
            ValueError: If measurement_name is not a valid measurement type

        Example:
            >>> step = ScrewStep(step_data, 0)
            >>> time_values = step.get_values(JsonFields.Measurements.TIME)
            >>> print(time_values[:3])  # First three time points
            [0.0, 0.0012, 0.0024]
        """
        measurement_map = {
            JsonFields.Measurements.TIME: self.time,
            JsonFields.Measurements.TORQUE: self.torque,
            JsonFields.Measurements.ANGLE: self.angle,
            JsonFields.Measurements.GRADIENT: self.gradient,
        }
        if measurement_name not in measurement_map:
            valid_names = list(measurement_map.keys())
            raise ValueError(
                f"Invalid measurement name: {measurement_name}. "
                f"Must be one of: {valid_names}"
            )

        return measurement_map[measurement_name]

    def __len__(self) -> int:
        """Return the number of measurement points in this step."""
        return len(self.time)

    def __repr__(self) -> str:
        """Return a string representation of the step."""
        return f"ScrewStep(number={self.step_number}, type={self.step_type!r}, result={self.result!r})"


class ScrewRun:
    """
    Represents a complete screw operation run containing multiple steps.

    A screw run represents one complete screw operation, which typically consists
    of multiple steps. It combines data from two sources:
    1. JSON file: Contains the actual measurements and step data
    2. CSV file: Contains metadata and classification information

    Args:
        json_data: Dictionary containing run data from JSON file
        label_data: Dictionary containing label information from CSV using CsvFields format

    Attributes:
        id: Unique run identifier from CSV data
        date: Date when the run was performed
        workpiece_id: Data matrix code identifying the workpiece
        program_result: Result from the screw program ("OK" or "NOK")
        class_label: Scenario-specific classification label
        workpiece_usage: Number of times this workpiece has been used
        workpiece_location: Screw position in workpiece (0 or 1)
        steps: List of ScrewStep objects representing each step in the run

    Raises:
        ValueError: If there's a mismatch between JSON and CSV data,
                   or if required fields are missing

    Example:
        >>> json_data = {
        ...     "date": "2024-02-11",
        ...     "id code": "DMC123",
        ...     "result": "OK",
        ...     "tightening steps": [
        ...         {
        ...             "cycle": "1",
        ...             "name": "Step 1",
        ...             "step type": "standard",
        ...             "result": "OK",
        ...             "graph": {...}
        ...         }
        ...     ]
        ... }
        >>> label_data = {
        ...     'id': 'run1',
        ...     'workpiece_id': 'DMC123',
        ...     'result_value': 'OK',
        ...     'workpiece_usage': 1,
        ...     'workpiece_location': 0,
        ...     'class_value': 0
        ... }
        >>> run = ScrewRun(json_data, label_data)
    """

    def __init__(self, json_data: Dict[str, Any], label_data: Dict[str, Any]):
        try:
            # Set ID from label data
            self.id = str(label_data[CsvFields.RUN_ID])

            # Set attributes from JSON data
            self.date = str(json_data[JsonFields.Run.DATE])
            self.workpiece_id = str(json_data[JsonFields.Run.WORKPIECE_ID])
            self.program_result = str(json_data[JsonFields.Run.RESULT_VALUE])

            # Set attributes from CSV label data
            self.class_label = int(label_data[CsvFields.CLASS_VALUE])
            self.workpiece_usage = int(label_data[CsvFields.WORKPIECE_USAGE])
            self.workpiece_location = int(label_data[CsvFields.WORKPIECE_LOCATION])

            # Cross-validate data from both sources
            if self.workpiece_id != label_data[CsvFields.WORKPIECE_ID]:
                raise ValueError(
                    f"Workpiece ID mismatch: "
                    f"JSON={self.workpiece_id}, "
                    f"CSV={label_data[CsvFields.WORKPIECE_ID]}"
                )

            if self.program_result != label_data[CsvFields.RESULT_VALUE]:
                raise ValueError(
                    f"Result mismatch: "
                    f"JSON={self.program_result}, "
                    f"CSV={label_data[CsvFields.RESULT_VALUE]}"
                )

            # Create steps from tightening steps data
            steps_data = json_data[JsonFields.Run.STEPS]
            self.steps = [ScrewStep(step, idx) for idx, step in enumerate(steps_data)]

        except KeyError as e:
            raise ValueError(f"Required field missing in run data: {str(e)}")

    def get_values(self, measurement_name: str) -> List[float]:
        """
        Get all values for a measurement type across all steps in the run.

        This method concatenates the measurements from all steps into a single
        sequence, maintaining the temporal order of the steps.

        Args:
            measurement_name: Name of the measurement type to retrieve.
                Must be one of the constants defined in JsonFields.Measurements:
                - TIME: Time values in 0.0012s increments
                - TORQUE: Torque measurements
                - ANGLE: Angle measurements (0.25° amplitude)
                - GRADIENT: Gradient measurements

        Returns:
            List of all values for the specified measurement type across all steps

        Raises:
            ValueError: If measurement_name is not a valid measurement type

        Example:
            >>> run = ScrewRun("run1", json_data, label_data)
            >>> torque_values = run.get_values(JsonFields.Measurements.TORQUE)
            >>> print(f"Total torque measurements: {len(torque_values)}")
        """
        all_values = []
        for step in self.steps:
            step_values = step.get_values(measurement_name)
            all_values.extend(step_values)
        return all_values

    def __len__(self) -> int:
        """Return the total number of measurement points across all steps."""
        return sum(len(step) for step in self.steps)

    def __repr__(self) -> str:
        """Return a string representation of the run."""
        return (
            f"ScrewRun(id={self.id!r}, "
            f"result={self.program_result!r}, "
            f"steps={len(self.steps)})"
        )


class ScrewDataset:
    """
    Collection of screw runs loaded from specified files.

    This class serves as the main interface for the data processing pipeline,
    handling data loading, filtering, and access to screw operation data.
    It manages both JSON measurement data and CSV label data, providing
    a unified interface to access and filter screw operations.

    Args:
        data_path: Path to directory containing data files
        scenario_classes: Optional list of class labels to include
        screw_cycles: Optional list of workpiece usage counts to include
        screw_positions: Optional specific workpiece location to filter by

    Attributes:
        data_path: Path to data directory
        json_path: Path to JSON files directory
        scenario_classes: Active class label filters
        screw_cycles: Active workpiece usage filters
        screw_positions: Active position filters
        labels_df: DataFrame containing label data
        file_names: List of filtered file names
        screw_runs: List of loaded ScrewRun objects
        processed_data: Dict for pipeline transformer results

    Example:
        >>> dataset = ScrewDataset(
        ...     data_path="data/",
        ...     scenario_classes=[0, 1],
        ...     screw_cycles=[1, 2],
        ...     screw_positions="left"
        ... )
        >>> print(len(dataset))  # Number of runs matching filters
        >>> for run in dataset:  # Iterate through matching runs
        ...     print(run.program_result)

    Raises:
        FileNotFoundError: If required files are not found
        ValueError: If filter parameters are invalid
    """

    POSITION_MAP: Dict[str, Optional[int]] = {
        "left": 0,
        "right": 1,
        "both": None,
    }

    VALID_MEASUREMENTS: Set[str] = {
        JsonFields.Measurements.TIME,
        JsonFields.Measurements.TORQUE,
        JsonFields.Measurements.ANGLE,
        JsonFields.Measurements.GRADIENT,
    }

    def __init__(
        self,
        data_path: Union[str, Path],
        scenario_classes: Optional[List[int]] = None,
        screw_cycles: Optional[List[int]] = None,
        screw_positions: Optional[str] = None,
    ) -> None:
        # Initialize paths and validate
        self.data_path = Path(data_path)
        self.json_path = self.data_path / "json"
        if not self.json_path.exists():
            raise FileNotFoundError(f"JSON directory not found: {self.json_path}")

        # Store filter parameters
        self.scenario_classes = scenario_classes
        self.screw_cycles = screw_cycles
        self.screw_positions = screw_positions

        # Will be populated by pipeline transformer
        self.processed_data: Dict[str, List[List[float]]] = {}

        # Load data
        self.labels_df = self._load_labels()
        self.file_names = self._filter_labels()
        self.screw_runs = self._load_runs()

    @classmethod
    def from_config(
        cls, data_path: Union[str, Path], config: ConfigSchema
    ) -> "ScrewDataset":
        """
        Create a dataset instance from a configuration object.

        This factory method simplifies dataset creation when using configuration files.

        Args:
            data_path: Path to data directory
            config: Configuration object containing filter parameters

        Returns:
            New ScrewDataset instance configured according to config object
        """
        return cls(
            data_path=data_path,
            scenario_classes=config.scenario_classes,
            screw_cycles=config.screw_cycles,
            screw_positions=config.screw_positions,
        )

    def _load_labels(self) -> pd.DataFrame:
        """
        Load and prepare the labels CSV file.

        The CSV file contains metadata about each screw run, including workpiece
        information, classification labels, and result values.

        Returns:
            DataFrame containing label data indexed by filename

        Raises:
            FileNotFoundError: If labels file is not found
        """
        labels_path = self.data_path / "labels.csv"
        if not labels_path.exists():
            raise FileNotFoundError(f"Labels file not found: {labels_path}")

        df = pd.read_csv(
            labels_path,
            dtype={
                CsvFields.RUN_ID: int,
                CsvFields.FILE_NAME: str,
                CsvFields.CLASS_VALUE: int,
                CsvFields.RESULT_VALUE: str,
                CsvFields.WORKPIECE_ID: str,
                CsvFields.WORKPIECE_USAGE: int,
                CsvFields.WORKPIECE_LOCATION: int,
            },
        )
        return df.set_index(CsvFields.FILE_NAME)

    def _filter_labels(self) -> List[str]:
        """
        Apply filtering criteria to the labels dataset and return matching file names.

        This method filters the labels DataFrame based on:
        - Scenario classes (classification categories)
        - Workpiece usage counts (how many times each piece was used)
        - Workpiece positions (left=0, right=1, or both)

        If a filter parameter is None, all values for that criterion are included.

        Returns:
            List of file names that match all specified filtering criteria

        Raises:
            ValueError: If an invalid position is specified
        """
        df = self.labels_df

        # Get full ranges if filters are None
        scenario_classes = (
            self.scenario_classes or df[CsvFields.CLASS_VALUE].unique().tolist()
        )
        screw_cycles = (
            self.screw_cycles or df[CsvFields.WORKPIECE_USAGE].unique().tolist()
        )

        # Apply filters
        mask = df[CsvFields.CLASS_VALUE].isin(scenario_classes) & df[
            CsvFields.WORKPIECE_USAGE
        ].isin(screw_cycles)

        # Handle position filtering
        if self.screw_positions is not None:
            if self.screw_positions not in self.POSITION_MAP:
                raise ValueError(
                    f"Invalid position value: {self.screw_positions}. "
                    f"Must be one of: {list(self.POSITION_MAP.keys())}"
                )

            if self.screw_positions != "both":
                mask &= (
                    df[CsvFields.WORKPIECE_LOCATION]
                    == self.POSITION_MAP[self.screw_positions]
                )

        filtered_files = df[mask].index.tolist()
        logger.info(f"Selected {len(filtered_files)} files")
        return filtered_files

    def _load_runs(self) -> List[ScrewRun]:
        """
        Load and instantiate ScrewRun objects from filtered JSON files.

        This method:
        1. Iterates through filtered file names
        2. Determines the correct class subdirectory for each file
        3. Loads JSON measurement data from the appropriate subdirectory
        4. Creates corresponding label data dictionary
        5. Instantiates ScrewRun objects

        The JSON directory structure is:
        json/
        ├── 0/         # Class 0 measurements
        ├── 1/         # Class 1 measurements
        └── n/         # Class n measurements

        Returns:
            List of ScrewRun objects representing the loaded runs

        Raises:
            FileNotFoundError: If a JSON file is missing
            ValueError: If JSON parsing fails or data is invalid
        """
        runs = []

        for file_name in self.file_names:
            # Get the class value for this file from the labels DataFrame
            class_value = str(self.labels_df.loc[file_name, CsvFields.CLASS_VALUE])

            # Construct path including class subdirectory
            json_file = self.json_path / class_value / file_name

            if not json_file.exists():
                raise FileNotFoundError(
                    f"File not found: {json_file}\n"
                    f"Expected file in class directory: {class_value}"
                )

            try:
                # Load JSON data
                with open(json_file, "r") as f:
                    try:
                        json_data = json.load(f)
                    except JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON in {file_name}: {str(e)}")

                # Create label data dictionary from DataFrame row
                row = self.labels_df.loc[file_name]
                label_data = {
                    CsvFields.RUN_ID: row[CsvFields.RUN_ID],
                    CsvFields.FILE_NAME: file_name,
                    CsvFields.CLASS_VALUE: row[CsvFields.CLASS_VALUE],
                    CsvFields.RESULT_VALUE: row[CsvFields.RESULT_VALUE],
                    CsvFields.WORKPIECE_ID: row[CsvFields.WORKPIECE_ID],
                    CsvFields.WORKPIECE_USAGE: row[CsvFields.WORKPIECE_USAGE],
                    CsvFields.WORKPIECE_LOCATION: row[CsvFields.WORKPIECE_LOCATION],
                }

                # Create ScrewRun instance using both data sources
                runs.append(ScrewRun(json_data, label_data))

            except Exception as e:
                raise ValueError(f"Error loading {file_name}: {str(e)}")

        logger.info(f"Successfully loaded {len(runs)} screw runs")
        return runs

    def get_values(self, measurement_name: str) -> List[List[float]]:
        """
        Retrieve measurement values for all runs across the dataset.

        Args:
            measurement_name: Name of the measurement to retrieve.
                Must be one of:
                - TIME: Time values in 0.0012s increments
                - TORQUE: Torque measurements
                - ANGLE: Angle measurements (0.25° amplitude)
                - GRADIENT: Gradient measurements

        Returns:
            List of measurement lists, one per run

        Raises:
            ValueError: If measurement_name is not valid
        """
        if measurement_name not in self.VALID_MEASUREMENTS:
            raise ValueError(
                f"Invalid measurement name: {measurement_name}. "
                f"Must be one of: {self.VALID_MEASUREMENTS}"
            )
        return [run.get_values(measurement_name) for run in self.screw_runs]

    def __len__(self) -> int:
        """Return the number of screw runs in the dataset."""
        return len(self.screw_runs)

    def __iter__(self) -> Iterator[ScrewRun]:
        """Create an iterator over the screw runs in the dataset."""
        return iter(self.screw_runs)

    def __repr__(self) -> str:
        """Provide a string representation of the dataset."""
        return f"ScrewDataset(runs={len(self)})"
