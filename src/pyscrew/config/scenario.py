from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Dict, List

import yaml


@dataclass
class ScenarioKeys:
    """Dataclass for scenario configuration keys to avoid hardcoding strings."""

    # Top-level sections
    NAMES: ClassVar[str] = "names"
    CLASSES: ClassVar[str] = "classes"
    DATA: ClassVar[str] = "data"
    METADATA: ClassVar[str] = "metadata"

    # Name fields
    SHORT: ClassVar[str] = "short"
    LONG: ClassVar[str] = "long"
    FULL: ClassVar[str] = "full"

    # Class fields
    COUNT: ClassVar[str] = "count"
    CONDITION: ClassVar[str] = "condition"  # e.g. "normal", "faulty" or "mixed"
    DESCRIPTION: ClassVar[str] = "description"

    # Data fields
    RECORD_ID: ClassVar[str] = "record_id"
    FILE_NAME: ClassVar[str] = "file_name"
    MD5_CHECKSUM: ClassVar[str] = "md5_checksum"


class ScenarioConfig:
    """Class for loading and working with scenario configurations from YAML files."""

    # Class-level access to keys
    Keys = ScenarioKeys

    def __init__(
        self,
        scenario_id: str,
        base_dir: Path = None,
        cache_dir: Path = None,
        force_download: bool = False,
    ):
        """
        Initialize a scenario configuration.

        Args:
            scenario_id: Identifier for the scenario (e.g., 's01', 's02')
            base_dir: Base directory where scenario YAML files are stored
            cache_dir: Directory for caching downloaded and extracted files
            force_download: Whether to force re-download even if cached
        """
        self.scenario_id = scenario_id

        # Set config directory for YAML files
        if base_dir is None:
            # Use the same path resolution as main.py
            self.config_dir = Path(__file__).parent.parent / "scenarios"
        else:
            self.config_dir = Path(base_dir)

        self.config_path = self.config_dir / f"{scenario_id}.yml"

        # Store cache directory and force_download flag
        self.cache_dir = cache_dir
        self.force_download = force_download

        self.names = {}
        self.classes = {}
        self.data = {}
        self.metadata = {}

        # Load the configuration
        self.load_config()

    def load_config(self) -> None:
        """Load the scenario configuration from YAML file."""

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Scenario config file not found: {self.config_path}"
            )

        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)

        # Update fields with loaded config
        self.names = config[self.Keys.NAMES]
        self.classes = config[self.Keys.CLASSES]
        self.data = config[self.Keys.DATA]
        self.metadata = config[self.Keys.METADATA]

    def get_name(self, name_type: str = "full") -> str:
        """
        Get the scenario name based on the specified type.

        Args:
            name_type: Type of name to return ('short', 'long', or 'full')

        Returns:
            The requested name or the scenario_id if the name type is not found
        """
        if name_type in self.names:
            return self.names[name_type]
        return self.scenario_id

    def get_full_name(self) -> str:
        """Get the full scenario name with ID prefix."""
        return f"{self.scenario_id}_{self.get_name(self.Keys.FULL)}"

    def get_class_counts(self) -> Dict[str, int]:
        """Get dictionary of class counts."""
        return {
            class_name: class_info[self.Keys.COUNT]
            for class_name, class_info in self.classes.items()
        }

    def get_class_conditions(self) -> Dict[str, str]:
        """Get dictionary of class conditions.

        Returns:
            Dictionary mapping class names to their condition values ('normal' by default)
        """
        return {
            class_name: class_info[self.Keys.CONDITION]
            for class_name, class_info in self.classes.items()
        }

    def get_class_descriptions(self) -> Dict[str, str]:
        """Get dictionary of class descriptions."""
        return {
            class_name: class_info[self.Keys.DESCRIPTION]
            for class_name, class_info in self.classes.items()
        }

    def get_total_observations(self) -> int:
        """Get the total number of observations across all classes."""
        return sum(class_info[self.Keys.COUNT] for class_info in self.classes.values())

    def get_class_ids(self) -> List[str]:
        """Get list of class IDs (numeric part only)."""
        return [name.split("_")[0] for name in self.classes.keys()]

    def get_dataset_filename(self) -> str:
        """Get the dataset filename from the data section."""
        return self.data[self.Keys.FILE_NAME]

    def get_md5_checksum(self) -> str:
        """Get the MD5 checksum from the data section."""
        return self.data[self.Keys.MD5_CHECKSUM]

    def get_download_url(self) -> str:
        """Generate download URL for this scenario's dataset on Zenodo."""
        ZENODO_BASE_URL = "https://zenodo.org/records"
        record_id = self.data[self.Keys.RECORD_ID]
        file_name = self.data[self.Keys.FILE_NAME]
        return f"{ZENODO_BASE_URL}/{record_id}/files/{file_name}?download=1"

    def get_cache_dir(self) -> Path:
        """Get the cache directory for downloaded files."""
        return self.cache_dir

    def get_force_download(self) -> bool:
        """Get whether to force re-download even if cached."""
        return self.force_download if hasattr(self, "force_download") else False

    def __str__(self) -> str:
        """String representation of the scenario configuration."""
        if len(self.classes) == 1:
            n_classes = "class"
        else:
            n_classes = "classes"
        return (
            f"Scenario {self.scenario_id}: {self.get_name()} - "
            f"{len(self.classes)} {n_classes}, {self.get_total_observations()} observations"
        )
