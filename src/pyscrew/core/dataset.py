"""
ScrewDataset class for managing and accessing screw operation data.

This module defines the ScrewDataset class, which serves as the main interface for
loading, filtering, and accessing screw operation data from both JSON measurement
files and CSV label files.
"""

import json
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set, Union

import pandas as pd

from pyscrew.config import PipelineConfig
from pyscrew.utils.logger import get_logger

from .fields import CsvFields, JsonFields
from .run import ScrewRun

logger = get_logger(__name__)


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
        screw_positions: Optional specific workpiece location to filter by ("left", "right", or "both")

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
        ...     scenario_classes=["001_control-group", "002_faulty-condition"],
        ...     screw_cycles=[1, 2],
        ...     screw_positions="left"
        ... )
        >>> print(len(dataset))  # Number of runs matching filters
        >>> for run in dataset:  # Iterate through matching runs
        ...     print(run.workpiece_result)

    Raises:
        FileNotFoundError: If required files are not found
        ValueError: If filter parameters are invalid
    """

    VALID_MEASUREMENTS: Set[str] = {
        JsonFields.Measurements.TIME,
        JsonFields.Measurements.TORQUE,
        JsonFields.Measurements.ANGLE,
        JsonFields.Measurements.GRADIENT,
    }

    def __init__(
        self,
        data_path: Union[str, Path],
        scenario_classes: Optional[List[str]] = None,
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
    def from_config(cls, config: PipelineConfig) -> "ScrewDataset":
        """
        Create a dataset instance from a configuration object.

        This factory method simplifies dataset creation when using configuration files.

        Args:
            config: Configuration object containing filter parameters and data path

        Returns:
            New ScrewDataset instance configured according to config object
        """
        return cls(
            data_path=config.get_data_path(),
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
                CsvFields.CLASS_VALUE: str,
                CsvFields.WORKPIECE_ID: str,
                CsvFields.WORKPIECE_DATE: str,
                CsvFields.WORKPIECE_USAGE: int,
                CsvFields.WORKPIECE_RESULT: str,
                CsvFields.WORKPIECE_LOCATION: str,
                CsvFields.SCENARIO_CONDITION: str,
                CsvFields.SCENARIO_EXCEPTION: int,
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
            valid_positions = ["left", "right", "both"]
            if self.screw_positions not in valid_positions:
                raise ValueError(
                    f"Invalid position value: {self.screw_positions}. "
                    f"Must be one of: {valid_positions}"
                )

            if self.screw_positions != "both":
                mask &= df[CsvFields.WORKPIECE_LOCATION] == self.screw_positions

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
        ├── 001_control-group/    # Control group measurements
        ├── 002_faulty-condition/ # Faulty condition measurements
        └── other_class_names/    # Other scenario classes

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
                    CsvFields.WORKPIECE_ID: row[CsvFields.WORKPIECE_ID],
                    CsvFields.WORKPIECE_DATE: row[CsvFields.WORKPIECE_DATE],
                    CsvFields.WORKPIECE_USAGE: row[CsvFields.WORKPIECE_USAGE],
                    CsvFields.WORKPIECE_RESULT: row[CsvFields.WORKPIECE_RESULT],
                    CsvFields.WORKPIECE_LOCATION: row[CsvFields.WORKPIECE_LOCATION],
                    CsvFields.SCENARIO_CONDITION: row[CsvFields.SCENARIO_CONDITION],
                    CsvFields.SCENARIO_EXCEPTION: row[CsvFields.SCENARIO_EXCEPTION],
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
