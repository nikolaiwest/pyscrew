"""
Pipeline state logging transformer for monitoring data processing stages.
"""

from sklearn.base import BaseEstimator, TransformerMixin

from pyscrew.utils.data_model import MEASUREMENTS, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineLoggingTransformer(BaseEstimator, TransformerMixin):
    """
    Logs data structure and state during pipeline execution.

    This transformer is used to monitor the state of data at different
    points in the processing pipeline. It helps with debugging and
    verification by logging dataset size and measurement information.

    Args:
        name: Identifier for this logging point in the pipeline

    Example:
        >>> pipeline = Pipeline([
        ...     ("input_state", PipelineLoggingTransformer("Input")),
        ...     # ... other transformers ...
        ...     ("output_state", PipelineLoggingTransformer("Output"))
        ... ])
    """

    def __init__(self, name: str = "Logger"):
        self.name = name

    def fit(self, dataset: ScrewDataset, y=None) -> "PipelineLoggingTransformer":
        """Log dataset structure during fit phase."""
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
        """Log dataset structure and return unchanged data."""
        logger.info(f"{self.name} - Transform: Processing {len(dataset)} runs")
        return dataset
