"""
Dataset conversion for final output formats.

This module provides transformer implementations for converting processed
screw dataset measurements into different output formats. It supports
conversion to various formats like lists, numpy arrays, and pandas DataFrames.

Key Features:
    - Multiple output format options (list, numpy, dataframe)
    - Metadata preservation
    - Measurement selection
    - Format-specific optimizations
    - Detailed validation and logging
"""

from typing import Dict, List, Literal, Optional, Union, Any
import copy

from sklearn.base import BaseEstimator, TransformerMixin

from pyscrew.core import JsonFields, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class ConversionError(Exception):
    """Raised when dataset conversion fails."""

    pass


class DatasetConversionTransformer(BaseEstimator, TransformerMixin):
    """Converts processed data to the requested output format.

    This transformer takes a ScrewDataset with processed measurements and
    converts them to the specified output format. It handles format-specific
    requirements and preserves metadata across conversions.

    Args:
        output_format: Target format for conversion
            - 'list': Nested Python lists (default)
            - 'numpy': NumPy arrays
            - 'dataframe': Pandas DataFrame
        measurements: List of measurements to include (None means all)
        include_metadata: Whether to include metadata in output

    Attributes:
        output_format: Current output format
        measurements: Selected measurements
        include_metadata: Metadata inclusion flag
        _stats: Statistics about the conversion process

    Example:
        >>> # Initialize transformer for DataFrame output
        >>> transformer = DatasetConversionTransformer(output_format='dataframe')
        >>>
        >>> # Convert dataset
        >>> converted = transformer.fit_transform(dataset)
        >>>
        >>> # Access data (now a DataFrame)
        >>> df = converted.processed_data

    Raises:
        ConversionError: If conversion fails due to missing dependencies or data issues
        ValueError: If an invalid format is specified
    """

    VALID_FORMATS = Literal["list", "numpy", "dataframe"]

    def __init__(
        self,
        output_format: VALID_FORMATS = "list",
        measurements: Optional[List[str]] = None,
        include_metadata: bool = True,
    ) -> None:
        """Initialize the dataset conversion transformer.

        Args:
            output_format: Target format for data conversion
            measurements: List of measurements to include (None for all)
            include_metadata: Whether to include metadata in output
        """
        self.output_format = output_format
        self.measurements = measurements
        self.include_metadata = include_metadata
        self._conversion_stats = {
            "format": output_format,
            "measurements_included": 0,
            "data_points_processed": 0,
        }

    def fit(self, dataset: ScrewDataset, y=None) -> "DatasetConversionTransformer":
        """Validate conversion parameters and data compatibility.

        Args:
            dataset: Input dataset to validate
            y: Ignored, exists for scikit-learn compatibility

        Returns:
            self: This transformer instance

        Raises:
            ValueError: If format is invalid
            ConversionError: If required dependencies are missing
        """
        if self.output_format not in ["list", "numpy", "dataframe"]:
            raise ValueError(
                f"Invalid output format: {self.output_format}. "
                f"Must be one of: list, numpy, dataframe"
            )

        # Check for required dependencies based on format
        if self.output_format == "numpy":
            try:
                import numpy as np  # noqa
            except ImportError:
                raise ConversionError(
                    "NumPy is required for 'numpy' output format but not installed"
                )
        elif self.output_format == "dataframe":
            try:
                import pandas as pd  # noqa
                import numpy as np  # noqa
            except ImportError:
                raise ConversionError(
                    "Pandas and NumPy are required for 'dataframe' output format but not installed"
                )

        return self

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """Transform the dataset to the requested output format.

        Args:
            dataset: Input dataset with processed measurements

        Returns:
            Transformed dataset with converted data

        Raises:
            ConversionError: If conversion fails
        """
        try:
            # Make a copy to avoid modifying the original
            processed_data = copy.deepcopy(dataset.processed_data)

            # Filter measurements if specified
            if self.measurements:
                fields_to_keep = []
                for field in self.measurements:
                    if field in processed_data:
                        fields_to_keep.append(field)
                    else:
                        logger.warning(
                            f"Requested measurement '{field}' not found in dataset"
                        )

                # Always keep class labels if present
                if JsonFields.Measurements.CLASS in processed_data:
                    fields_to_keep.append(JsonFields.Measurements.CLASS)

                # Filter to keep only requested measurements
                processed_data = {
                    k: v for k, v in processed_data.items() if k in fields_to_keep
                }

            self._conversion_stats["measurements_included"] = len(processed_data)

            # Count total data points
            if JsonFields.Measurements.TIME in processed_data:
                for time_series in processed_data[JsonFields.Measurements.TIME]:
                    self._conversion_stats["data_points_processed"] += len(time_series)

            # Extract metadata if present
            metadata = None
            if "metadata" in processed_data:
                metadata = processed_data.pop("metadata")

            # Convert to requested format
            converted_data = self._convert_to_format(
                processed_data, self.output_format, dataset
            )

            # Add metadata back if requested
            if self.include_metadata and metadata:
                if self.output_format == "dataframe":
                    # For DataFrame, add as attributes
                    converted_data.attrs = metadata
                else:
                    # For other formats, add as a separate key
                    converted_data["metadata"] = metadata

            # Log conversion results
            self._log_conversion_summary()

            # Update dataset with converted data
            dataset.processed_data = converted_data
            return dataset

        except Exception as e:
            logger.error(f"Failed to convert dataset: {str(e)}")
            raise ConversionError(f"Dataset conversion failed: {str(e)}") from e

    def _convert_to_format(
        self, data: Dict[str, List], format_name: str, dataset: ScrewDataset
    ) -> Any:
        """Convert data to the specified format.

        Args:
            data: Dictionary of measurement data
            format_name: Target format name
            dataset: Original dataset (for metadata)

        Returns:
            Converted data in requested format

        Raises:
            ConversionError: If conversion fails
        """
        if format_name == "list":
            # Already in list format, nothing to do
            return data

        elif format_name == "numpy":
            try:
                import numpy as np

                # Convert all values to numpy arrays
                numpy_data = {}
                for key, value in data.items():
                    numpy_data[key] = np.array(value)

                logger.info(f"Converted data to NumPy arrays")
                return numpy_data

            except Exception as e:
                raise ConversionError(
                    f"Failed to convert to NumPy format: {str(e)}"
                ) from e

        elif format_name == "dataframe":
            try:
                import pandas as pd
                import numpy as np

                # For DataFrame, we need to restructure the data
                # First, check if all series have the same length
                series_lengths = {}
                for key, series_list in data.items():
                    if key != JsonFields.Measurements.CLASS:  # Skip class labels
                        series_lengths[key] = [len(series) for series in series_list]

                # Check if all measurements have the same structure
                keys = list(series_lengths.keys())
                if not all(
                    series_lengths[keys[0]] == series_lengths[key] for key in keys[1:]
                ):
                    logger.warning(
                        "Measurements have different lengths, DataFrame creation may not be ideal"
                    )

                # Create a DataFrame with multiindex
                # Level 0: Series index, Level 1: Measurement type
                dfs = []

                # Get number of series
                if JsonFields.Measurements.TIME in data:
                    num_series = len(data[JsonFields.Measurements.TIME])
                else:
                    # Fallback to first available measurement
                    num_series = len(next(iter(data.values())))

                # Process each series
                for i in range(num_series):
                    series_data = {}
                    for key, series_list in data.items():
                        if (
                            key != JsonFields.Measurements.CLASS
                        ):  # Process class separately
                            if i < len(series_list):
                                series_data[key] = series_list[i]
                            else:
                                logger.warning(
                                    f"Series {i} missing for measurement {key}"
                                )
                                series_data[key] = []

                    # Create DataFrame for this series
                    df = pd.DataFrame(series_data)

                    # Add class label if available
                    if JsonFields.Measurements.CLASS in data and i < len(
                        data[JsonFields.Measurements.CLASS]
                    ):
                        class_value = data[JsonFields.Measurements.CLASS][i]
                        df["class"] = class_value

                    # Add series index
                    df["series"] = i
                    dfs.append(df)

                # Combine all series
                if dfs:
                    combined_df = pd.concat(dfs, ignore_index=True)
                    logger.info(
                        f"Converted data to DataFrame with {len(combined_df)} rows"
                    )
                    return combined_df
                else:
                    logger.warning("No data to convert to DataFrame")
                    return pd.DataFrame()

            except Exception as e:
                raise ConversionError(
                    f"Failed to convert to DataFrame format: {str(e)}"
                ) from e

        else:
            raise ConversionError(f"Unsupported format: {format_name}")

    def _log_conversion_summary(self) -> None:
        """Log summary statistics of the conversion process."""
        stats = self._conversion_stats

        logger.info(f"Completed conversion to '{stats['format']}' format")
        logger.info(f"Included {stats['measurements_included']} measurement types")
        logger.info(f"Processed {stats['data_points_processed']:,} total data points")
