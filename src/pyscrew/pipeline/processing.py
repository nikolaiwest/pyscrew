"""
Data processing pipeline for screw operation analysis.

This module implements a scikit-learn pipeline for processing screw operation data.
The pipeline transforms raw step-based measurements into analysis-ready format through
a series of configurable transformations:

1. Input validation and logging
2. Step data unpacking into measurement collections
3. Time point deduplication (optional)
4. Measurement interpolation (optional)
5. Length normalization (optional)
6. Dataset conversion for output
7. Output validation and logging

Each transformation is implemented as a scikit-learn transformer that accepts a
PipelineConfig object, allowing for:
- Consistent interface across transformations
- Centralized configuration management
- Extensibility for new transformations
"""

from typing import Dict, List, cast

from sklearn.pipeline import Pipeline

from pyscrew.config import PipelineConfig
from pyscrew.core import ScrewDataset
from pyscrew.utils.logger import get_logger

from .transformers import (
    DatasetConversionTransformer,
    HandleDuplicatesTransformer,
    HandleLengthsTransformer,
    HandleMissingsTransformer,
    PipelineLoggingTransformer,
    UnpackStepsTransformer,
)

logger = get_logger(__name__)


class ProcessingError(Exception):
    """Raised when pipeline processing fails due to invalid data, configuration, or operation constraints."""

    pass


def create_processing_pipeline(config: PipelineConfig) -> Pipeline:
    """
    Create a configured processing pipeline for screw operation data.

    The pipeline implements these processing stages:
    1. Input State Logging:
       - Validates initial data structure
       - Logs dataset characteristics

    2. Step Data Unpacking:
       - Transforms hierarchical step data into measurement collections
       - Maintains run-level organization
       - Tracks measurement origins

    3. Duplicate Value Handling:
       - Identifies duplicate time points
       - Applies configured handling method (first, last, mean)
       - Validates time sequence consistency

    4. Missing Value Handling:
       - Ensures equidistant time points
       - Handles missing values based on config method
       - Maintains measurement alignment

    5. Length Normalization:
       - Ensures all measurement sequences have equal length
       - Pads shorter sequences or truncates longer ones

    6. Dataset Conversion:
       - Converts the dataset to the final output format
       - Applies any final transformations needed for output

    7. Output State Logging:
       - Validates processed data
       - Logs transformation results

    Args:
        config: Complete pipeline configuration object

    Returns:
        Configured scikit-learn Pipeline ready for execution

    Raises:
        ProcessingError: On pipeline configuration failure
    """
    try:
        steps = []

        # 1. Add input logging transformer (initial step)
        logger.info("Adding input_logging transformer to pipeline")
        steps.append(("input_logging", PipelineLoggingTransformer(config, "Input")))

        # 2. Add step unpacking transformer (required step)
        logger.info("Adding step_unpacking transformer to pipeline")
        steps.append(("step_unpacking", UnpackStepsTransformer(config)))

        # 3. Add duplicate value handler (if configured)
        if config.handle_duplicates:
            logger.info(f"Adding duplicate handling with {config.handle_duplicates}")
            steps.append(("duplicate_handling", HandleDuplicatesTransformer(config)))

        # 4. Add missing value handler (if configured)
        if config.handle_missings:
            logger.info(f"Adding handling of missings with {config.handle_missings}")
            steps.append(("missing_value_handling", HandleMissingsTransformer(config)))

        # 5. Add length normalization handler (if configured)
        if config.target_length:
            logger.info(f"Adding length normalization with {config.target_length}")
            steps.append(("length_normalization", HandleLengthsTransformer(config)))

        # 6. Add dataset conversion transformer (if configured)
        if config.output_format:
            logger.info(f"Adding dataset conversion with {config.output_format}")
            steps.append(("dataset_conversion", DatasetConversionTransformer(config)))

        # 7. Add output logging transformer (final step)
        logger.info("Adding output_logging transformer to pipeline")
        steps.append(("output_logging", PipelineLoggingTransformer(config, "Output")))

        return Pipeline(steps)

    except Exception as e:
        error_msg = f"Failed to create processing pipeline: {str(e)}"
        logger.error(error_msg)
        raise ProcessingError(error_msg) from e


def process_data(pipeline_config: PipelineConfig) -> Dict[str, List[float]]:
    """
    Process screw operation data according to configuration.

    This function orchestrates the complete data processing workflow:
    1. Creates dataset from configuration
    2. Builds processing pipeline
    3. Executes transformations
    4. Returns processed results

    Args:
        pipeline_config: Complete pipeline configuration with scenario and processing settings

    Returns:
        Dictionary containing processed measurements with keys:
            - "time_values": List of time measurements
            - "torque_values": List of torque measurements
            - "angle_values": List of angle measurements
            - "gradient_values": List of gradient measurements
            - "step_values": List of step indicators
            - "class_labels": List of class labels

    Raises:
        ProcessingError: If any stage of processing fails
            - Dataset creation errors
            - Pipeline configuration issues
            - Transformation failures
    """
    # Create dataset from configuration
    dataset = ScrewDataset.from_config(pipeline_config)

    # Create and execute pipeline
    pipeline = create_processing_pipeline(pipeline_config)

    # Apply cast to help type checker recognize that pipeline.fit_transform maintains ScrewDataset type
    # This doesn't change the runtime behavior, just helps with static type checking
    processed_dataset = cast(ScrewDataset, pipeline.fit_transform(dataset))

    return processed_dataset.processed_data
