import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

import numpy as np

# Reminder: The data structure is as follows

# ScrewDataset
# └── List[ScrewRun]
#    └── List[ScrewStep]
#        └── Dict[str, np.ndarray]  # measurements


@dataclass
class Measurements:
    """Measurement identifiers."""

    TIME: str = "time values"
    TORQUE: str = "torque values"
    ANGLE: str = "angle values"
    GRADIENT: str = "gradient values"


@dataclass
class RunFields:
    """Run metadata field identifiers."""

    DATE: str = "date"
    RESULT: str = "result"
    DMC_CODE: str = "dmc_code"
    STEPS: str = "tightening steps"


@dataclass
class StepFields:
    """Step metadata field identifiers."""

    NAME: str = "name"
    TYPE: str = "step type"
    RESULT: str = "result"
    QUALITY: str = "quality code"
    GRAPH: str = "graph"


# Initialize constant instances
MEASUREMENTS = Measurements()
RUN_FIELDS = RunFields()
STEP_FIELDS = StepFields()


class ScrewStep:
    """Represents a single step in a screw run."""

    def __init__(self, step_data: Dict[str, Any], step_number: int):
        # Step metadata
        self.step_number = step_number
        self.name = step_data.get(STEP_FIELDS.NAME, "")
        self.step_type = step_data.get(STEP_FIELDS.TYPE, "")
        self.result = step_data.get(STEP_FIELDS.RESULT, "")
        self.quality_code = step_data.get(STEP_FIELDS.QUALITY, "")

        # Get measurement data from graph
        graph_data: dict = step_data.get(STEP_FIELDS.GRAPH, {})
        self.time = np.array(graph_data.get(MEASUREMENTS.TIME, []))
        self.torque = np.array(graph_data.get(MEASUREMENTS.TORQUE, []))
        self.angle = np.array(graph_data.get(MEASUREMENTS.ANGLE, []))
        self.gradient = np.array(graph_data.get(MEASUREMENTS.GRADIENT, []))

    def get_values(self, measurement_name: str) -> List[float]:
        """Get values for a specific measurement."""
        measurement_map = {
            MEASUREMENTS.TIME: self.time,
            MEASUREMENTS.TORQUE: self.torque,
            MEASUREMENTS.ANGLE: self.angle,
            MEASUREMENTS.GRADIENT: self.gradient,
        }
        if measurement_name not in measurement_map:
            raise ValueError(f"Invalid measurement name: {measurement_name}")
        return measurement_map[measurement_name].tolist()

    def __len__(self) -> int:
        return len(self.time)

    def __repr__(self) -> str:
        return f"ScrewStep(number={self.step_number}, type={self.step_type!r}, result={self.result!r})"


class ScrewRun:
    """
    Represents a complete screw run containing multiple steps.
    """

    def __init__(self, run_id: str, json_path: Path):
        self.id = run_id

        # Load data from JSON
        with open(json_path, "r") as f:
            data: dict = json.load(f)

        # Set basic attributes
        self.date = str(data.get(RUN_FIELDS.DATE))
        self.result = str(data.get(RUN_FIELDS.RESULT))
        self.dmc_code = str(data.get(RUN_FIELDS.DMC_CODE))

        # Create steps from tightening steps data
        self.steps = [
            ScrewStep(step, idx)
            for idx, step in enumerate(data.get(RUN_FIELDS.STEPS, []))
        ]

    def get_values(self, measurement_name: str) -> List[float]:
        """Get all values for a measurement across all steps.

        Args:
            measurement_name: Name of the measurement to get

        Returns:
            List of values concatenated from all steps
        """
        all_values = []
        for step in self.steps:
            all_values.extend(step.get_values(measurement_name))
        return all_values

    def __len__(self) -> int:
        return sum(len(step) for step in self.steps)

    def __repr__(self) -> str:
        return (
            f"ScrewRun(id={self.id!r}, result={self.result!r}, steps={len(self.steps)})"
        )


class ScrewDataset:
    """
    Collection of screw runs loaded from specified files.
    Main interface for data processing pipeline.
    """

    def __init__(self, data_path: Union[str, Path], file_names: List[str]):
        """
        Initialize dataset with path to data directory and list of files to load.

        Args:
            data_path: Path to directory containing JSON files
            file_names: List of JSON file names to load from the directory
        """
        self.data_path = Path(data_path)
        self.file_names = file_names
        self.screw_runs: List[ScrewRun] = []
        self._load_runs()

    def get_values(self, measurement_name: str) -> List[List[float]]:
        """Get measurement values for all runs.

        Args:
            measurement_name: Name of the measurement to get

        Returns:
            List of value lists, one per run
        """
        return [run.get_values(measurement_name) for run in self.screw_runs]

    def _load_runs(self) -> None:
        """Load specified runs from JSON files."""
        for file_name in self.file_names:
            json_path = self.data_path / file_name
            if not json_path.exists():
                raise FileNotFoundError(f"File not found: {json_path}")
            try:
                run_id = json_path.stem  # "Ch_0000012345678"
                self.screw_runs.append(ScrewRun(run_id, json_path))
            except Exception as e:
                raise ValueError(f"Error loading {file_name}: {str(e)}")

    def __len__(self) -> int:
        return len(self.screw_runs)

    def __iter__(self):
        return iter(self.screw_runs)

    def __repr__(self) -> str:
        return f"ScrewDataset(runs={len(self)})"
