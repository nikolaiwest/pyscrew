from pathlib import Path
from typing import Any, Dict, Union

from sklearn.pipeline import Pipeline

from pyscrew.transformers import (
    InterpolateMissingsTransformer,
    PipelineLoggingTransformer,
    RemoveDuplicatesTransformer,
    UnpackStepsTransformer,
)
from pyscrew.utils.data_model import Measurements, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)

MEASUREMENTS = Measurements()


class ProcessingError(Exception):
    """Custom exception for processing errors."""

    pass


def create_processing_pipeline(config: Dict[str, Any]) -> Pipeline:
    """Creates the data processing pipeline based on configuration.

    The pipeline processes screw driving data through these steps:
    1. Input state logging
    2. Unpacking raw step data into measurements
    3. Removing duplicate time points (if enabled)
    4. Interpolating to equidistant points (if enabled)
    5. Output state logging

    Args:
        config: Pipeline configuration including:
            - handle_duplicates: Whether to handle duplicate time points
            - duplicate_strategy: Strategy for handling duplicates
            - interpolate_missings: Whether to apply interpolation
            - target_interval: Time interval for interpolation

    Returns:
        Configured scikit-learn Pipeline
    """
    steps = []

    # 1. Add input logging
    steps.append(("input_logger", PipelineLoggingTransformer("Input")))

    # 2. Add step unpacking
    steps.append(("unpack_steps", UnpackStepsTransformer()))

    # 3. Add duplicate handler if enabled
    if True:  # TODO: Implement with config parameter
        duplicate_strategy = "mean"
        logger.info(f"Adding duplicate handler with {duplicate_strategy} strategy")
        steps.append(
            (
                "remove_duplicates",
                RemoveDuplicatesTransformer(strategy=duplicate_strategy),
            )
        )

    # 4. Add interpolation for equidistant time points
    if True:  # TODO: Only default to True for backward compatibility
        target_interval = 0.0012
        logger.info(f"Adding interpolation with interval {target_interval}")
        steps.append(
            (
                "interpolate_missings",
                InterpolateMissingsTransformer(target_interval=target_interval),
            )
        )

    # 5. Add output logging
    steps.append(("output_logger", PipelineLoggingTransformer("Output")))

    return Pipeline(steps)


def process_data(data_path: Union[str, Path], config: Dict[str, Any]) -> ScrewDataset:
    """Process screw driving data according to configuration.

    Args:
        data_path: Path to directory containing JSON files
        config: Processing configuration dictionary

    Returns:
        Processed dataset

    Raises:
        ProcessingError: If processing fails
    """
    try:
        # Create dataset using the from_config method
        dataset = ScrewDataset.from_config(data_path, config)

        # Create and fit pipeline
        pipeline = create_processing_pipeline(config)
        processed_dataset = pipeline.fit_transform(dataset)

        # Return processed data
        return processed_dataset.processed_data

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise ProcessingError(f"Failed to process data: {str(e)}")
