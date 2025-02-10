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


class InitialTransformer(BaseEstimator, TransformerMixin):
    """Organizes raw ScrewDataset values into processed_data structure.

    Args:
        include_steps: If True, adds step indicators that map each measurement
                       to its originating step number (0,1,2,3)
    """

    def __init__(self, include_steps: bool = True):
        self.include_steps = include_steps

    def fit(self, dataset: ScrewDataset, y=None):
        """Nothing to fit, just implements interface."""
        return self

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """
        Transform raw data into organized measurement collections.

        Creates a dictionary with measurement arrays and optionally step indicators.
        """
        # Initialize all measurement lists
        measurements = [
            MEASUREMENTS.TORQUE,
            MEASUREMENTS.ANGLE,
            MEASUREMENTS.GRADIENT,
            MEASUREMENTS.TIME,
        ]
        dataset.processed_data = {m: [] for m in measurements}

        if self.include_steps:
            dataset.processed_data[MEASUREMENTS.STEP] = []

        # Pre-allocate lists for each run
        for _ in dataset.screw_runs:
            for measurement in measurements:
                dataset.processed_data[measurement].append([])
            if self.include_steps:
                dataset.processed_data[MEASUREMENTS.STEP].append([])

        # Single pass through runs and steps
        for run_idx, run in enumerate(dataset.screw_runs):
            for step_idx, step in enumerate(run.steps):
                # Get length once since we'll use it multiple times
                step_length = len(step.get_values(MEASUREMENTS.TIME))

                # Process all measurements for this step
                for measurement in measurements:
                    values = step.get_values(measurement)
                    dataset.processed_data[measurement][run_idx].extend(values)

                # Add step indicators if requested
                if self.include_steps:
                    dataset.processed_data[MEASUREMENTS.STEP][run_idx].extend(
                        [step_idx] * step_length
                    )

        return dataset


def create_processing_pipeline(config: Dict[str, Any]) -> Pipeline:
    """Creates the processing pipeline based on configuration.

    Args:
        config: Dictionary containing pipeline configuration

    Returns:
        Configured sklearn Pipeline
    """
    steps = []

    # Add input and output logging transformers
    steps.append(("input_logger", LoggingTransformer("Input Logger")))

    # Add initial transformer to organize data
    steps.append(("initial_transformer", InitialTransformer()))

    # Add final logging transformer
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
