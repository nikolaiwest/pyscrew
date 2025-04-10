from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Union


@dataclass
class PipelineKeys:
    """Dataclass for pipeline configuration key constants."""

    # Configuration section keys
    SCENARIO: ClassVar[str] = "scenario"
    FILTERING: ClassVar[str] = "filtering"
    PROCESSING: ClassVar[str] = "processing"
    SYSTEM: ClassVar[str] = "system"

    # Scenario keys
    SCENARIO_NAME: ClassVar[str] = "scenario_name"
    SCENARIO_ID: ClassVar[str] = "scenario_id"

    # Filtering keys
    SCENARIO_CLASSES: ClassVar[str] = "scenario_classes"
    MEASUREMENTS: ClassVar[str] = "measurements"
    SCREW_PHASES: ClassVar[str] = "screw_phases"
    SCREW_CYCLES: ClassVar[str] = "screw_cycles"
    SCREW_POSITIONS: ClassVar[str] = "screw_positions"

    # Processing keys
    HANDLE_DUPLICATES: ClassVar[str] = "handle_duplicates"
    HANDLE_MISSINGS: ClassVar[str] = "handle_missings"
    TARGET_LENGTH: ClassVar[str] = "target_length"
    PADDING_VALUE: ClassVar[str] = "padding_value"
    PADDING_POSITION: ClassVar[str] = "padding_position"
    CUTOFF_POSITION: ClassVar[str] = "cutoff_position"
    OUTPUT_FORMAT: ClassVar[str] = "output_format"

    # System keys
    CACHE_DIR: ClassVar[str] = "cache_dir"
    FORCE_DOWNLOAD: ClassVar[str] = "force_download"


class PipelineOptions:
    """Class containing valid options for the pipeline configuration."""

    MEASUREMENTS: List[str] = ["torque", "angle", "gradient", "time"]
    POSITIONS: List[str] = ["left", "right", "both"]
    OUTPUT_FORMATS: List[str] = ["numpy", "dataframe", "tensor", "list"]
    DUPLICATE_METHODS: List[str] = ["first", "last", "mean"]
    MISSING_METHODS: List[str] = ["mean", "zero"]
    PADDING_POSITIONS: List[str] = ["pre", "post"]
    CUTOFF_POSITIONS: List[str] = ["pre", "post"]

    @classmethod
    def validate_option(cls, option_name: str, value: Any) -> bool:
        """Validate if a value is a valid option for the given option type."""
        options_list = getattr(cls, option_name.upper(), None)
        if options_list is None:
            return True  # No validation if the option list doesn't exist
        return value in options_list


class ScenarioMap:
    """Mapping between scenario names/codes and IDs."""

    FULL_NAMES: Dict[str, int] = {
        "thread-degradation": 1,
        "surface-friction": 2,
        "injection-molding-manipulations-upper-workpiece": 5,
        "injection-molding-manipulations-lower-workpiece": 6,
    }

    SHORT_CODES: Dict[str, int] = {
        "s01": 1,
        "s02": 2,
        "s05": 5,
        "s06": 6,
    }

    @classmethod
    def get_map(cls) -> Dict[str, int]:
        """Return combined mapping of all scenario identifiers to IDs."""
        combined = {}
        combined.update(cls.FULL_NAMES)
        combined.update(cls.SHORT_CODES)
        return combined

    @classmethod
    def get_id(cls, scenario_name: Union[str, int]) -> int:
        """Get scenario ID from name, short code, or ID."""
        if isinstance(scenario_name, int):
            # Verify it's a valid ID
            valid_ids = set(cls.get_map().values())
            if scenario_name not in valid_ids:
                raise ValueError(f"Invalid scenario ID: {scenario_name}")
            return scenario_name

        # Convert string to lowercase for case-insensitive matching
        name = scenario_name.lower()
        scenario_id = cls.get_map().get(name)

        if scenario_id is None:
            valid_options = sorted(
                set(cls.get_map().keys()) | set(map(str, set(cls.get_map().values())))
            )
            raise ValueError(
                f"Invalid scenario identifier. Valid options are: {', '.join(valid_options)}"
            )

        return scenario_id


