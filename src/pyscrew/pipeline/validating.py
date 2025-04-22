from pathlib import Path
from typing import Any, Union

from pyscrew.config import PipelineConfig


def validate_loaded_data(data_path: Union[str, Path], config: PipelineConfig) -> None:
    """Validate the raw data structure after loading.

    Args:
        data_path: Path to directory containing the raw JSON files
        config: Configuration object containing validation settings

    Raises:
        ValidationError: If any of these checks fail:
            - Directory exists and is readable
            - Contains expected files for given scenario
            - Files have valid JSON structure
            - Required fields present in JSON
    """
    pass


def validate_processed_data(data: Any, config: PipelineConfig) -> None:
    """Validate the processed data before format conversion.

    Args:
        data: The processed data to validate
        config: Configuration object containing validation settings

    Raises:
        ValidationError: If any of these checks fail:
            - Data has expected shape/structure
            - No NaN/invalid values present
            - Values are within expected ranges
            - Selected measurements are present
            - Selected phases are present
    """
    pass


def validate_converted_data(data: Any, config: PipelineConfig) -> None:
    """Validate the data after format conversion.

    Args:
        data: The converted data to validate
        config: Configuration object containing format validation settings

    Raises:
        ValidationError: If any of these checks fail:
            - Data matches requested output format
            - No data was lost during conversion
            - Data types are correct for the format
            - Format-specific requirements are met
            - Precision/accuracy maintained if critical
    """
    pass
