from pathlib import Path
from typing import Dict, List

from pyscrew.conversion import convert_data
from pyscrew.loading import DatasetRegistry, load_data
from pyscrew.processing import process_data
from pyscrew.utils import ConfigSchema, get_logger
from pyscrew.utils.data_model import ScrewDataset
from pyscrew.validation import (
    validate_converted_data,
    validate_loaded_data,
    validate_processed_data,
)

# 1. User selects a scenario and config

# select by scenario (s01, s02, etc.) via scenario_name
# select by label (default all labels, accept list to limit selection from scenario)
# select by cycle (default all cycles, accept list to limit selection from scenario)
# select by workpiece_location/side (left or right, default both)
# --> list of file names (with cache path to load in json/)

# 2. Load data from list of file names

# ScrewRun and ScrewStep objects from file_names

# list of ScrewRun objects in slearn pipeline
# Transformers to build:
# * remove negative values (only torque, OPTIONAL, default=False)
# * apply equal distance (0.0012 for time, all other have to be interpolated: torque, angle, gradient)
# * equal length (mandatory for np, pd, tf; optional then nested lists) --> maybe np default, rest future stuff


# future feature list:
# select by screw phase (default all four, accept list to limit selection from scenario): get individual screw phases as nested lists (default False)
# aggregation method (default None, accept intervall lengtht or total length)


# Initialize logger for this module
logger = get_logger(__name__)


# Custom exception hierarchy for clear error handling
class PyScewError(Exception):
    """Base exception class for PyScrew errors"""

    pass


class DataNotFoundError(PyScewError):
    """Raised when scenario data cannot be found"""

    pass


class ValidationError(PyScewError):
    """Raised when data validation fails"""

    pass


class ProcessingError(PyScewError):
    """Raised when data processing fails"""

    pass


class ConversionError(PyScewError):
    """Raised when data conversion fails"""

    pass


def list_scenarios() -> Dict[str, str]:
    """
    List all available scenarios and their descriptions.

    Returns:
        Dictionary mapping scenario names to their descriptions

    Example:
        >>> scenarios = list_scenarios()
        >>> print(scenarios)
        {
            'thread-degradation': 'Dataset for thread degradation analysis',
            'other-scenario': 'Description of other scenario'
        }
    """
    try:
        # Get all datasets through the proper getter method
        datasets = DatasetRegistry.get_datasets()

        # Create description dictionary using the DatasetConfig objects
        return {name: config.description for name, config in datasets.items()}
    except Exception as e:
        logger.error(f"Error listing scenarios: {str(e)}")
        raise


def get_data(
    scenario_name: str,
    *,
    # Filtering options
    scenario_classes: list[str] | None = None,
    return_measurements: list[str] | None = None,
    screw_phase: list[int] | None = None,
    screw_cycles: list[int] | None = None,
    screw_positions: str = "both",
    # Processing options
    handle_duplicates: str = "first",
    handle_missings: str = "mean",
    output_format: str = "numpy",
    # System options
    cache_dir: str | Path | None = None,
    force_download: bool = False,
) -> Dict[str, List[float]]:
    """Load and process screw driving data from a specific scenario.

    Args:
        scenario_name: Name of the scenario to load
        scenario_classes: List of scenario classes to include. None means "all"
        return_measurements: List of measurements to return. Options are ["torque", "angle", "gradient", "time"].
            None means "all measurements"
        screw_phase: List of screw phases to include. Options are [1,2,3,4]. None means "all phases"
        screw_cycles: List of cycle numbers to include. None means "all cycles"
        screw_position: Position to analyze. Options are ["left", "right" or "both"]
        handle_duplicates: How to remove negative values and what to keep. Options are ["first", "last", "mean", None].
            None means no duplactes are removed.
        handle_missings: Whether to interpolate missing values. Options are ["mean", "zeor" or a float value]
            Time is recorded at 0.0012s intervals. None means no values are interpolated.
        output_format: Format of the output data. Options are "numpy", "dataframe" or "list"
        cache_dir: Directory for caching downloaded data
        force_download: Force re-download even if cached

    Returns:
        Processed data in the requested format

    Examples:
        >>> # Get all data for a scenario
        >>> data = get_data("thread-degradation")

        >>> # Get specific measurements for certain phases
        >>> data = get_data(
        ...     "thread-degradation",
        ...     return_measurements=["torque", "angle"],
        ...     screw_phase=[1, 2],
        ...     output_format="dataframe"
        ... )
    """
    logger.info(f"Starting data retrieval for scenario: {scenario_name}")

    # Convert inputs to config schema
    config = ConfigSchema(
        scenario_name=scenario_name,
        scenario_classes=scenario_classes,
        measurements=return_measurements,
        screw_phase=screw_phase,
        screw_cycles=screw_cycles,
        screw_positions=screw_positions,
        handle_duplicates=handle_duplicates,
        handle_missings=handle_missings,
        output_format=output_format,
        cache_dir=Path(cache_dir) if cache_dir else None,
        force_download=force_download,
    )

    try:
        # Step 1: Get raw data path and download if needed
        # load_data() from loading.py should:
        # - Check if data exists in cache_dir
        # - If not or if force=True, download from Zenodo
        # - Extract to cache_dir
        # - Return path to extracted data
        logger.debug("Loading raw data")
        data_path = load_data(config)

        # Step 2: Validate raw data structure
        # validate_loaded_data() from validation.py should:
        # - Check if all expected files exist
        # - Verify basic file structure/format
        # - Raise ValidationError if checks fail
        logger.debug("Validating raw data")
        try:
            validate_loaded_data(data_path, config)
        except Exception as e:
            raise ValidationError(f"Raw data validation failed: {e}")

        # Step 3: Process the data according to config
        # process_data() from processing.py should:
        # - Read the raw data
        # - Apply transformations based on config
        # - Return data in memory (not on disk)
        logger.debug(f"Processing data with config: {config.model_dump()}")
        try:
            data = process_data(data_path, config)
        except Exception as e:
            raise ProcessingError(f"Data processing failed: {e}")

        # Step 4: Validate processed data
        # validate_processed_data() from validation.py should:
        # - Check data shape/structure
        # - Verify no NaN/invalid values
        # - Ensure data meets expected constraints
        logger.debug("Validating processed data")
        try:
            validate_processed_data(data, config)
        except Exception as e:
            raise ValidationError(f"Processed data validation failed: {e}")

        # Step 5: Convert to requested output format
        # convert_data() from conversion.py should:
        # - Check if required dependencies are installed
        # - Detect current format of data
        # - Convert to requested format if needed
        # - Handle all import logic for optional dependencies
        # - Provide clear error messages for missing dependencies
        logger.debug(f"Converting data to {config.output_format} format")
        try:
            data = convert_data(data, config)
        except ImportError as e:
            raise ConversionError(
                f"Missing dependencies for {config.output_format} format: {e}"
            )
        except Exception as e:
            raise ConversionError(f"Data conversion failed: {e}")

        # Step 6: Validate converted data
        # validate_converted_data() from validation.py should:
        # - Verify no data was lost during conversion
        # - Check format-specific requirements were met
        # - Ensure data types are correct for the format
        # - Verify precision/accuracy maintained if critical
        logger.debug("Validating converted data")
        try:
            validate_converted_data(data, config)
        except Exception as e:
            raise ValidationError(f"Converted data validation failed: {e}")

        logger.info(f"Successfully retrieved data for scenario: {config.scenario_name}")
        return data

    except Exception as e:
        logger.error(f"Error processing scenario {config.scenario_name}: {e}")
        raise
