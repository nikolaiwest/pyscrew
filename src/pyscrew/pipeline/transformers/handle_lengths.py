"""
Transformer for ensuring all measurement sequences have equal length.

This transformer processes the standardized measurement data to ensure all
sequences have the same length, using padding and truncation as needed.
It preserves all metadata fields while normalizing measurement data.

Key Features:
    - Supports both padding and truncation operations
    - Configurable padding value and position
    - Configurable truncation position
    - Preservation of all metadata fields
    - Maintains synchronization across different measurement types
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from pyscrew.config import PipelineConfig
from pyscrew.core import OutputFields, ScrewDataset
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
    It preserves all metadata fields during the transformation process.

    Args:
        config: PipelineConfig object containing processing settings
            The relevant fields are:
            - target_length: Desired length for all sequences
            - padding_value: Value to use when padding shorter sequences
            - padding_position: Where to add padding ('pre' or 'post')
            - cutoff_position: Where to truncate longer sequences ('pre' or 'post')

    Attributes:
        config: Configuration settings for the pipeline
        outputs: OutputFields instance for accessing standardized field names
        _stats: Statistics about length normalization
    """

    def __init__(self, config: PipelineConfig):
        """Initialize transformer with pipeline configuration."""
        self.config = config
        self.outputs = OutputFields()
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
        measurement_fields = [
            self.outputs.TIME_VALUES,
            self.outputs.TORQUE_VALUES,
            self.outputs.ANGLE_VALUES,
            self.outputs.GRADIENT_VALUES,
            self.outputs.STEP_VALUES,
        ]

        metadata_fields = [
            self.outputs.CLASS_VALUES,
            self.outputs.WORKPIECE_LOCATION,
            self.outputs.WORKPIECE_USAGE,
            self.outputs.WORKPIECE_RESULT,
            self.outputs.SCENARIO_CONDITION,
            self.outputs.SCENARIO_EXCEPTION,
        ]

        for k, v in cycle_values.items():
            if k in measurement_fields and k != self.outputs.CLASS_VALUES:
                truncated_sequences[k] = truncate_sequence(
                    v, self.config.target_length, self.config.cutoff_position
                )
            elif k in metadata_fields:
                # Do not modify metadata fields
                truncated_sequences[k] = v
            else:
                # For any other fields, preserve them unchanged
                truncated_sequences[k] = v

        # Determine final length from a measurement field
        for field in measurement_fields:
            if field in truncated_sequences:
                final_length = len(truncated_sequences[field])
                break
        else:
            final_length = initial_length  # No changes if no measurement fields found

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
        # Find length from first measurement field
        measurement_fields = [
            self.outputs.TIME_VALUES,
            self.outputs.TORQUE_VALUES,
            self.outputs.ANGLE_VALUES,
            self.outputs.GRADIENT_VALUES,
        ]

        for field in measurement_fields:
            if field in cycle_values:
                initial_length = len(cycle_values[field])
                break
        else:
            # No measurement fields found, return unchanged
            return cycle_values, 0, 0

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
        metadata_fields = [
            self.outputs.CLASS_VALUES,
            self.outputs.WORKPIECE_LOCATION,
            self.outputs.WORKPIECE_USAGE,
            self.outputs.WORKPIECE_RESULT,
            self.outputs.SCENARIO_CONDITION,
            self.outputs.SCENARIO_EXCEPTION,
        ]

        for k, v in cycle_values.items():
            if k == self.outputs.TIME_VALUES:
                # Time gets padded with incrementing values
                pad_len = self.config.target_length - len(v)
                if pad_len > 0:
                    last_time = v[-1]
                    padding = [
                        round(last_time + (i + 1) * 0.0012, 4) for i in range(pad_len)
                    ]
                    padded_sequences[k] = (
                        padding + v
                        if self.config.padding_position == "pre"
                        else v + padding
                    )
                else:
                    padded_sequences[k] = v
            elif k == self.outputs.STEP_VALUES:
                # Step padding simply adds a -1
                pad_len = self.config.target_length - len(v)
                if pad_len > 0:
                    padding = [-1] * pad_len
                    padded_sequences[k] = (
                        padding + v
                        if self.config.padding_position == "pre"
                        else v + padding
                    )
                else:
                    padded_sequences[k] = v
            elif k in metadata_fields:
                # Do not modify metadata fields
                padded_sequences[k] = v
            elif k in measurement_fields:
                # Apply padding to other measurements
                padded_sequences[k] = pad_sequence(
                    v,
                    self.config.target_length,
                    self.config.padding_value,
                    self.config.padding_position,
                )
            else:
                # For any other fields, preserve them unchanged
                padded_sequences[k] = v

        # Get the final length from a measurement field
        for field in measurement_fields:
            if field in padded_sequences:
                final_length = len(padded_sequences[field])
                break
        else:
            final_length = initial_length  # No changes if no measurement fields found

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
        # Find length from first measurement field
        measurement_fields = [
            self.outputs.TIME_VALUES,
            self.outputs.TORQUE_VALUES,
            self.outputs.ANGLE_VALUES,
            self.outputs.GRADIENT_VALUES,
        ]

        for field in measurement_fields:
            if field in cycle_values:
                initial_length = len(cycle_values[field])
                break
        else:
            # No measurement fields found, return unchanged
            return cycle_values, 0, 0

        if initial_length > self.config.target_length:
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
        sequences have the same length through padding or truncation,
        while preserving all metadata fields.

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
        # If target_length is None or 0, return dataset unchanged
        if not self.config.target_length:
            logger.info("Length normalization disabled (target_length=0)")
            return dataset

        logger.info("Starting to apply equal lengths.")
        logger.info(f"- 'target_length' : {self.config.target_length}")
        logger.info(f"- 'padding_value' : {self.config.padding_value}")
        logger.info(f"- 'padding_position' : {self.config.padding_position}")
        logger.info(f"- 'cutoff_position' : {self.config.cutoff_position}")

        # Verify consistent lengths within each run
        for field, data_list in dataset.processed_data.items():
            if not isinstance(data_list, list) or not data_list:
                continue

            # Skip metadata fields that have one value per run
            if field in [
                self.outputs.CLASS_VALUES,
                self.outputs.WORKPIECE_LOCATION,
                self.outputs.WORKPIECE_USAGE,
                self.outputs.WORKPIECE_RESULT,
                self.outputs.SCENARIO_CONDITION,
                self.outputs.SCENARIO_EXCEPTION,
            ]:
                continue

            # For measurement fields, check consistency within each run
            for i, run_data in enumerate(data_list):
                if not isinstance(run_data, list):
                    continue

                # Find a measurement field to compare against
                length_reference = None
                for ref_field in [
                    self.outputs.TIME_VALUES,
                    self.outputs.TORQUE_VALUES,
                    self.outputs.ANGLE_VALUES,
                    self.outputs.GRADIENT_VALUES,
                ]:
                    if (
                        ref_field in dataset.processed_data
                        and dataset.processed_data[ref_field]
                    ):
                        length_reference = len(dataset.processed_data[ref_field][i])
                        break

                if length_reference is not None and len(run_data) != length_reference:
                    raise ValueError(
                        f"Inconsistent lengths in run {i}: {field}={len(run_data)}, "
                        f"reference={length_reference}"
                    )

        # Initialize result storage
        transformed_data = {}

        # Copy all fields from the original dataset to preserve structure
        for key in dataset.processed_data.keys():
            transformed_data[key] = []

        initial_lengths = []
        final_lengths = []

        # Determine number of runs from a metadata field
        if self.outputs.CLASS_VALUES in dataset.processed_data:
            number_of_screw_runs = len(
                dataset.processed_data[self.outputs.CLASS_VALUES]
            )
        else:
            # Fall back to a measurement field
            for field in [
                self.outputs.TIME_VALUES,
                self.outputs.TORQUE_VALUES,
                self.outputs.ANGLE_VALUES,
                self.outputs.GRADIENT_VALUES,
            ]:
                if field in dataset.processed_data and dataset.processed_data[field]:
                    number_of_screw_runs = len(dataset.processed_data[field])
                    break
            else:
                # No valid fields found
                logger.warning("No valid data found for length normalization")
                return dataset

        # Process each screw cycle
        for i in range(number_of_screw_runs):
            # Extract single cycle data
            screw_run_at_index = {
                key: lst[i] if i < len(lst) else []
                for key, lst in dataset.processed_data.items()
                if isinstance(lst, list) and lst
            }

            # Apply length normalization
            equal_length_values, initial_len, final_len = self.apply_equal_length(
                screw_run_at_index
            )

            # Store results
            for k, v in equal_length_values.items():
                if k in transformed_data:
                    transformed_data[k].append(v)
                else:
                    transformed_data[k] = [v]

            initial_lengths.append(initial_len)
            final_lengths.append(final_len)

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
            f"- Total points before normalization:\t{stats.total_original_points:,}"
        )
        logger.info(
            f"- Total points after normalization:\t{stats.total_normalized_points:,}"
        )
