"""
Transformer for ensuring all measurement sequences have equal length.

This transformer handles variable-length measurement sequences by either
padding shorter sequences or truncating longer ones to reach a target length.
It's particularly useful for preparing data for machine learning models that
require fixed-length inputs.

Key Features:
- Supports both padding and truncation operations
- Configurable padding value and position
- Configurable truncation position
- Maintains synchronization across different measurement types

Attributes:
    target_length (int): Desired length for all sequences
    padding_value (float): Value to use for padding shorter sequences (default: 0.0)
    padding_position (str): Position to add padding ('pre' or 'post', default: 'post')
    cutoff_position (str): Position to truncate ('pre' or 'post', default: 'post')

Example:
    ```python
    transformer = HandleLengthsTransformer(
        target_length=1000,
        padding_value=0.0,
        padding_position='post',
        cutoff_position='post'
    )
    normalized_data = transformer.transform(screw_data)
    ```
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from pyscrew.core import JsonFields, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LengthNormalizationStats:
    """Statistics about length normalization processing.

    Attributes:
        total_series: Number of time series processed
        total_original_points: Total points before normalization
        total_normalized_points: Total points after normalization
        avg_initial_length: Average initial length of sequences
        avg_final_length: Average final length of sequences
    """

    total_series: int = 0
    total_original_points: int = 0
    total_normalized_points: int = 0
    avg_initial_length: float = 0.0
    avg_final_length: float = 0.0


class HandleLengthsTransformer(BaseEstimator, TransformerMixin):
    """
    Transformer for ensuring all measurement sequences have equal length.

    This transformer handles variable-length measurement sequences by either
    padding shorter sequences or truncating longer ones to reach a target length.
    It's particularly useful for preparing data for machine learning models that
    require fixed-length inputs.

    Args:
        target_length: Desired length for all sequences
        padding_value: Value to use when padding shorter sequences
        padding_position: Where to add padding ('pre' or 'post')
        cutoff_position: Where to truncate longer sequences ('pre' or 'post')
    """

    def __init__(
        self,
        target_length: int,
        padding_value: float = 0.0,
        padding_position: str = "post",
        cutoff_position: str = "post",
    ):
        self.target_length = target_length
        self.padding_value = padding_value
        self.padding_position = padding_position
        self.cutoff_position = cutoff_position
        self._stats = LengthNormalizationStats()

    def fit(self, X: ScrewDataset, y: Any = None) -> "HandleLengthsTransformer":
        """Fit method for compatibility with scikit-learn Pipeline."""
        return self

    def apply_truncating(
        self, cycle_values: Dict[str, List[Any]]
    ) -> Tuple[Dict[str, List[Any]], int, int]:
        """
        Truncate sequences that are longer than the target length.

        Process:
        1. Identify initial sequence length
        2. Truncate each sequence based on cutoff position
        3. Track the length changes

        Args:
            cycle_values: Dictionary of measurement sequences for one cycle

        Returns:
            Tuple containing:
            - Dictionary of truncated sequences
            - Original length
            - New length
        """
        initial_length = len(next(iter(cycle_values.values())))

        def truncate_sequence(
            seq: List[Any], target_length: int, cutoff_position: str
        ) -> List[Any]:
            """Helper function to truncate a single sequence."""
            if cutoff_position == "pre":
                return seq[-target_length:]  # Keep last target_length elements
            else:
                return seq[:target_length]  # Keep first target_length elements

        truncated_sequences = {}

        for k, v in cycle_values.items():
            if k == JsonFields.Measurements.TIME:
                truncated_sequences[k] = truncate_sequence(
                    v, self.target_length, self.cutoff_position
                )
            elif k == JsonFields.Measurements.STEP:
                truncated_sequences[k] = truncate_sequence(
                    v, self.target_length, self.cutoff_position
                )
            elif k == JsonFields.Measurements.CLASS:
                truncated_sequences[k] = v  # Do not change class values
            else:
                truncated_sequences[k] = truncate_sequence(
                    v, self.target_length, self.cutoff_position
                )

        final_length = len(next(iter(truncated_sequences.values())))
        return truncated_sequences, initial_length, final_length

    def apply_padding(
        self, cycle_values: Dict[str, List[Any]]
    ) -> Tuple[Dict[str, List[Any]], int, int]:
        """
        Pad sequences that are shorter than the target length.

        Process:
        1. Identify initial sequence length
        2. Pad each sequence based on padding position
        3. Track the length changes

        Args:
            cycle_values: Dictionary of measurement sequences for one cycle

        Returns:
            Tuple containing:
            - Dictionary of padded sequences
            - Original length
            - New length
        """
        initial_length = len(next(iter(cycle_values.values())))

        def pad_sequence(
            seq: List[Any],
            target_length: int,
            padding_value: float,
            padding_position: str,
        ) -> List[Any]:
            """Helper function to pad a single sequence."""
            pad_len = target_length - len(seq)
            padding = [padding_value] * pad_len
            return padding + seq if padding_position == "pre" else seq + padding

        padded_sequences = {}
        for k, v in cycle_values.items():
            if k == JsonFields.Measurements.TIME:
                # Time gets padded with incrementing values
                pad_len = self.target_length - len(v)
                last_time = v[-1]
                padding = [
                    round(last_time + (i + 1) * 0.0012, 4) for i in range(pad_len)
                ]
                padded_sequences[k] = (
                    padding + v if self.padding_position == "pre" else v + padding
                )
            elif k == JsonFields.Measurements.STEP:
                # Step padding simply adds a -1 to
                pad_len = self.target_length - len(v)
                padding = [-1] * pad_len
                padded_sequences[k] = (
                    padding + v if self.padding_position == "pre" else v + padding
                )
            elif k == JsonFields.Measurements.CLASS:
                # Class values remain unchanged
                padded_sequences[k] = v
            else:
                # Apply padding to other measurements
                padded_sequences[k] = pad_sequence(
                    v, self.target_length, self.padding_value, self.padding_position
                )

        final_length = len(next(iter(padded_sequences.values())))
        return padded_sequences, initial_length, final_length

    def apply_equal_length(
        self, cycle_values: Dict[str, List[Any]]
    ) -> Tuple[Dict[str, List[Any]], int, int]:
        """
        Apply appropriate length normalization based on sequence length.

        This method decides whether to pad or truncate based on the comparison
        between current length and target length.

        Args:
            cycle_values: Dictionary of measurement sequences for one cycle

        Returns:
            Tuple containing:
            - Dictionary of normalized sequences
            - Original length
            - New length
        """
        initial_length = len(next(iter(cycle_values.values())))

        if initial_length > self.target_length:
            equal_length_values, initial_length, final_length = self.apply_truncating(
                cycle_values
            )
        else:
            equal_length_values, initial_length, final_length = self.apply_padding(
                cycle_values
            )

        return equal_length_values, initial_length, final_length

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """
        Transform variable-length sequences to have equal length.

        This method processes multiple screw cycles to ensure all measurement
        sequences have the same length through padding or truncation.

        Process:
        1. Verify data consistency
        2. Process each cycle independently
        3. Track length changes
        4. Log transformation statistics

        Args:
            dataset: Input dataset containing lists of measurements for multiple
                screw cycles

        Returns:
            Dataset with length-normalized measurements

        Raises:
            ValueError: If measurement lists have inconsistent lengths
        """
        logger.info("Starting to apply equal lengths.")
        logger.info(f"- 'target_length' : {self.target_length}")
        logger.info(f"- 'padding_value' : {self.padding_value}")
        logger.info(f"- 'padding_position' : {self.padding_position}")
        logger.info(f"- 'cutoff_position' : {self.cutoff_position}")

        # Verify consistent lengths across measurements
        number_of_screw_runs = len(dataset.processed_data[JsonFields.Measurements.TIME])
        if not all(
            len(lst) == number_of_screw_runs
            for lst in dataset.processed_data.values()
            if isinstance(lst, list)
        ):
            raise ValueError(
                "All recordings for one screw run must have the same length"
            )

        # Initialize result storage
        transformed_data = {key: [] for key in dataset.processed_data.keys()}
        initial_lengths = []
        final_lengths = []

        # Process each screw cycle
        for i in range(number_of_screw_runs):
            # Extract single cycle data
            screw_run_at_index = {
                key: lst[i] for key, lst in dataset.processed_data.items()
            }

            # Apply length normalization
            equal_length_values, initial_len, final_len = self.apply_equal_length(
                screw_run_at_index
            )

            # Store results
            for k, v in equal_length_values.items():
                transformed_data[k].append(v)
            initial_lengths.append(initial_len)
            final_lengths.append(final_len)

        # Handle step values separately to pad with -1
        if JsonFields.Measurements.STEP in dataset.processed_data:
            for i in range(number_of_screw_runs):
                step_values = dataset.processed_data[JsonFields.Measurements.STEP][i]
                if len(step_values) < self.target_length:
                    pad_len = self.target_length - len(step_values)
                    padding = [-1] * pad_len
                    if self.padding_position == "pre":
                        step_values = padding + step_values
                    else:
                        step_values = step_values + padding
                transformed_data[JsonFields.Measurements.STEP].append(step_values)

        # Ensure class values remain unchanged
        if JsonFields.Measurements.CLASS in dataset.processed_data:
            transformed_data[JsonFields.Measurements.CLASS] = dataset.processed_data[
                JsonFields.Measurements.CLASS
            ]

        # Update statistics
        self._stats.total_series = number_of_screw_runs
        self._stats.total_original_points = sum(initial_lengths)
        self._stats.total_normalized_points = sum(final_lengths)
        self._stats.avg_initial_length = np.mean(initial_lengths)
        self._stats.avg_final_length = np.mean(final_lengths)

        # Log transformation summary
        self._log_summary()

        dataset.processed_data = transformed_data
        return dataset

    def _log_summary(self) -> None:
        """Log summary statistics of length normalization processing."""
        stats = self._stats

        logger.info("Finished applying equal lengths to the screw driving data.")
        logger.info(f"- Total screw runs loaded:\t{stats.total_series}")
        logger.info(
            f"- Average change of length:\t{stats.avg_initial_length:.2f} -> {stats.avg_final_length:.2f}"
        )
        logger.info(
            f"- Total points before normalization:\t{stats.total_original_points}"
        )
        logger.info(
            f"- Total points after normalization:\t{stats.total_normalized_points}"
        )
