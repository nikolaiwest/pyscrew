"""
Transformer for creating equidistant time series through interpolation.

This module provides transformer implementations for converting irregular time series
into equidistant measurements through interpolation. It handles multiple measurement
types and maintains data integrity throughout the process.

Key Features:
    - Linear interpolation to create regular time intervals
    - Multiple interpolation methods (mean, zero, custom value)
    - Handles multiple measurement types (torque, angle, gradient)
    - Special handling for step indicators
    - Detailed statistics tracking
    - Comprehensive input validation
"""

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from numpy.typing import NDArray
from sklearn.base import BaseEstimator, TransformerMixin
from tqdm import tqdm

from pyscrew.config import PipelineConfig
from pyscrew.core import JsonFields, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class InterpolationStats:
    """Statistics about interpolation processing.

    Attributes:
        total_series: Number of time series processed
        total_original_points: Total points before interpolation
        total_interpolated_points: Total points after interpolation
        min_time_gap: Minimum time gap in original data
        max_time_gap: Maximum time gap in original data
        avg_time_gap: Average time gap in original data
    """

    total_series: int = 0
    total_original_points: int = 0
    total_interpolated_points: int = 0
    min_time_gap: float = float("inf")
    max_time_gap: float = 0.0
    avg_time_gap: float = 0.0


class ProcessingError(Exception):
    """Raised when interpolation processing fails."""

    pass


