from pathlib import Path
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator

# Constants for valid options
MEASUREMENTS = ["torque", "angle", "gradient", "time"]
POSITIONS = ["left", "right", "both"]
OUTPUT_FORMATS = ["numpy", "dataframe", "tensor", "list"]

# Constants for scenario mapping
SCENARIO_MAP = {
    # Full names
    "thread-degradation": 1,
    "surface-friction": 2,
    # Short versions
    "s01": 1,
    "s02": 2,
}


class ConfigSchema(BaseModel):
    """Schema for data loading and processing configuration.

    This class handles all configuration settings for the data loading and processing pipeline.
    It validates inputs and provides standardized access to configuration values.
    """

    # Scenario identification
    scenario_name: Union[str, int] = Field(
        description="Scenario identifier (name, short code, or ID)"
    )
    scenario_id: Optional[int] = Field(None, exclude=True)

    # Filtering settings
    scenario_classes: Optional[List[str]] = Field(
        None, description="List of scenario classes to include"
    )
    measurements: Optional[List[str]] = Field(
        None, description=f"Measurements to return. Options: {MEASUREMENTS}"
    )
    phases: Optional[List[int]] = Field(
        None, ge=1, le=4, description="Screw phases to include (1-4)"
    )
    cycles: Optional[List[int]] = Field(None, description="Specific cycles to include")
    position: str = Field(
        "both", description=f"Position to analyze. Options: {POSITIONS}"
    )

    # Processing settings
    remove_negative_torque: bool = Field(
        False, description="Remove negative torque values from data"
    )
    interpolate_missings: bool = Field(
        False, description="Interpolate missing values (0.0012s intervals)"
    )
    output_format: str = Field(
        "numpy", description=f"Output format. Options: {OUTPUT_FORMATS}"
    )

    # System settings
    cache_dir: Optional[Path] = Field(
        None, description="Directory for caching downloaded data"
    )
    force_download: bool = Field(False, description="Force re-download even if cached")

    @field_validator("scenario_name")
    def validate_scenario_name(cls, v: Union[str, int]) -> str:
        """Validate and standardize scenario name input."""
        if isinstance(v, int):
            scenario_id = v
        else:
            v = v.lower()
            scenario_id = SCENARIO_MAP.get(v)

        valid_ids = set(SCENARIO_MAP.values())
        if scenario_id not in valid_ids:
            valid_options = sorted(set(SCENARIO_MAP.keys()) | set(map(str, valid_ids)))
            raise ValueError(
                f"Invalid scenario identifier. Valid options are: {', '.join(valid_options)}"
            )
        return v

    @field_validator("scenario_id", mode="after")
    def set_scenario_id(cls, v: Optional[int], info) -> int:
        """Set scenario_id based on scenario_name after validation."""
        scenario_name = info.data.get("scenario_name")
        if isinstance(scenario_name, int):
            return scenario_name
        return SCENARIO_MAP[scenario_name.lower()]

    @field_validator("measurements")
    def validate_measurements(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate measurement types."""
        if v is None:
            return v
        invalid = [m for m in v if m not in MEASUREMENTS]
        if invalid:
            raise ValueError(
                f"Invalid measurements: {invalid}. Valid options are {MEASUREMENTS}"
            )
        return v

    @field_validator("position")
    def validate_position(cls, v: str) -> str:
        """Validate position value."""
        if v not in POSITIONS:
            raise ValueError(f"Invalid position: {v}. Valid options are {POSITIONS}")
        return v

    @field_validator("output_format")
    def validate_output_format(cls, v: str) -> str:
        """Validate output format."""
        if v not in OUTPUT_FORMATS:
            raise ValueError(
                f"Invalid output format: {v}. Valid options are {OUTPUT_FORMATS}"
            )
        return v
