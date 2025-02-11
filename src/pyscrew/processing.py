"""
Data processing pipeline for screw operation analysis.

This module implements a scikit-learn pipeline for processing screw operation data.
The pipeline transforms raw step-based measurements into analysis-ready format through
a series of configurable transformations:

1. Input validation and logging
2. Step data unpacking into measurement collections
3. Time point deduplication (optional)
4. Measurement interpolation (optional)
5. Output validation and logging

Each transformation is implemented as a scikit-learn transformer, allowing for:
- Consistent interface across transformations
- Easy pipeline configuration
- Extensibility for new transformations
"""

from pathlib import Path
from typing import Any, Dict, Union

from sklearn.pipeline import Pipeline

from pyscrew.transformers import (
    InterpolateMissingsTransformer,
    PipelineLoggingTransformer,
    RemoveDuplicatesTransformer,
    UnpackStepsTransformer,
)
from pyscrew.utils.data_model import JsonFields, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class ProcessingError(Exception):
    """
    Raised when data processing fails.

    Common triggers:
        - Pipeline configuration errors
        - Transformer execution failures
        - Data validation errors
        - Input/output format mismatches
    """

    pass


def create_processing_pipeline(config: Dict[str, Any]) -> Pipeline:
    """
    Create a configured processing pipeline for screw operation data.

    The pipeline implements these processing stages:
    1. Input State Logging:
       - Validates initial data structure
       - Logs dataset characteristics

    2. Step Data Unpacking:
       - Transforms hierarchical step data into measurement collections
       - Maintains run-level organization
       - Optionally tracks measurement origins

    3. Duplicate Handling (optional):
       - Identifies duplicate time points
       - Applies configured resolution strategy
       - Validates time sequence consistency

    4. Measurement Interpolation (optional):
       - Ensures equidistant time points
       - Handles missing values
       - Maintains measurement alignment

    5. Output State Logging:
       - Validates processed data
       - Logs transformation results

    Args:
        config: Pipeline configuration including:
            - handle_duplicates: Enable duplicate handling
            - duplicate_strategy: How to resolve duplicates ("mean", "first", etc.)
            - interpolate_missings: Enable interpolation
            - target_interval: Time interval for interpolation (default: 0.0012s)

    Returns:
        Configured scikit-learn Pipeline ready for execution

    Example:
        >>> config = {
        ...     "handle_duplicates": True,
        ...     "duplicate_strategy": "mean",
        ...     "interpolate_missings": True,
        ...     "target_interval": 0.0012
        ... }
        >>> pipeline = create_processing_pipeline(config)
        >>> processed_data = pipeline.fit_transform(dataset)
    """
    steps = []

    # 1. Add input logging transformer
    steps.append(("input_logger", PipelineLoggingTransformer("Input")))

    # 2. Add step unpacking transformer
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

    # 4. Add interpolation transformer
    if True:  # TODO: Only default to True for backward compatibility
        target_interval = 0.0012  # Standard measurement interval
        logger.info(f"Adding interpolation with interval {target_interval}")
        steps.append(
            (
                "interpolate_missings",
                InterpolateMissingsTransformer(target_interval=target_interval),
            )
        )

    # 5. Add output logging transformer
    steps.append(("output_logger", PipelineLoggingTransformer("Output")))

    return Pipeline(steps)


def process_data(data_path: Union[str, Path], config: Dict[str, Any]) -> ScrewDataset:
    """
    Process screw operation data according to configuration.

    This function orchestrates the complete data processing workflow:
    1. Creates dataset from configuration
    2. Builds processing pipeline
    3. Executes transformations
    4. Returns processed results

    Args:
        data_path: Path to directory containing JSON measurement files
        config: Processing configuration dictionary containing pipeline settings

    Returns:
        Processed dataset with transformed measurements

    Raises:
        ProcessingError: If any stage of processing fails
            - Dataset creation errors
            - Pipeline configuration issues
            - Transformation failures
    """
    try:
        # Create dataset from configuration
        dataset = ScrewDataset.from_config(data_path, config)

        # Create and execute pipeline
        pipeline = create_processing_pipeline(config)
        processed_dataset = pipeline.fit_transform(dataset)

        return processed_dataset.processed_data

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise ProcessingError(f"Failed to process data: {str(e)}")
