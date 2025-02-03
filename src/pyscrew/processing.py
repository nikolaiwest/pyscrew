from pathlib import Path
from typing import Any, Dict, Union

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

from pyscrew.utils.data_model import Measurements, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)

MEASUREMENTS = Measurements()


class ProcessingError(Exception):
    """Custom exception for processing errors."""

    pass


class LoggingTransformer(BaseEstimator, TransformerMixin):
    """Simple transformer that logs data structure and passes through data unchanged."""

    def __init__(self, name: str = "Logger"):
        self.name = name

    def fit(self, dataset: ScrewDataset, y=None) -> "LoggingTransformer":
        """Log dataset structure during fit.

        Args:
            dataset: Input dataset to analyze
            y: Ignored (included for sklearn compatibility)

        Returns:
            self
        """
        logger.info(f"{self.name} - Fit: Dataset contains {len(dataset)} runs")

        for measurement in [
            MEASUREMENTS.TIME,
            MEASUREMENTS.TORQUE,
            MEASUREMENTS.ANGLE,
            MEASUREMENTS.GRADIENT,
        ]:
            values = dataset.get_values(measurement)
            logger.info(f"{measurement}: {len(values)} runs")
        return self

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """Log dataset structure during transform and return unchanged.

        Args:
            dataset: Input dataset to process

        Returns:
            Unchanged dataset
        """
        logger.info(f"{self.name} - Transform: Processing {len(dataset)} runs")
        return dataset


def create_processing_pipeline(config: Dict[str, Any]) -> Pipeline:
    """Creates the processing pipeline based on configuration.

    Args:
        config: Dictionary containing pipeline configuration

    Returns:
        Configured sklearn Pipeline
    """
    steps = []
    steps.append(("input_logger", LoggingTransformer("Input Logger")))
    steps.append(("output_logger", LoggingTransformer("Output Logger")))
    return Pipeline(steps)


def process_data(data_path: Union[str, Path], config: Dict[str, Any]) -> ScrewDataset:
    """Process screw driving data according to configuration.

    Args:
        data_path: Path to directory containing JSON files
        config: Dictionary containing processing configuration

    Returns:
        Processed dataset

    Raises:
        ProcessingError: If processing fails
    """
    try:
        # Create dataset from files
        file_names = [f.name for f in Path(data_path).glob("*.json")]
        dataset = ScrewDataset(data_path, file_names)

        # Create and fit pipeline
        pipeline = create_processing_pipeline(config)
        processed_dataset = pipeline.fit_transform(dataset)

        return processed_dataset

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise ProcessingError(f"Failed to process data: {str(e)}")