class HandleMissingsTransformer(BaseEstimator, TransformerMixin):
    """Creates equidistant time series through interpolation.

    This transformer ensures that measurements are available at regular time
    intervals by performing interpolation between existing points.
    It handles all measurement types appropriately, including special handling
    for step indicators.

    Args:
        config: PipelineConfig object containing processing settings
            The config.handle_missings field determines how to handle missing values:
            - 'mean': Use linear interpolation (default)
            - 'zero': Fill gaps with zeros
            - float value: Fill gaps with specified value
            - None: Skip interpolation entirely

    Attributes:
        config: Configuration settings for the pipeline
        target_interval: Time interval for interpolation (0.0012s by default)
        decimal_places: Number of decimal places for rounding (4 by default)
        _stats: Statistics about processed interpolations

    Example:
        >>> # Initialize transformer with pipeline config
        >>> transformer = HandleMissingsTransformer(config)
        >>>
        >>> # Process dataset
        >>> processed = transformer.fit_transform(dataset)
        >>>
        >>> # Check statistics
        >>> print(f"Processed {transformer._stats.total_series} series")
        >>> print(f"Added {transformer._stats.total_interpolated_points - transformer._stats.total_original_points} points")

    Raises:
        ProcessingError: If processing fails due to invalid data
        ValueError: If invalid parameters are specified
    """

    def __init__(self, config: PipelineConfig) -> None:
        """Initialize transformer with pipeline configuration."""
        self.config = config
        self.target_interval = 0.0012  # Standard time interval in seconds
        self.decimal_places = 4  # Ideal number of decimal places when rounding
        self._stats = InterpolationStats()

    def _validate_arrays(
        self, time: NDArray[np.float64], values: Dict[str, NDArray[np.float64]]
    ) -> None:
        """Validate input arrays before processing.

        Args:
            time: Time measurements
            values: Dictionary of measurement arrays

        Raises:
            ProcessingError: If validation fails
        """
        length = len(time)

        # Check array lengths
        if not all(len(arr) == length for arr in values.values()):
            raise ProcessingError(
                f"Inconsistent array lengths: {[len(arr) for arr in values.values()]}"
            )

        # Check for NaN/inf values
        if not np.isfinite(time).all():
            raise ProcessingError("Found NaN or infinite values in time array")

        for name, arr in values.items():
            if not np.isfinite(arr).all():
                raise ProcessingError(f"Found NaN or infinite values in {name}")

        # Validate time sequence
        if not np.all(np.diff(time) >= 0):
            raise ProcessingError("Time values must be strictly increasing")

    def _compute_time_stats(self, time: NDArray[np.float64]) -> None:
        """Update time gap statistics.

        Args:
            time: Array of time measurements
        """
        gaps = np.diff(time)
        self._stats.min_time_gap = min(self._stats.min_time_gap, np.min(gaps))
        self._stats.max_time_gap = max(self._stats.max_time_gap, np.max(gaps))
        self._stats.avg_time_gap = np.mean(gaps)

    def _interpolate_values(
        self,
        time_original: NDArray[np.float64],
        time_target: NDArray[np.float64],
        values: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        # Convert inputs to numpy arrays if they aren't already
        time_original_arr = np.array(time_original)
        time_target_arr = np.array(time_target)
        values_arr = np.array(values)

        if self.config.handle_missings == "mean":
            # Simply perform linear interpolation for all cases
            return np.interp(time_target_arr, time_original_arr, values_arr)

        elif self.config.handle_missings == "zero":
            result = np.zeros_like(time_target_arr)

            # Use isclose() with appropriate tolerances
            matches = np.isclose(
                time_target_arr.reshape(-1, 1),
                time_original_arr,
                rtol=1e-09,  # Relative tolerance
                atol=1e-12,  # Absolute tolerance
            )
            match_indices = np.where(matches.any(axis=1))[0]
            orig_indices = np.where(matches[match_indices])[1]

            result[match_indices] = values_arr[orig_indices]
            return result

        else:
            try:
                fill_value = float(self.config.handle_missings)
                result = np.full_like(time_target_arr, fill_value)

                matches = np.isclose(
                    time_target_arr.reshape(-1, 1),
                    time_original_arr,
                    rtol=1e-09,
                    atol=1e-12,
                )
                match_indices = np.where(matches.any(axis=1))[0]
                orig_indices = np.where(matches[match_indices])[1]

                result[match_indices] = values_arr[orig_indices]
                return result

            except (TypeError, ValueError) as e:
                raise ProcessingError(
                    f"Invalid handle_missings value: {self.config.handle_missings}"
                ) from e

    def _to_float_list(self, values: NDArray[np.float64]) -> List[float]:
        """Convert numpy array to list of Python floats with rounding.

        Args:
            values: Array to convert

        Returns:
            List of rounded float values
        """
        return [float(round(x, self.decimal_places)) for x in values]

    def fit(self, dataset: ScrewDataset, y=None) -> "HandleMissingsTransformer":
        """Validate interpolation parameters and data structure.

        Args:
            dataset: Input dataset to validate
            y: Ignored, exists for scikit-learn compatibility

        Returns:
            self: This transformer instance

        Raises:
            ValueError: If parameters are invalid
        """
        if self.target_interval <= 0:
            raise ValueError("target_interval must be positive")
        if self.decimal_places < 0:
            raise ValueError("decimal_places must be non-negative")
        if not dataset.get_values(JsonFields.Measurements.TIME):
            raise ValueError("Dataset must contain time values")

        # Validate config.handle_missings
        if self.config.handle_missings not in ["mean", "zero", None]:
            try:
                float(self.config.handle_missings)
            except (TypeError, ValueError):
                raise ValueError(
                    "handle_missings must be 'mean', 'zero', a float value, or None"
                )

        return self

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """Transform the dataset by interpolating to regular intervals.

        If config.handle_missings is None, returns the dataset unchanged.
        Otherwise, processes the dataset to interpolate missing values.

        Args:
            dataset: Input dataset to transform

        Returns:
            Transformed dataset with regular intervals

        Raises:
            ProcessingError: If transformation fails
        """
        # If no interpolation is configured, return dataset unchanged
        if self.config.handle_missings is None:
            logger.info("Missing value handling disabled (handle_missings=None)")
            return dataset

        # Reset statistics
        self._stats = InterpolationStats()

        # Initialize processed data structure
        processed_data = {
            JsonFields.Measurements.TIME: [],
            JsonFields.Measurements.TORQUE: [],
            JsonFields.Measurements.ANGLE: [],
            JsonFields.Measurements.GRADIENT: [],
        }

        # Include step field if it exists in input
        if JsonFields.Measurements.STEP in dataset.processed_data:
            processed_data[JsonFields.Measurements.STEP] = []

        # Include class_value if it exists in input
        if JsonFields.Measurements.CLASS in dataset.processed_data:
            processed_data[JsonFields.Measurements.CLASS] = dataset.processed_data[
                JsonFields.Measurements.CLASS
            ]

        try:
            # Process each run
            time_series = dataset.processed_data[JsonFields.Measurements.TIME]
            self._stats.total_series = len(time_series)

            for idx in tqdm(
                range(self._stats.total_series),
                desc="Interpolating missing values",
                leave=False,
            ):
                time_values = np.array(time_series[idx])
                # Round end point to match our decimal places
                end_time = time_values[-1]
                time_values_ideal = np.arange(
                    0,
                    end_time + self.target_interval,
                    self.target_interval,
                )
                time_values_ideal = [
                    round(x, self.decimal_places) for x in time_values_ideal
                ]
                # Prepare measurement arrays
                measurements = {
                    JsonFields.Measurements.TORQUE: np.array(
                        dataset.processed_data[JsonFields.Measurements.TORQUE][idx]
                    ),
                    JsonFields.Measurements.ANGLE: np.array(
                        dataset.processed_data[JsonFields.Measurements.ANGLE][idx]
                    ),
                    JsonFields.Measurements.GRADIENT: np.array(
                        dataset.processed_data[JsonFields.Measurements.GRADIENT][idx]
                    ),
                }

                # Validate arrays
                self._validate_arrays(time_values, measurements)

                # Update statistics
                self._stats.total_original_points += len(time_values)
                self._stats.total_interpolated_points += len(time_values_ideal)
                self._compute_time_stats(time_values)

                # Store interpolated time values
                processed_data[JsonFields.Measurements.TIME].append(
                    self._to_float_list(time_values_ideal)
                )

                # Interpolate each measurement
                for measurement, values in measurements.items():
                    interpolated = self._interpolate_values(
                        time_values, time_values_ideal, values
                    )
                    processed_data[measurement].append(
                        self._to_float_list(interpolated)
                    )

                # Handle step values if they exist (always use 'first' method)
                if JsonFields.Measurements.STEP in dataset.processed_data:
                    step_values = np.array(
                        dataset.processed_data[JsonFields.Measurements.STEP][idx]
                    )
                    interpolated = np.interp(
                        time_values_ideal, time_values, step_values
                    )
                    processed_data[JsonFields.Measurements.STEP].append(
                        [int(x) for x in np.round(interpolated)]
                    )

            # Log summary statistics
            self._log_summary()

            # Update dataset and return
            dataset.processed_data = processed_data
            return dataset

        except Exception as e:
            raise ProcessingError(f"Failed to transform dataset: {str(e)}") from e

    def _log_summary(self) -> None:
        """Log summary statistics of interpolation processing."""
        stats = self._stats

        # Calculate statistics
        points_ratio = (
            stats.total_interpolated_points - stats.total_original_points
        ) / stats.total_original_points
        points_per_series = (
            stats.total_interpolated_points - stats.total_original_points
        ) / stats.total_series

        logger.info(
            f"Completed missing interpolation using '{self.config.handle_missings}' method (interval={self.target_interval:.4f})"
        )
        logger.info(
            f"Processed {stats.total_series:,} series with {stats.total_original_points:,} total points"
        )
        logger.info(
            f"Found gaps - min: {stats.min_time_gap:.4f}s, max: {stats.max_time_gap:.4f}s, avg: {stats.avg_time_gap:.4f}s"
        )
        logger.info(
            f"Added {stats.total_interpolated_points-stats.total_original_points:,} points (+{points_ratio*100:.2f}% of total)"
        )
        logger.info(f"Average {points_per_series:.1f} points added per series")
