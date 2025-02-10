"""
Transformer for handling duplicate time points in measurement data.
"""

from typing import Literal

from sklearn.base import BaseEstimator, TransformerMixin

from pyscrew.utils.data_model import MEASUREMENTS, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class RemoveDuplicatesTransformer(BaseEstimator, TransformerMixin):
    """
    Handles duplicate time points in measurement data.

    This transformer detects and resolves cases where multiple measurements
    exist for the same time point. Different strategies are available for
    handling these duplicates.

    Args:
        strategy: How to handle duplicate values:
            - 'mean': Use average of measurements (default)
            - 'first': Keep first occurrence
            - 'last': Keep last occurrence
            - 'min': Use minimum value
            - 'max': Use maximum value

    Example:
        >>> transformer = RemoveDuplicatesTransformer(strategy='mean')
        >>> processed = transformer.fit_transform(dataset)

    Note:
        Step indicators are always handled using 'first' strategy to
        maintain sequence integrity, regardless of chosen strategy.
    """

    VALID_STRATEGIES = Literal["mean", "first", "last", "min", "max"]

    def __init__(self, strategy: VALID_STRATEGIES = "mean"):
        self.strategy = strategy

    def fit(self, dataset: ScrewDataset, y=None):
        """Validate strategy and data structure."""
        if self.strategy not in ["mean", "first", "last", "min", "max"]:
            raise ValueError(
                f"Invalid strategy: {self.strategy}. "
                f"Must be one of: mean, first, last, min, max"
            )
        return self

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """Remove duplicate time points using selected strategy."""
        # TODO: Implement duplicate removal
        # 1. Find duplicate time points
        # 2. Apply strategy to consolidate measurements
        # 3. Handle step indicators appropriately
        # 4. Update processed_data structure
        logger.info(f"Removing duplicates using {self.strategy} strategy")
        return dataset
