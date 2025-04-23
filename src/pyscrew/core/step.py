"""
ScrewStep class for representing an individual step in a screw operation.

This module defines the ScrewStep class which represents a single step in
a multi-step screw operation. Each step contains measurement data (time,
torque, angle, gradient) and metadata describing the step's properties.
"""

from typing import Any, Dict, List

from .fields import JsonFields


class ScrewStep:
    """
    Represents a single step in a screw operation run.

    This class encapsulates all data and metadata for one step of a multi-step
    screw operation. It handles both the step's descriptive metadata and its
    measurement time series data. Usually, a four-step screw operation consists
    of four of these. In case of an error during tightening, less steps are recorded.

    Args:
        step_data: Dictionary containing step metadata and measurements
        step_number: Sequential number of this step in the run (0-indexed)

    Attributes:
        step_number: Position in sequence of steps (0-indexed)
        name: Identifier name of the step
        step_type: Classification of step type (typically "standard")
        workpiece_result: Result status ("OK" or "NOK")
        quality_code: Quality assessment code
        time: List of time measurements in 0.0012s increments
        torque: List of torque measurements
        angle: List of angle measurements (0.25° amplitude)
        gradient: List of gradient measurements

    Raises:
        ValueError: If any required fields are missing in step_data

    Example:
        >>> step_data = {
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
            self.workpiece_result = step_data[JsonFields.Step.WORKPIECE_RESULT]
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
            >>> # Assuming step_data is properly defined
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
        return f"ScrewStep(number={self.step_number}, type={self.step_type!r}, result={self.workpiece_result!r})"