class PipelineConfig:
    """Configuration for data loading and processing pipeline."""

    # Class-level access to keys and options
    Keys = PipelineKeys
    Options = PipelineOptions
    Scenarios = ScenarioMap

    def __init__(
        self,
        scenario_name: Union[str, int],
        measurements: Optional[List[str]] = None,
        scenario_classes: Optional[List[int]] = None,
        screw_phases: Optional[List[int]] = None,
        screw_cycles: Optional[List[int]] = None,
        screw_positions: str = "both",
        handle_duplicates: str = "first",
        handle_missings: str = "mean",
        target_length: int = 1000,
        padding_value: float = 0.0,
        padding_position: str = "post",
        cutoff_position: str = "post",
        output_format: str = "numpy",
        cache_dir: Optional[Path] = None,
        force_download: bool = False,
    ):
        """
        Initialize pipeline configuration.

        Args:
            scenario_name: Scenario identifier (name, short code, or ID)
            measurements: Measurements to return (torque, angle, gradient, time)
            scenario_classes: List of scenario classes to include
            screw_phases: Screw phases to include (1-4)
            screw_cycles: Specific cycles to include
            screw_positions: Position to analyze (left, right, both)
            handle_duplicates: How to handle duplicate time points (first, last, mean)
            handle_missings: How to handle missing values (mean, zero, or float value)
            target_length: Desired length for all sequences
            padding_value: Value to use for padding shorter sequences
            padding_position: Position to add padding (pre, post)
            cutoff_position: Position to truncate longer sequences (pre, post)
            output_format: Output format (numpy, dataframe, tensor, list)
            cache_dir: Directory for caching downloaded data
            force_download: Force re-download even if cached
        """
        # Scenario identification
        self.scenario_name = scenario_name
        self.scenario_id = self.Scenarios.get_id(scenario_name)

        # Filtering settings
        self.scenario_classes = scenario_classes
        self.measurements = self._validate_measurements(measurements)
        self.screw_phases = self._validate_phases(screw_phases)
        self.screw_cycles = screw_cycles
        self.screw_positions = self._validate_option("POSITIONS", screw_positions)

        # Processing settings
        self.handle_duplicates = self._validate_option(
            "DUPLICATE_METHODS", handle_duplicates
        )
        self.handle_missings = self._validate_missing_method(handle_missings)

        # Validate missing/duplicate dependency
        if self.handle_missings is not None and self.handle_duplicates is None:
            raise ValueError(
                "Cannot handle missing values without handling duplicates first. "
                "Please set handle_duplicates to a valid method when using handle_missings."
            )

        self.target_length = target_length
        self.padding_value = padding_value
        self.padding_position = self._validate_option(
            "PADDING_POSITIONS", padding_position
        )
        self.cutoff_position = self._validate_option(
            "CUTOFF_POSITIONS", cutoff_position
        )
        self.output_format = self._validate_option("OUTPUT_FORMATS", output_format)

        # System settings
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.force_download = force_download

    def _validate_measurements(
        self, measurements: Optional[List[str]]
    ) -> Optional[List[str]]:
        """Validate measurement types."""
        if measurements is None:
            return None

        invalid = [m for m in measurements if m not in self.Options.MEASUREMENTS]
        if invalid:
            raise ValueError(
                f"Invalid measurements: {invalid}. Valid options are {self.Options.MEASUREMENTS}"
            )
        return measurements

    def _validate_phases(self, phases: Optional[List[int]]) -> Optional[List[int]]:
        """Validate screw phases."""
        if phases is None:
            return None

        invalid = [p for p in phases if p < 1 or p > 4]
        if invalid:
            raise ValueError(
                f"Invalid screw phases: {invalid}. Must be between 1 and 4."
            )
        return phases

    def _validate_option(self, option_type: str, value: str) -> str:
        """Validate option against allowed values."""
        options_list = getattr(self.Options, option_type, None)
        if options_list is None:
            return value

        if value not in options_list:
            raise ValueError(
                f"Invalid {option_type.lower()}: {value}. Valid options are {options_list}"
            )
        return value

    def _validate_missing_method(self, value: Union[str, float]) -> Union[str, float]:
        """Validate missing value handling method."""
        if value is None:
            return None

        if value in self.Options.MISSING_METHODS:
            return value

        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid missing value method: {value}. "
                f"Valid options are {self.Options.MISSING_METHODS}, None, or a float value"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            self.Keys.SCENARIO: {
                self.Keys.SCENARIO_NAME: self.scenario_name,
                self.Keys.SCENARIO_ID: self.scenario_id,
            },
            self.Keys.FILTERING: {
                self.Keys.SCENARIO_CLASSES: self.scenario_classes,
                self.Keys.MEASUREMENTS: self.measurements,
                self.Keys.SCREW_PHASES: self.screw_phases,
                self.Keys.SCREW_CYCLES: self.screw_cycles,
                self.Keys.SCREW_POSITIONS: self.screw_positions,
            },
            self.Keys.PROCESSING: {
                self.Keys.HANDLE_DUPLICATES: self.handle_duplicates,
                self.Keys.HANDLE_MISSINGS: self.handle_missings,
                self.Keys.TARGET_LENGTH: self.target_length,
                self.Keys.PADDING_VALUE: self.padding_value,
                self.Keys.PADDING_POSITION: self.padding_position,
                self.Keys.CUTOFF_POSITION: self.cutoff_position,
                self.Keys.OUTPUT_FORMAT: self.output_format,
            },
            self.Keys.SYSTEM: {
                self.Keys.CACHE_DIR: str(self.cache_dir) if self.cache_dir else None,
                self.Keys.FORCE_DOWNLOAD: self.force_download,
            },
        }

    def __str__(self) -> str:
        """String representation of the pipeline configuration."""
        return (
            f"Pipeline Config for {self.scenario_name} (ID: {self.scenario_id})\n"
            f"Measurements: {self.measurements or 'all'}\n"
            f"Format: {self.output_format}, Target length: {self.target_length}"
        )
