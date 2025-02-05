import json
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Union

import numpy as np
import pandas as pd

from pyscrew.utils.config_schema import ConfigSchema
from pyscrew.utils.logger import get_logger


@dataclass
class RunFields:
    """
    Constants for run-level metadata fields in screw operation data.

    These fields describe the overall properties of a complete screw operation run.

    Attributes:
        DATE: Date when the run was performed
        RESULT: Overall result of the run as per the screw driving control (does not equal the class label)
        DMC: Machine-defined identification code for each workpiece
        STEPS: Collection of tightening steps in the run (list of dictionaries)

    Note:
        There are several more fields in the JSON files, but these are the most relevant ones.
    """

    DATE: str = "date"
    RESULT: str = "result"
    DMC: str = "id code"  # Name pre-defined by screw driving control
    STEPS: str = "tightening steps"


@dataclass
class StepFields:
    """
    Constants for step-level metadata fields in screw operation data.

    These fields describe individual steps within a screw operation run.

    Attributes:
        NAME: Name identifier for the step as set in the screw driving control
        TYPE: Type classification of the step (simply "standard")
        RESULT: Result status of the step (e.g., "OK", "NOK")
        QUALITY: Quality assessment code
        GRAPH: Measurement data for the step (dict with measurement identifiers as keys)
            See Measurements for the specific identifiers
    """

    NAME: str = "name"
    TYPE: str = "step type"
    RESULT: str = "result"
    QUALITY: str = "quality code"
    GRAPH: str = "graph"


@dataclass
class Measurements:
    """
    Constants for measurement identifiers in screw operation data.

    These identifiers are used consistently throughout the codebase to refer to
    the four different types of measurements collected during screw operations.

    Attributes:
        TIME: Identifier for time measurements (mostly in 0.0012 increments)
        TORQUE: Identifier for torque measurements
        ANGLE: Identifier for angle measurements (inconsistent distance, 0.25° amplitude)
        GRADIENT: Identifier for gradient measurements

    Note:
        `"angleRed values"`` and `torqueRed values` are recorded but always [0,...,0].
        They are not used in the processing pipline and not returned as measurements.
    """

    TIME: str = "time values"
    TORQUE: str = "torque values"
    ANGLE: str = "angle values"
    GRADIENT: str = "gradient values"


@dataclass
class LabelFields:
    """
    Constants for fields in the label file (csv) that provides metadata about runs.

    These fields connect raw measurement data with classification and identification info.

    Attributes:
        FILE_NAME: Name of the data file
        DMC: Data matrix code for identification
        RESULT: Result classification
        CYCLE: Cycle number in sequence
        POSITION: Physical location of workpiece
        CLASS: Classification label
    """

    FILE_NAME: str = "file_name"
    DMC: str = "data_matrix_code"
    RESULT: str = "result_value"
    CYCLE: str = "cycle_number"
    POSITION: str = "workpiece_location"
    CLASS: str = "class_label"


@dataclass
class RunMetadata:
    """
    Container for metadata about a screw run from label information.

    This class consolidates label data that describes properties of a complete run.

    Attributes:
        data_matrix_code: Unique identifier code
        result: Result classification
        cycle: Sequential cycle number
        position: Physical location identifier
        class_label: Classification category

    Note:
        With the next file upload, this class should become outdated and will be substituted by the label fileds.
    """

    data_matrix_code: str
    result: str
    cycle: int
    position: int
    class_label: int


