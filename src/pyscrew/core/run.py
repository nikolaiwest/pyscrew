"""
ScrewRun class for representing a complete screw operation.

This module defines the ScrewRun class which represents a complete screw operation
consisting of multiple steps. It combines data from JSON measurement files and
CSV label files into a unified representation.
"""

from typing import Any, Dict, List

from .fields import CsvFields, JsonFields
from .step import ScrewStep


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
        workpiece_result: Result from the screw program ("OK" or "NOK")
        class_value: Scenario-specific classification label
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
        ...             "name": "Step 1",
        ...             "step type": "standard",
        ...             "result": "OK",
        ...             "quality code": "A1",
        ...             "graph": {...}
        ...         }
        ...     ]
        ... }
        >>> label_data = {
        ...     'run_id': 1234,
        ...     'file_name': 'Ch_000...1234.json',
        ...     'workpiece_id': '300000...1234',
        ...     'workpiece_result': 'OK',
        ...     'workpiece_usage': 0,
        ...     'workpiece_location': "left"",
        ...     'class_value': '001_control-group'
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
            self.workpiece_result = str(json_data[JsonFields.Run.WORKPIECE_RESULT])

            # Set attributes from CSV label data
            self.class_value = str(label_data[CsvFields.CLASS_VALUE])
            self.workpiece_usage = int(label_data[CsvFields.WORKPIECE_USAGE])
            self.workpiece_location = str(label_data[CsvFields.WORKPIECE_LOCATION])

            # Cross-validate data from both sources
            if self.workpiece_id != label_data[CsvFields.WORKPIECE_ID]:
                raise ValueError(
                    f"Workpiece ID mismatch: "
                    f"JSON={self.workpiece_id}, "
                    f"CSV={label_data[CsvFields.WORKPIECE_ID]}"
                )

            if self.workpiece_result != label_data[CsvFields.WORKPIECE_RESULT]:
                raise ValueError(
                    f"Result mismatch: "
                    f"JSON={self.workpiece_result}, "
                    f"CSV={label_data[CsvFields.WORKPIECE_RESULT]}"
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
            >>> json_data = {...}  # JSON data
            >>> label_data = {...}  # Label data
            >>> run = ScrewRun(json_data, label_data)
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
            f"result={self.workpiece_result!r}, "
            f"steps={len(self.steps)})"
        )
