"""
Pipeline state logging transformer for monitoring data processing stages.

This transformer provides visibility into data flow through the scikit-learn pipeline
by logging dataset characteristics at different processing stages. It can be inserted
at key points in the pipeline to track:
- Number of runs being processed
- Measurement availability and completeness
- Data structure consistency

The transformer is passive (does not modify data) and is primarily used for:
- Debugging pipeline issues
- Validating data transformations
- Monitoring processing progress
"""

from sklearn.base import BaseEstimator, TransformerMixin

from pyscrew.core import JsonFields, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineLoggingTransformer(BaseEstimator, TransformerMixin):
    """
    Logs data structure and state during pipeline execution.

    This transformer can be inserted at any point in a scikit-learn pipeline
    to monitor the state of data as it flows through different processing stages.
    It performs no modifications to the data, only logging information about
    dataset size and measurement completeness.

    Args:
        name: Identifier for this logging point in the pipeline, used to
              distinguish between multiple logging transformers in the same pipeline

    Attributes:
        name: String identifier for this transformer instance

    Example:
        >>> from sklearn.pipeline import Pipeline
        >>> pipeline = Pipeline([
        ...     ("input_state", PipelineLoggingTransformer("Input")),
        ...     # ... processing transformers ...
        ...     ("output_state", PipelineLoggingTransformer("Output"))
        ... ])
        >>> pipeline.fit_transform(dataset)
        Input - Fit: Dataset contains 100 runs
        Input - Transform: Processing 100 runs
        Output - Fit: Dataset contains 100 runs
        Output - Transform: Processing 100 runs
    """

    def __init__(self, name: str = "Logger"):
        """Initialize the transformer with a name for identification in logs."""
        self.name = name

    def fit(self, dataset: ScrewDataset, y=None) -> "PipelineLoggingTransformer":
        """
        Log dataset structure during pipeline fitting.

        This method logs:
        - Total number of runs in the dataset
        - Number of runs containing each measurement type

        Args:
            dataset: ScrewDataset instance being processed
            y: Ignored, included for scikit-learn compatibility

        Returns:
            self, following scikit-learn transformer convention
        """
        logger.info(f"{self.name} - Fit: Dataset contains {len(dataset)} runs")

        measurements = JsonFields.Measurements()
        for measurement in [
            measurements.TIME,
            measurements.TORQUE,
            measurements.ANGLE,
            measurements.GRADIENT,
        ]:
            values = dataset.get_values(measurement)
            logger.info(f"{measurement}: {len(values)} runs")

        return self

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """
        Log dataset state during transformation and return unchanged.

        Args:
            dataset: ScrewDataset instance to examine

        Returns:
            Unmodified dataset, following scikit-learn transformer convention
        """
        logger.info(f"{self.name} - Transform: Processing {len(dataset)} runs")
        return dataset
