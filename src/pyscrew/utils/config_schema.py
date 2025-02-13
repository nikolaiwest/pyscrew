from pathlib import Path
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

# Constants for valid options
MEASUREMENTS = ["torque", "angle", "gradient", "time"]
POSITIONS = ["left", "right", "both"]
OUTPUT_FORMATS = ["numpy", "dataframe", "tensor", "list"]
DUPLICATE_METHODS = ["first", "last", "mean"]
MISSING_METHODS = ["mean", "zero"]  # Will also accept float values
PADDING_POSITIONS = ["pre", "post"]
CUTOFF_POSITIONS = ["pre", "post"]

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

    Note:
        - If handle_missings is set, handle_duplicates must also be set
        - handle_duplicates can be used independently
    """

    # Scenario identification
    scenario_name: Union[str, int] = Field(
        description="Scenario identifier (name, short code, or ID)"
    )
    scenario_id: Optional[int] = Field(None, exclude=True)

    # Filtering settings
    scenario_classes: Optional[List[int]] = Field(
        None, description="List of scenario classes to include"
    )
    measurements: Optional[List[str]] = Field(
        None, description=f"Measurements to return. Options: {MEASUREMENTS}"
    )
    screw_phases: Optional[List[int]] = Field(
        None, ge=1, le=4, description="Screw phases to include (1-4)"
    )
    screw_cycles: Optional[List[int]] = Field(
        None, description="Specific cycles to include"
    )
    screw_positions: str = Field(
        "both", description=f"Position to analyze. Options: {POSITIONS}"
    )

    # Processing settings
    handle_duplicates: Optional[str] = Field(
        "first",
        description=f"How to handle duplicate time points. Options: {DUPLICATE_METHODS} or None to skip",
    )
    handle_missings: Optional[str] = Field(
        "mean",
        description=f"How to handle missing values. Options: {MISSING_METHODS}, float value, or None to skip",
    )
    target_length: int = Field(1000, description="Desired length for all sequences")
    padding_value: float = Field(
        0.0, description="Value to use for padding shorter sequences"
    )
    padding_position: str = Field(
        "post", description=f"Position to add padding. Options: {PADDING_POSITIONS}"
    )
    cutoff_position: str = Field(
        "post",
        description=f"Position to truncate longer sequences. Options: {CUTOFF_POSITIONS}",
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

    @field_validator("screw_positions")
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

    @field_validator("handle_duplicates")
    def validate_duplicate_method(cls, v: Optional[str]) -> Optional[str]:
        """Validate duplicate handling method."""
        if v is None:
            return v
        if v not in DUPLICATE_METHODS:
            raise ValueError(
                f"Invalid duplicate handling method: {v}. Valid options are {DUPLICATE_METHODS} or None"
            )
        return v

    @field_validator("handle_missings")
    def validate_missing_method(cls, v: Optional[str]) -> Optional[str]:
        """Validate missing value handling method."""
        if v is None:
            return v
        if v in MISSING_METHODS:
            return v
        try:
            float(v)
            return v
        except ValueError:
            raise ValueError(
                f"Invalid missing value method: {v}. Valid options are {MISSING_METHODS}, None, or a float value"
            )

    @field_validator("padding_position")
    def validate_padding_position(cls, v: str) -> str:
        """Validate padding position."""
        if v not in PADDING_POSITIONS:
            raise ValueError(
                f"Invalid padding position: {v}. Valid options are {PADDING_POSITIONS}"
            )
        return v

    @field_validator("cutoff_position")
    def validate_cutoff_position(cls, v: str) -> str:
        """Validate cutoff position."""
        if v not in CUTOFF_POSITIONS:
            raise ValueError(
                f"Invalid cutoff position: {v}. Valid options are {CUTOFF_POSITIONS}"
            )
        return v

    @model_validator(mode="after")
    def validate_missing_requires_duplicates(cls, values):
        """Ensure that if handle_missings is set, handle_duplicates is also set."""
        handle_missings = values.handle_missings
        handle_duplicates = values.handle_duplicates

        if handle_missings is not None and handle_duplicates is None:
            raise ValueError(
                "Cannot handle missing values without handling duplicates first. "
                "Please set handle_duplicates to a valid method when using handle_missings."
            )

        return values
