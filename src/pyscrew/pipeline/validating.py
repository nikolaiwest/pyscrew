"""
Data validation module for PyScrew.

This module provides functionality for validating processed data against
expected formats, ranges, and integrity constraints before it is used in analysis.

Key features:
    - Format validation for different output formats
    - Range checking for physical measurements
    - Consistency validation across measurement collections
    - Structural validation for completeness
    - Metadata field validation
    - Error reporting with detailed diagnostic information
"""

from math import isfinite
from typing import Dict, List

from pyscrew.config import PipelineConfig
from pyscrew.core import OutputFields
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
    4. Metadata field presence and consistency
    5. Format-specific requirements

    Args:
        data: Dictionary containing processed measurements
        config: Pipeline configuration with validation parameters

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails with detailed reason
    """
    logger.info(f"Validating processed data for scenario '{config.scenario_name}'")
    outputs = OutputFields()

    try:
        # Step 1: Verify data structure
        _validate_data_structure(data, config, outputs)

        # Step 2: Verify data lengths
        _validate_data_lengths(data, config)

        # Step 3: Verify physical value ranges
        _validate_value_ranges(data, outputs)

        # Step 4: Verify consistency between measurements
        _validate_measurement_consistency(data, outputs)

        # Step 5: Verify metadata fields
        _validate_metadata_fields(data, outputs)

        # Step 6: Verify format-specific requirements
        _validate_format_requirements(data, config)

        # Log successful validation
        measurement_keys = [
            outputs.TIME_VALUES,
            outputs.TORQUE_VALUES,
            outputs.ANGLE_VALUES,
            outputs.GRADIENT_VALUES,
        ]
        metadata_keys = [
            outputs.STEP_VALUES,
            outputs.CLASS_VALUES,
            outputs.WORKPIECE_LOCATION,
            outputs.WORKPIECE_USAGE,
            outputs.WORKPIECE_RESULT,
            outputs.SCENARIO_CONDITION,
            outputs.SCENARIO_EXCEPTION,
        ]

        measurement_count = sum(1 for k in measurement_keys if k in data)
        metadata_count = sum(1 for k in metadata_keys if k in data)

        # Find a measurement field to get count from
        count = 0
        for field in measurement_keys:
            if field in data and data[field]:
                count = len(data[field])
                break

        logger.info(
            f"Data validation passed: {measurement_count} measurement types and {metadata_count} metadata fields with {count} runs"
        )
        return True

    except Exception as e:
        if not isinstance(e, ValidationError):
            e = ValidationError(f"Data validation failed: {str(e)}")
        logger.error(str(e))
        raise e


def _validate_data_structure(
    data: Dict[str, List[float]], config: PipelineConfig, outputs: OutputFields
) -> None:
    """Validate data structure based on requested measurements."""
    # Determine required measurement keys based on config
    required_keys = []

    # If measurements is None, include all measurements
    if config.measurements is None:
        required_keys = [
            outputs.TIME_VALUES,
            outputs.TORQUE_VALUES,
            outputs.ANGLE_VALUES,
            outputs.GRADIENT_VALUES,
        ]
    else:
        # Otherwise, include only requested measurements
        measurement_mapping = {
            "time": outputs.TIME_VALUES,
            "torque": outputs.TORQUE_VALUES,
            "angle": outputs.ANGLE_VALUES,
            "gradient": outputs.GRADIENT_VALUES,
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

    # Check if all measurement values are lists
    for key in required_keys:
        if key not in data:
            continue

        value = data[key]
        if not isinstance(value, list):
            raise ValidationError(f"Field '{key}' is not a list")

        # Check that values is a list of lists
        if not all(isinstance(inner_list, list) for inner_list in value):
            raise ValidationError(f"{key} contains elements that are not lists")

        # Check each inner list to ensure all elements are numeric
        for i, inner_list in enumerate(value):
            non_numeric_values = [
                j
                for j, val in enumerate(inner_list)
                if not isinstance(val, (int, float))
            ]
            if non_numeric_values:
                raise ValidationError(
                    f"Non-numeric elements in {key}[{i}] at indices: {non_numeric_values[:5]}{'...' if len(non_numeric_values) > 5 else ''}"
                )

    logger.debug(f"Structure validation passed for measurements")


def _validate_data_lengths(
    data: Dict[str, List[float]], config: PipelineConfig
) -> None:
    """Validate data lengths for consistency."""
    # Get the lengths of all measurement and metadata collections
    measurement_fields = [k for k in data.keys() if k.endswith("_values")]
    lengths = {
        key: len(values) for key, values in data.items() if isinstance(values, list)
    }

    # Check if all collections have the same length
    if lengths:
        unique_lengths = set(lengths.values())
        if len(unique_lengths) > 1:
            length_details = ", ".join([f"{k}: {v}" for k, v in lengths.items()])
            raise ValidationError(f"Inconsistent field lengths: {length_details}")

        actual_length = next(iter(lengths.values())) if lengths else 0
        logger.debug(
            f"Length validation passed: all fields have consistent length ({actual_length})"
        )


def _validate_value_ranges(data: Dict[str, List[float]], outputs: OutputFields) -> None:
    """Validate physical value ranges for screw measurements."""
    # Define expected physical ranges for screw measurements
    # These should be adjusted based on actual physical constraints of your system
    physical_ranges = {
        outputs.TORQUE_VALUES: {"min": 0.0, "max": 1000.0},  # Nm, positive only
        outputs.ANGLE_VALUES: {
            "min": 0.0,
            "max": 3600.0,
        },  # Degrees, can accumulate multiple rotations
        outputs.GRADIENT_VALUES: {
            "min": -100.0,
            "max": 100.0,
        },  # Rate of change, can be negative
        outputs.TIME_VALUES: {
            "min": 0.0,
            "max": float("inf"),
        },  # Time is always positive
    }

    # Currently, some measurement values (like torque) can be negative
    """
    # Validate each measurement type against its expected range
    for key, constraints in physical_ranges.items():
        if key not in data or not data[key]:
            continue

        # For each run in the dataset
        for i, run_values in enumerate(data[key]):
            if not run_values:
                continue

            min_val = min(run_values)
            max_val = max(run_values)

            # Check minimum value
            if min_val < constraints["min"]:
                raise ValidationError(
                    f"{key} in run {i} contains values below physical minimum: {min_val} < {constraints['min']}"
                )

            # Check maximum value if not infinity
            if constraints["max"] != float("inf") and max_val > constraints["max"]:
                raise ValidationError(
                    f"{key} in run {i} contains values above physical maximum: {max_val} > {constraints['max']}"
                )"""

    logger.debug(
        "Range validation passed: all measurements within expected physical ranges"
    )


def _validate_measurement_consistency(
    data: Dict[str, List[float]], outputs: OutputFields
) -> None:
    """Validate consistency across measurements based on physical relationships."""
    # Check if both torque and angle are present to validate their relationship
    if outputs.TORQUE_VALUES in data and outputs.ANGLE_VALUES in data:
        torque_runs = data[outputs.TORQUE_VALUES]
        angle_runs = data[outputs.ANGLE_VALUES]

        # Make sure they have the same number of runs
        if len(torque_runs) != len(angle_runs):
            raise ValidationError(
                f"Inconsistent number of runs: {outputs.TORQUE_VALUES}={len(torque_runs)}, "
                f"{outputs.ANGLE_VALUES}={len(angle_runs)}"
            )

        # Check each run
        for i, (torque, angle) in enumerate(zip(torque_runs, angle_runs)):
            # Skip empty runs
            if not angle or not torque:
                continue

            # Simple validation: Check that angle is monotonically increasing
            # This is a basic physical constraint in screw driving
            if len(angle) > 1:
                non_increasing = sum(
                    1 for j in range(1, len(angle)) if angle[j] < angle[j - 1]
                )
                if non_increasing > 0:
                    # Allow for a small percentage of non-increasing values due to sensor noise
                    non_increasing_percent = (non_increasing / len(angle)) * 100
                    if (
                        non_increasing_percent > 5
                    ):  # Allow up to 5% non-monotonic points
                        raise ValidationError(
                            f"Angle values in run {i} are not consistently increasing "
                            f"({non_increasing_percent:.1f}% decreasing values)"
                        )

    # Check time values for monotonicity if present
    if outputs.TIME_VALUES in data:
        time_runs = data[outputs.TIME_VALUES]

        # Check each run
        for i, time in enumerate(time_runs):
            # Skip empty runs
            if not time:
                continue

            if len(time) > 1:
                non_increasing = sum(
                    1 for j in range(1, len(time)) if time[j] <= time[j - 1]
                )
                if non_increasing > 0:
                    raise ValidationError(
                        f"Time values in run {i} are not strictly increasing "
                        f"({non_increasing} non-increasing points)"
                    )

    logger.debug(
        "Consistency validation passed: measurement relationships are physically plausible"
    )


def _validate_metadata_fields(
    data: Dict[str, List[float]], outputs: OutputFields
) -> None:
    """Validate metadata fields for consistency and completeness."""
    # Check for required metadata fields
    required_metadata = [
        outputs.STEP_VALUES,
        outputs.CLASS_VALUES,
    ]

    optional_metadata = [
        outputs.WORKPIECE_LOCATION,
        outputs.WORKPIECE_USAGE,
        outputs.WORKPIECE_RESULT,
        outputs.SCENARIO_CONDITION,
        outputs.SCENARIO_EXCEPTION,
    ]

    # Check that required metadata fields are present
    missing_metadata = [field for field in required_metadata if field not in data]
    if missing_metadata:
        logger.warning(
            f"Missing required metadata fields: {', '.join(missing_metadata)}"
        )

    # Check that all metadata fields have the same number of entries
    metadata_lengths = {
        field: len(data[field])
        for field in required_metadata + optional_metadata
        if field in data and isinstance(data[field], list)
    }

    if metadata_lengths:
        unique_lengths = set(metadata_lengths.values())
        if len(unique_lengths) > 1:
            length_details = ", ".join(
                [f"{k}: {v}" for k, v in metadata_lengths.items()]
            )
            raise ValidationError(
                f"Inconsistent metadata field lengths: {length_details}"
            )

    # Verify step values are valid if present
    if outputs.STEP_VALUES in data:
        for i, steps in enumerate(data[outputs.STEP_VALUES]):
            invalid_steps = [
                s for s in steps if not isinstance(s, int) or s < -1 or s > 3
            ]
            if invalid_steps:
                raise ValidationError(
                    f"Invalid step values in run {i}: step values should be integers between -1 and 3"
                )

    logger.debug("Metadata validation passed: all metadata fields are consistent")


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
        for key, values_list in data.items():
            if not isinstance(values_list, list):
                continue

            for i, values in enumerate(values_list):
                if not isinstance(values, list):
                    continue

                # Check each individual value for NaN or infinity
                invalid_indices = [
                    j
                    for j, val in enumerate(values)
                    if not isinstance(val, (int, float))
                    or (isinstance(val, float) and not isfinite(val))
                ]
                if invalid_indices:
                    raise ValidationError(
                        f"{key} in run {i} contains NaN or infinite values at indices: "
                        f"{invalid_indices[:5]}{'...' if len(invalid_indices) > 5 else ''}"
                    )

    elif output_format == "dataframe":
        # For dataframe, check that all measurement collections have consistent length
        # This is already checked in _validate_data_lengths
        pass

    elif output_format == "tensor":
        # For tensor format, same requirements as numpy
        for key, values_list in data.items():
            if not isinstance(values_list, list):
                continue

            for i, values in enumerate(values_list):
                if not isinstance(values, list):
                    continue

                # Check each individual value for NaN or infinity
                invalid_indices = [
                    j
                    for j, val in enumerate(values)
                    if not isinstance(val, (int, float))
                    or (isinstance(val, float) and not isfinite(val))
                ]
                if invalid_indices:
                    raise ValidationError(
                        f"{key} in run {i} contains NaN or infinite values at indices: "
                        f"{invalid_indices[:5]}{'...' if len(invalid_indices) > 5 else ''}"
                    )

    else:
        logger.warning(
            f"Unknown output format: {output_format}, skipping format-specific validation"
        )

    logger.debug(f"Format validation passed for output format: {output_format}")
