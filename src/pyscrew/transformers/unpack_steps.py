"""
Transformer for unpacking raw screw step data into organized measurements.
"""

from sklearn.base import BaseEstimator, TransformerMixin

from pyscrew.utils.data_model import MEASUREMENTS, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class UnpackStepsTransformer(BaseEstimator, TransformerMixin):
    """
    Unpacks raw screw step data into organized measurement collections.

    This transformer takes the raw step-based data from ScrewDataset
    and organizes it into measurement-based collections in processed_data.
    It handles time, torque, angle, and gradient measurements, optionally
    including step indicators.

    Args:
        include_steps: Whether to include step indicators in output

    Example:
        >>> transformer = UnpackStepsTransformer(include_steps=True)
        >>> processed = transformer.fit_transform(dataset)
        >>> print(processed.processed_data.keys())
        ['time', 'torque', 'angle', 'gradient', 'step']
    """

    def __init__(self, include_steps: bool = True):
        self.include_steps = include_steps

    def fit(self, dataset: ScrewDataset, y=None):
        """Nothing to fit, implements interface."""
        return self

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """Transform step-based data into measurement collections."""
        # Initialize measurement lists
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

        # Process runs and steps
        for run_idx, run in enumerate(dataset.screw_runs):
            for step_idx, step in enumerate(run.steps):
                step_length = len(step.get_values(MEASUREMENTS.TIME))

                # Process measurements
                for measurement in measurements:
                    values = step.get_values(measurement)
                    dataset.processed_data[measurement][run_idx].extend(values)

                # Add step indicators if requested
                if self.include_steps:
                    dataset.processed_data[MEASUREMENTS.STEP][run_idx].extend(
                        [step_idx] * step_length
                    )

        return dataset
