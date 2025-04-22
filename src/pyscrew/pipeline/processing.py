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
6. Output validation and logging

Each transformation is implemented as a scikit-learn transformer, allowing for:
- Consistent interface across transformations
- Easy pipeline configuration
- Extensibility for new transformations
"""

from pathlib import Path
from typing import Dict, List, Union, cast

from sklearn.pipeline import Pipeline

from pyscrew.transformers import (
    HandleDuplicatesTransformer,
    HandleLengthsTransformer,
    HandleMissingsTransformer,
    PipelineLoggingTransformer,
    UnpackStepsTransformer,
)
from pyscrew.config import PipelineConfig
from pyscrew.core import ScrewDataset
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

    6. Output State Logging:
       - Validates processed data
       - Logs transformation results

    Args:
        config: Pipeline configuration including:
            - handle_duplicates: Which duplicates to keep? ("first", "last" or "mean")
            - handle_missings: How to handle missing values? ("mean", "zero", or float value)
            - handle_lengths: Desired length for all sequences (int)
            - output_format: Desired output format ("numpy", "dataframe", "list")

    Returns:
        Configured scikit-learn Pipeline ready for execution

    Raises:
        ProcessingError: On pipeline configuration failure
    """
    try:
        steps = []

        # 1. Add input logging transformer
        steps.append(("log_in", PipelineLoggingTransformer("Input")))

        # 2. Add step unpacking transformer
        steps.append(
            ("unpack", UnpackStepsTransformer(include_steps=True, include_classes=True))
        )

        # 3. Add duplicate value handler (if configured)
        if config.handle_duplicates:
            logger.info(f"Adding duplicate handler with {config.handle_duplicates}")
            steps.append(("dup", HandleDuplicatesTransformer(config.handle_duplicates)))

        # 4. Add missing value handler (if configured)
        if config.handle_missings:
            logger.info(f"Adding missing value handler with {config.handle_missings}")
            steps.append(("mis", HandleMissingsTransformer(config.handle_missings)))

        # 5. Add length normalization handler (if configured)
        if config.target_length:
            logger.info(
                f"Adding length normalization handler with target length {config.target_length}"
            )
            steps.append(
                (
                    "lengths",
                    HandleLengthsTransformer(
                        target_length=config.target_length,
                        padding_value=config.padding_value,
                        padding_position=config.padding_position,
                        cutoff_position=config.cutoff_position,
                    ),
                )
            )

        # 6. Add output logging transformer
        steps.append(("log_out", PipelineLoggingTransformer("Output")))

        return Pipeline(steps)

    except Exception as e:
        raise ProcessingError(f"Failed to create processing pipeline: {str(e)}") from e


def process_data(
    data_path: Union[str, Path], config: PipelineConfig
) -> Dict[str, List[float]]:
    """
    Process screw operation data according to configuration.

    This function orchestrates the complete data processing workflow:
    1. Creates dataset from configuration
    2. Builds processing pipeline
    3. Executes transformations
    4. Returns processed results

    Args:
        data_path: Path to directory containing JSON measurement files
        config: Pipeline configuration from ConfigSchema

    Returns:
        Dictionary containing processed measurements with keys:
            - "time values": List of time measurements
            - "torque values": List of torque measurements
            - "angle values": List of angle measurements
            - "gradient values": List of gradient measurements
            - "step values": List of step indicators
            - "class labels": List of class labels

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
        processed_dataset = cast(ScrewDataset, pipeline.fit_transform(dataset))

        # Return the processed data dictionary
        if not processed_dataset.processed_data:
            raise ProcessingError("Pipeline did not produce any processed data")

        return processed_dataset.processed_data

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise ProcessingError(f"Failed to process data: {str(e)}") from e
