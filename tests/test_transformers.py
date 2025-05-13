from pathlib import Path

import pytest

from pyscrew.config import PipelineConfig
from pyscrew.core.fields import OutputFields
from pyscrew.pipeline.transformers import (
    DatasetConversionTransformer,
    HandleDuplicatesTransformer,
    HandleLengthsTransformer,
    HandleMissingsTransformer,
    UnpackStepsTransformer,
)


def test_unpack_steps_transformer(raw_test_dataset, test_config):
    """Test UnpackStepsTransformer extracts data correctly."""
    # Create transformer
    transformer = UnpackStepsTransformer(test_config)

    # Apply transformation
    result = transformer.transform(raw_test_dataset)

    # Verify output structure
    assert hasattr(result, "processed_data")
    assert "time_values" in result.processed_data
    assert "torque_values" in result.processed_data
    assert "angle_values" in result.processed_data
    assert "gradient_values" in result.processed_data
    assert "step_values" in result.processed_data
    assert "class_values" in result.processed_data

    # Check dimensions
    num_runs = len(result.processed_data["class_values"])
    assert num_runs == len(raw_test_dataset)

    # Check that data is not empty
    for run_idx in range(num_runs):
        assert len(result.processed_data["time_values"][run_idx]) > 0
        assert len(result.processed_data["torque_values"][run_idx]) > 0


def test_handle_duplicates_transformer(unpacked_test_dataset, test_config):
    """Test HandleDuplicatesTransformer removes duplicates."""
    # Configure transformer
    config = PipelineConfig(
        scenario_name=test_config.scenario_name,
        cache_dir=test_config.cache_dir,
        handle_duplicates="first",
    )
    transformer = HandleDuplicatesTransformer(config)

    # Store original info
    outputs = OutputFields()
    original_counts = []
    for time_series in unpacked_test_dataset.processed_data[outputs.TIME_VALUES]:
        original_counts.append(len(time_series))

    # Apply transformation
    result = transformer.transform(unpacked_test_dataset)

    # Check result
    for i, time_series in enumerate(result.processed_data[outputs.TIME_VALUES]):
        # Time series should either be same length or shorter
        assert len(time_series) <= original_counts[i]

        # Time values should be strictly increasing (no duplicates)
        for j in range(len(time_series) - 1):
            assert time_series[j] < time_series[j + 1]


def test_handle_lengths_transformer(unpacked_test_dataset, test_config):
    """Test HandleLengthsTransformer normalizes lengths."""
    # Configure transformer
    target_length = 500
    config = PipelineConfig(
        scenario_name=test_config.scenario_name,
        cache_dir=test_config.cache_dir,
        target_length=target_length,
    )
    transformer = HandleLengthsTransformer(config)

    # Apply transformation
    result = transformer.transform(unpacked_test_dataset)

    # Check all series have target length
    outputs = OutputFields()
    for time_series in result.processed_data[outputs.TIME_VALUES]:
        assert len(time_series) == target_length


def test_handle_missings_transformer(unpacked_test_dataset, test_config):
    """Test HandleMissingsTransformer creates equidistant time points."""
    # Configure transformer
    config = PipelineConfig(
        scenario_name=test_config.scenario_name,
        cache_dir=test_config.cache_dir,
        handle_missings="mean",  # Use linear interpolation
    )
    transformer = HandleMissingsTransformer(config)

    # Apply transformation
    result = transformer.transform(unpacked_test_dataset)

    # Check that time points are equidistant
    outputs = OutputFields()
    for time_series in result.processed_data[outputs.TIME_VALUES]:
        if len(time_series) > 2:  # Need at least 3 points to check intervals
            # Calculate intervals between consecutive time points
            intervals = [
                time_series[i + 1] - time_series[i] for i in range(len(time_series) - 1)
            ]

            # Check if all intervals are approximately equal
            target_interval = 0.0012  # Standard time interval
            tolerance = 1e-6  # Allow for small floating-point differences

            for interval in intervals:
                assert (
                    abs(interval - target_interval) < tolerance
                ), f"Time interval {interval} deviates from expected {target_interval}"

            # Check that missing values were interpolated
            # Torque should have values at all time points
            torque_series = result.processed_data[outputs.TORQUE_VALUES][
                result.processed_data[outputs.TIME_VALUES].index(time_series)
            ]
            assert len(torque_series) == len(time_series)


def test_dataset_conversion_transformer(unpacked_test_dataset, test_config):
    """Test DatasetConversionTransformer converts to different formats."""
    # Configure transformer for list format
    config = PipelineConfig(
        scenario_name=test_config.scenario_name,
        cache_dir=test_config.cache_dir,
        output_format="list",
    )
    transformer = DatasetConversionTransformer(config)

    # Apply transformation
    result = transformer.transform(unpacked_test_dataset)

    # Check result structure
    outputs = OutputFields()
    assert outputs.TIME_VALUES in result.processed_data
    assert outputs.TORQUE_VALUES in result.processed_data
    assert isinstance(result.processed_data[outputs.TIME_VALUES], list)
    assert isinstance(result.processed_data[outputs.TORQUE_VALUES], list)

    # Verify that first element is a list (nested structure)
    assert isinstance(result.processed_data[outputs.TIME_VALUES][0], list)

    # Test with measurements filter
    config = PipelineConfig(
        scenario_name=test_config.scenario_name,
        cache_dir=test_config.cache_dir,
        output_format="list",
        measurements=["torque", "angle"],  # Only include these measurements
    )
    transformer = DatasetConversionTransformer(config)
    result = transformer.transform(unpacked_test_dataset)

    # Should include only torque and angle
    assert outputs.TORQUE_VALUES in result.processed_data
    assert outputs.ANGLE_VALUES in result.processed_data

    # Time values should be included by default
    assert outputs.TIME_VALUES in result.processed_data
