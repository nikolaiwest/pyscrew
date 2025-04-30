"""
Data validation module for PyScrew.

This module provides functionality for validating processed data against
expected formats, ranges, and integrity constraints before it is used in analysis.

Key features:
    - Format validation for different output formats
    - Range checking for physical measurements
    - Consistency validation across measurement collections
    - Structural validation for completeness
    - Error reporting with detailed diagnostic information
"""

from math import isfinite
from typing import Dict, List

from pyscrew.config import PipelineConfig
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Raised when data validation fails due to format, range, or integrity issues."""

    pass


def validate_data(data: Dict[str, List[float]], config: PipelineConfig) -> bool:
    """
    Validate processed data against configuration constraints.

    This function performs validation checks on processed data to ensure it meets
    the requirements for analysis. It validates:
    1. Data structure and completeness
    2. Value ranges and distributions
    3. Consistency across measurement types
    4. Format-specific requirements

    Args:
        data: Dictionary containing processed measurements
        config: Pipeline configuration with validation parameters

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails with detailed reason
    """
    logger.info(f"Validating processed data for scenario '{config.scenario_name}'")

    try:
        # Step 1: Verify data structure
        _validate_data_structure(data, config)

        # Step 2: Verify data lengths
        _validate_data_lengths(data, config)

        # Step 3: Verify physical value ranges
        _validate_value_ranges(data)

        # Step 4: Verify consistency between measurements
        _validate_measurement_consistency(data)

        # Step 5: Verify format-specific requirements
        _validate_format_requirements(data, config)

        # Log successful validation
        count = len(next(iter(data.values()))) if data else 0
        logger.info(
            f"Data validation passed: {len(data)} measurement types with {count} points each"
        )
        return True

    except Exception as e:
        if not isinstance(e, ValidationError):
            e = ValidationError(f"Data validation failed: {str(e)}")
        logger.error(str(e))
        raise e


def _validate_data_structure(
    data: Dict[str, List[float]], config: PipelineConfig
) -> None:
    """Validate data structure based on requested measurements."""
    # Determine required measurements based on config
    required_keys = []

    # If measurements is None, include all measurements
    if config.measurements is None:
        required_keys = [
            "torque values",
            "angle values",
            "gradient values",
            "time values",
        ]
    else:
        # Otherwise, include only requested measurements
        measurement_mapping = {
            "torque": "torque values",
            "angle": "angle values",
            "gradient": "gradient values",
            "time": "time values",
        }
        required_keys = [
            measurement_mapping[m]
            for m in config.measurements
            if m in measurement_mapping
        ]

    # Check for missing keys
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise ValidationError(
            f"Missing required measurements: {', '.join(missing_keys)}"
        )

    # Check for empty measurements
    empty_keys = [key for key, values in data.items() if not values]
    if empty_keys:
        raise ValidationError(f"Empty measurement collections: {', '.join(empty_keys)}")

    # Check if all values are lists
    non_list_keys = [key for key, value in data.items() if not isinstance(value, list)]
    if non_list_keys:
        raise ValidationError(
            f"Non-list type for measurements: {', '.join(non_list_keys)}"
        )

    # Check if all elements in lists of lists are numeric
    for key in required_keys:
        # Skip if key is not in data
        if key not in data:
            continue
        values = data[key]
        # Check that values is a list of lists
        if not all(isinstance(inner_list, list) for inner_list in values):
            raise ValidationError(f"{key} contains elements that are not lists")

        # Check each inner list to ensure all elements are numeric
        for i, inner_list in enumerate(values):
            non_numeric_values = [
                j
                for j, val in enumerate(inner_list)
                if not isinstance(val, (int, float))
            ]
            if non_numeric_values:
                raise ValidationError(
                    f"Non-numeric elements in {key}[{i}] at indices: {non_numeric_values[:5]}{'...' if len(non_numeric_values) > 5 else ''}"
                )

    logger.debug(f"Structure validation passed for {len(data)} measurement types")


def _validate_data_lengths(
    data: Dict[str, List[float]], config: PipelineConfig
) -> None:
    """Validate data lengths for consistency."""
    # Get the lengths of all measurement collections
    lengths = {key: len(values) for key, values in data.items()}

    # Check if all collections have the same length
    unique_lengths = set(lengths.values())
    if len(unique_lengths) > 1:
        length_details = ", ".join([f"{k}: {v}" for k, v in lengths.items()])
        raise ValidationError(f"Inconsistent measurement lengths: {length_details}")

    actual_length = next(iter(lengths.values())) if lengths else 0

    logger.debug(
        f"Length validation passed: all measurements have consistent length ({actual_length})"
    )


def _validate_value_ranges(data: Dict[str, List[float]]) -> None:
    """Validate physical value ranges for screw measurements."""
    # Define expected physical ranges for screw measurements
    # These should be adjusted based on actual physical constraints of your system
    physical_ranges = {
        "torque_values": {"min": 0.0, "max": 1000.0},  # Nm, positive only
        "angle_values": {
            "min": 0.0,
            "max": 3600.0,
        },  # Degrees, can accumulate multiple rotations
        "gradient_values": {
            "min": -100.0,
            "max": 100.0,
        },  # Rate of change, can be negative
        "time_values": {"min": 0.0, "max": float("inf")},  # Time is always positive
    }

    # Validate each measurement type against its expected range
    for key, values in data.items():
        if key in physical_ranges:
            constraints = physical_ranges[key]
            min_val = min(values) if values else 0
            max_val = max(values) if values else 0

            # Check minimum value
            if min_val < constraints["min"]:
                raise ValidationError(
                    f"{key} contains values below physical minimum: {min_val} < {constraints['min']}"
                )

            # Check maximum value if not infinity
            if constraints["max"] != float("inf") and max_val > constraints["max"]:
                raise ValidationError(
                    f"{key} contains values above physical maximum: {max_val} > {constraints['max']}"
                )

    logger.debug(
        "Range validation passed: all measurements within expected physical ranges"
    )


def _validate_measurement_consistency(data: Dict[str, List[float]]) -> None:
    """Validate consistency across measurements based on physical relationships."""
    # Check if both torque and angle are present to validate their relationship
    if "torque_values" in data and "angle_values" in data:
        torque = data["torque_values"]
        angle = data["angle_values"]

        # Simple validation: Check that angle is monotonically increasing
        # This is a basic physical constraint in screw driving
        if len(angle) > 1:
            non_increasing = sum(
                1 for i in range(1, len(angle)) if angle[i] < angle[i - 1]
            )
            if non_increasing > 0:
                # Allow for a small percentage of non-increasing values due to sensor noise
                non_increasing_percent = (non_increasing / len(angle)) * 100
                if non_increasing_percent > 5:  # Allow up to 5% non-monotonic points
                    raise ValidationError(
                        f"Angle values are not consistently increasing ({non_increasing_percent:.1f}% decreasing values)"
                    )

    # Check time values for monotonicity if present
    if "time_values" in data:
        time = data["time_values"]
        if len(time) > 1:
            non_increasing = sum(
                1 for i in range(1, len(time)) if time[i] <= time[i - 1]
            )
            if non_increasing > 0:
                raise ValidationError(
                    f"Time values are not strictly increasing ({non_increasing} non-increasing points)"
                )

    logger.debug(
        "Consistency validation passed: measurement relationships are physically plausible"
    )


def _validate_format_requirements(
    data: Dict[str, List[float]], config: PipelineConfig
) -> None:
    """Validate format-specific requirements for the output format."""
    output_format = config.output_format

    # Additional checks specific to each output format
    if output_format == "list":
        # List format is most lenient, basic validation already done
        pass

    elif output_format == "numpy":
        # For numpy, check that there are no NaN or infinite values
        for key, values in data.items():
            # Check each individual value for NaN or infinity
            invalid_indices = [
                i
                for i, val in enumerate(values)
                if not isinstance(val, (int, float))
                or (isinstance(val, float) and not isfinite(val))
            ]
            if invalid_indices:
                raise ValidationError(
                    f"{key} contains NaN or infinite values at indices: {invalid_indices[:5]}{'...' if len(invalid_indices) > 5 else ''}"
                )

    elif output_format == "dataframe":
        # For dataframe, check that all measurement collections have consistent length
        # This is already checked in _validate_data_lengths
        pass

    elif output_format == "tensor":
        # For tensor format, same requirements as numpy
        for key, values in data.items():
            # Check each individual value for NaN or infinity
            invalid_indices = [
                i
                for i, val in enumerate(values)
                if not isinstance(val, (int, float))
                or (isinstance(val, float) and not isfinite(val))
            ]
            if invalid_indices:
                raise ValidationError(
                    f"{key} contains NaN or infinite values at indices: {invalid_indices[:5]}{'...' if len(invalid_indices) > 5 else ''}"
                )

    else:
        logger.warning(
            f"Unknown output format: {output_format}, skipping format-specific validation"
        )

    logger.debug(f"Format validation passed for output format: {output_format}")
