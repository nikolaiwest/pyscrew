from pathlib import Path
from typing import Any, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field

from pyscrew.utils.logger import get_logger
from pyscrew.conversion import convert_data
from pyscrew.loading import DatasetRegistry, load_data
from pyscrew.processing import process_data
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


class ScenarioConfig(BaseModel):
    """
    Configuration model for data processing scenarios.

    Attributes:
        output_type: Format for the output data (numpy, dataframe, or tensor)
        aggregation: Method to aggregate the data (e.g., mean, median)
        validation_level: Strictness of validation checks
        extra_params: Additional parameters for custom processing
    """

    output_type: Literal["numpy", "dataframe", "tensor"] = Field(
        default="numpy", description="Output format for the processed data"
    )
    aggregation: Optional[str] = Field(
        default=None, description="Aggregation method to apply to the data"
    )
    validation_level: Literal["strict", "lenient"] = Field(
        default="strict", description="Level of validation to apply"
    )
    extra_params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional processing parameters"
    )

    class Config:
        extra = "allow"
        validate_assignment = True


def list_scenarios() -> Dict[str, str]:
    """
    List all available scenarios and their descriptions.

    Returns:
        Dictionary mapping scenario names to their descriptions
    """
    return {
        name: config.description for name, config in DatasetRegistry.DATASETS.items()
    }


def get_data(
    scenario_name: str,
    config: Optional[Union[Dict[str, Any], ScenarioConfig]] = None,
    cache_dir: Optional[Union[str, Path]] = None,
    force: bool = False,
) -> Any:
    """
    Get and process data for a specific scenario.

    Parameters:
        scenario_name: Name of the scenario to load
        config: Configuration controlling processing and output format
               Can be either a dictionary or ScenarioConfig instance
               e.g. {'output_type': 'dataframe', 'aggregation': 'mean'}
        cache_dir: Optional directory for downloaded data
        force: Force new download even if cached

    Returns:
        Processed data in specified format (numpy array by default,
        optionally pandas DataFrame or tensorflow Tensor)

    Raises:
        DataNotFoundError: If scenario data cannot be found
        ValidationError: If data fails validation at any stage
        ProcessingError: If data processing fails
        ConversionError: If format conversion fails
        ImportError: If requested output format requires uninstalled dependencies
    """
    logger.info(f"Starting data retrieval for scenario: {scenario_name}")

    # Convert input config to ScenarioConfig instance
    if isinstance(config, dict):
        config = ScenarioConfig(**config)
    elif config is None:
        config = ScenarioConfig()

    try:
        # Step 1: Get raw data path and download if needed
        # load_data() from loading.py should:
        # - Check if data exists in cache_dir
        # - If not or if force=True, download from Zenodo
        # - Extract to cache_dir
        # - Return path to extracted data
        logger.debug("Loading raw data")
        raw_data_path = load_data(scenario_name, cache_dir=cache_dir, force=force)

        # Step 2: Validate raw data structure
        # validate_loaded_data() from validation.py should:
        # - Check if all expected files exist
        # - Verify basic file structure/format
        # - Raise ValidationError if checks fail
        logger.debug("Validating raw data")
        try:
            validate_loaded_data(raw_data_path)
        except Exception as e:
            raise ValidationError(f"Raw data validation failed: {e}")

        # Step 3: Process the data according to config
        # process_data() from processing.py should:
        # - Read the raw data
        # - Apply transformations based on config
        # - Return data in memory (not on disk)
        logger.debug(f"Processing data with config: {config.model_dump()}")
        try:
            data = process_data(raw_data_path, config.model_dump())
        except Exception as e:
            raise ProcessingError(f"Data processing failed: {e}")

        # Step 4: Validate processed data
        # validate_processed_data() from validation.py should:
        # - Check data shape/structure
        # - Verify no NaN/invalid values
        # - Ensure data meets expected constraints
        logger.debug("Validating processed data")
        try:
            validate_processed_data(data)
        except Exception as e:
            raise ValidationError(f"Processed data validation failed: {e}")

        # Step 5: Convert to requested output format
        # convert_data() from conversion.py should:
        # - Check if required dependencies are installed
        # - Detect current format of data
        # - Convert to requested format if needed
        # - Handle all import logic for optional dependencies
        # - Provide clear error messages for missing dependencies
        logger.debug(f"Converting data to {config.output_type} format")
        try:
            data = convert_data(data, config.output_type)
        except ImportError as e:
            raise ConversionError(
                f"Missing dependencies for {config.output_type} format: {e}"
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
            validate_converted_data(data, config.output_type)
        except Exception as e:
            raise ValidationError(f"Converted data validation failed: {e}")

        logger.info(f"Successfully retrieved data for scenario: {scenario_name}")
        return data

    except Exception as e:
        logger.error(f"Error processing scenario {scenario_name}: {e}")
        raise


# Example usage
if __name__ == "__main__":
    # Get data as numpy array (default)
    data = get_data("thread-degradation")

    # Get data as pandas DataFrame with specific processing
    config = ScenarioConfig(
        output_type="dataframe",
        aggregation="mean",
        extra_params={"custom_param": "value"},
    )
    data_df = get_data("thread-degradation", config=config)