# Initialize constant instances
MEASUREMENTS = Measurements()
RUN_FIELDS = RunFields()
STEP_FIELDS = StepFields()
LABEL_FIELDS = LabelFields()

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
        step_number: Position in sequence of steps (0-indexed)
        name: Identifier name of the step
        step_type: Classification of step type
        result: Result status
        quality_code: Quality assessment code
        time: Array of time measurements
        torque: Array of torque measurements
        angle: Array of angle measurements
        gradient: Array of gradient measurements

    Example:
        >>> step_data = {
        ...     "name": "Step 1",
        ...     "step type": "tightening",
        ...     "result": "OK",
        ...     "graph": {
        ...         "time values": [0.1, 0.2, 0.3],
        ...         "torque values": [1.0, 1.5, 2.0]
        ...     }
        ... }
        >>> step = ScrewStep(step_data, step_number=0)
        >>> print(step.name)
        'Step 1'
        >>> print(len(step))
        3

    Raises:
        KeyError: If any required fields are missing in the step data

    """

    def __init__(self, step_data: Dict[str, Any], step_number: int):
        try:
            # Step metadata
            self.step_number = step_number
            self.name = step_data.get(STEP_FIELDS.NAME)
            self.step_type = step_data.get(STEP_FIELDS.TYPE)
            self.result = step_data.get(STEP_FIELDS.RESULT)
            self.quality_code = step_data.get(STEP_FIELDS.QUALITY)

            # Get measurement data from graph
            graph_data: dict = step_data.get(STEP_FIELDS.GRAPH)
            self.time = np.array(graph_data.get(MEASUREMENTS.TIME))
            self.torque = np.array(graph_data.get(MEASUREMENTS.TORQUE))
            self.angle = np.array(graph_data.get(MEASUREMENTS.ANGLE))
            self.gradient = np.array(graph_data.get(MEASUREMENTS.GRADIENT))

        except KeyError as e:
            raise ValueError(f"Error loading step data: {str(e)}")

    def get_values(self, measurement_name: str) -> List[float]:
        """
        Retrieve values for a specific measurement type.

        Args:
            measurement_name: Name of the measurement type to retrieve
                            (must be one of the MEASUREMENTS constants)

        Returns:
            List of measurement values for the specified type

        Raises:
            ValueError: If measurement_name is not a valid measurement type
        """
        measurement_map = {
            MEASUREMENTS.TIME: self.time,
            MEASUREMENTS.TORQUE: self.torque,
            MEASUREMENTS.ANGLE: self.angle,
            MEASUREMENTS.GRADIENT: self.gradient,
        }
        if measurement_name not in measurement_map:  # Should be impossible
            raise ValueError(f"Invalid measurement name: {measurement_name}")

        return measurement_map[measurement_name].tolist()

    def __len__(self) -> int:
        """Return the number of measurement points in this step."""
        return len(self.time)

    def __repr__(self) -> str:
        """Return a string representation of the step."""
        return f"ScrewStep(number={self.step_number}, type={self.step_type!r}, result={self.result!r})"


class ScrewRun:
    """
    Represents a complete screw operation run containing multiple steps.

    This class manages the full lifecycle of a screw operation, including both
    the screw step data from the individual json files (as a sequence of individual
    steps) as well as the label or metadata from the csv label file (as attributes).

    Args:
        run_id: Unique identifier for this run
        json_data: Dictionary containing run data from JSON file
        label_data: RunMetadata object containing label information

    Attributes:
        id: Unique run identifier
        date: Date of the run
        dmc: Data matrix code
        result: Result classification
        screw_cycle: Cycle number
        screw_position: Position identifier
        class_label: Classification label
        steps: List of ScrewStep objects for this run

    Example:
        >>> json_data = {
        ...     "date": "2024-02-05",
        ...     "id code": "DMC123",
        ...     "result": "OK",
        ...     "tightening steps": [
        ...         {"name": "Step 1", "result": "OK"}
        ...     ]
        ... }
        >>> label_data = RunMetadata(
        ...     data_matrix_code="DMC123",
        ...     result="OK",
        ...     cycle=1,
        ...     position=0,
        ...     class_label=0
        ... )
        >>> run = ScrewRun("run1", json_data, label_data)
        >>> print(run.result)
        'OK'
    """

    def __init__(self, run_id: str, json_data: Dict[str, Any], label_data: RunMetadata):
        self.id = run_id

        # Set basic attributes from JSON
        self.date = str(json_data.get(RUN_FIELDS.DATE))
        self.dmc = str(json_data.get(RUN_FIELDS.DMC))
        self.result = str(json_data.get(RUN_FIELDS.RESULT))

        # Set attributes from label data
        self.screw_cycle = label_data.cycle
        self.screw_position = label_data.position
        self.class_label = label_data.class_label

        # Sanity checks for overlapping data
        assert (
            self.dmc == label_data.data_matrix_code
        ), f"DMC mismatch: JSON={self.dmc}, label={label_data.data_matrix_code}"
        assert (
            self.result == label_data.result
        ), f"Result mismatch: JSON={self.result}, label={label_data.result}"

        # Create steps from tightening steps data
        self.steps = [
            ScrewStep(step, idx)
            for idx, step in enumerate(json_data.get(RUN_FIELDS.STEPS, []))
        ]

    def get_values(self, measurement_name: str) -> List[float]:
        """
        Get all values for a measurement type across all steps in the run.

        This method concatenates measurements from all steps into a single sequence.

        Args:
            measurement_name: Name of the measurement type to retrieve
                            (must be one of the MEASUREMENTS constants)

        Returns:
            List of all values for the specified measurement type across all steps
        """
        # TODO: Use both .extend() and .append() to concatenate lists according to parameter
        all_values = []
        for step in self.steps:
            all_values.extend(step.get_values(measurement_name))
        return all_values

    def __len__(self) -> int:
        """Return the total number of measurement points across all steps."""
        return sum(len(step) for step in self.steps)

    def __repr__(self) -> str:
        """Return a string representation of the run."""
        return (
            f"ScrewRun(id={self.id!r}, result={self.result!r}, steps={len(self.steps)})"
        )


class ScrewDataset:
    """
    Collection of screw runs loaded from specified files.

    This class serves as the main interface for the data processing pipeline,
    handling data loading, filtering, and access to screw operation data.

    Args:
        data_path: Path to directory containing data files
        scenario_classes: Optional list of class labels to include
        screw_cycles: Optional list of cycle numbers to include
        screw_positions: Optional specific workpiece location to filter by

    Attributes:
        data_path: Path to data directory
        json_path: Path to JSON files directory
        scenario_classes: Active class label filters
        screw_cycles: Active cycle number filters
        screw_positions: Active position filters
        labels_df: DataFrame containing label data
        file_names: List of filtered file names
        screw_runs: List of loaded ScrewRun objects
        processed_data: List for pipeline transformer results

    Example:
        >>> dataset = ScrewDataset(
        ...     data_path="data/",
        ...     scenario_classes=[0, 1],
        ...     screw_cycles=[1, 2],
        ...     screw_positions="left"
        ... )
        >>> print(len(dataset))  # Number of runs matching filters
        >>> for run in dataset:  # Iterate through matching runs
        ...     print(run.result)

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
        MEASUREMENTS.TIME,
        MEASUREMENTS.TORQUE,
        MEASUREMENTS.ANGLE,
        MEASUREMENTS.GRADIENT,
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
        self.processed_data: List[Any] = []

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
                LABEL_FIELDS.FILE_NAME: str,
                LABEL_FIELDS.DMC: str,
                LABEL_FIELDS.RESULT: str,
                LABEL_FIELDS.CYCLE: int,
                LABEL_FIELDS.POSITION: int,
                LABEL_FIELDS.CLASS: int,
            },
        )
        return df.set_index(LABEL_FIELDS.FILE_NAME)

    def _filter_labels(self) -> List[str]:
        """
        Apply filtering criteria to the labels dataset and return matching file names.

        This internal method filters the labels DataFrame based on:
        - Scenario classes (e.g., 0, 1 for different classification categories)
        - Screw cycles (sequential run numbers)
        - Workpiece positions (left, right, or both)

        The method uses the filter parameters set during dataset initialization:
        - If no scenario_classes are specified, uses all unique classes
        - If no screw_cycles are specified, uses all unique cycles
        - Position filtering can be 'left', 'right', or 'both'

        Returns:
            List of file names that match all specified filtering criteria

        Raises:
            ValueError: If an invalid position is specified

        Note:
            - Logs the number of files selected after filtering
            - Uses boolean masking to efficiently filter the DataFrame
        """
        df = self.labels_df

        # Get full ranges if filters are None using or operator
        scenario_classes = (
            self.scenario_classes or df[LABEL_FIELDS.CLASS].unique().tolist()
        )
        screw_cycles = self.screw_cycles or df[LABEL_FIELDS.CYCLE].unique().tolist()

        # Apply filters
        mask = df[LABEL_FIELDS.CLASS].isin(scenario_classes) & df[
            LABEL_FIELDS.CYCLE
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
                    df[LABEL_FIELDS.POSITION] == self.POSITION_MAP[self.screw_positions]
                )

        filtered_files = df[mask].index.tolist()
        logger.info(f"Selected {len(filtered_files)} files")
        return filtered_files

    def _get_run_label_data(self, file_name: str) -> RunMetadata:
        """
        Extract metadata for a specific run from the labels DataFrame.

        This internal method retrieves the label information for a given file name,
        creating a RunMetadata object with key identifying and classification attributes.

        Args:
            file_name: Name of the JSON file corresponding to a screw run

        Returns:
            RunMetadata object containing:
            - data_matrix_code: Unique identifier for the workpiece
            - result: Operational result of the run
            - cycle: Sequential cycle number
            - position: Physical location of the workpiece
            - class_label: Classification category

        Raises:
            KeyError: If the file name is not found in the labels DataFrame

        Note:
            This method is typically called during run loading to associate
            metadata with the corresponding JSON file data.
        """
        row = self.labels_df.loc[file_name]

        return RunMetadata(
            data_matrix_code=row[LABEL_FIELDS.DMC],
            result=row[LABEL_FIELDS.RESULT],
            cycle=row[LABEL_FIELDS.CYCLE],
            position=row[LABEL_FIELDS.POSITION],
            class_label=row[LABEL_FIELDS.CLASS],
        )

    def _load_runs(self) -> List[ScrewRun]:
        """
        Load and instantiate ScrewRun objects from filtered JSON files.

        This internal method performs the following key operations:
        - Iterates through filtered file names
        - Reads and parses JSON files
        - Retrieves corresponding label data
        - Creates ScrewRun instances for each valid file

        Returns:
            List of ScrewRun objects representing the loaded and filtered runs

        Raises:
            FileNotFoundError: If a JSON file is missing
            ValueError: If:
                - JSON file cannot be parsed
                - There are unexpected errors during file loading
                - JSON data is invalid

        Note:
            - Handles JSON decoding errors specifically
            - Provides detailed error messaging for debugging
            - Uses file stem as run_id for identification
        """

        runs = []

        for file_name in self.file_names:
            json_file = self.json_path / file_name
            if not json_file.exists():
                raise FileNotFoundError(f"File not found: {json_file}")

            try:
                with open(json_file, "r") as f:
                    try:
                        # Specific JSON parsing error handling
                        json_data = json.load(f)
                    except JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON in {file_name}: {str(e)}")

                run_id = json_file.stem
                label_data = self._get_run_label_data(file_name)
                runs.append(ScrewRun(run_id, json_data, label_data))
            except Exception as e:
                # Catch any other unexpected errors
                raise ValueError(f"Error loading {file_name}: {str(e)}")
        return runs

    def get_values(self, measurement_name: str) -> List[List[float]]:
        """
        Retrieve measurement values for all runs across the dataset.

        This method collects specified measurement values from each run in the dataset,
        returning a list of lists where each inner list represents the measurements
        for a single run.

            Args:
                measurement_name: Name of the measurement to get

            Returns:
                List of value lists, one per run

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
        """Provide a string representation of the ScrewDataset."""
        return f"ScrewDataset(runs={len(self)})"
