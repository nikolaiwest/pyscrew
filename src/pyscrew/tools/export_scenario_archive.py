"""
Tool to generate scenario archive files

This script handles the archive creation process for the pyscrew package's published datasets.
It packages JSON data files with metadata into standardized archive formats for distribution.

This is the second step in the two-step dataset preparation process:
1. Step: Label creation (create_label_csv.py)
   * Generates scenario-specific CSV files with metadata
2. Step: Archive creation (this script)
   * Combines JSON data, labels, and documentation
   * Creates archives in multiple formats

While the script can be run, its main purpose is to document the process rather than
serve as a general-purpose tool. The configuration values are intentionally hardcoded
to match the published dataset versions. This is primarily provided for transparency
and documentation purposes, showing exactly how the dataset archives were created for
publication on Zenodo.

Dataset: A link to the newest version can be found in the pyscrew library.
Repository: https://github.com/nikolaiwest/pyscrew
"""

import tarfile
import zipfile
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from pyscrew.config import ScenarioConfig
from pyscrew.utils.logger import get_logger

# Configuration for the published dataset version
# ----------------------------------------------

# The specific scenario ID as published on Zenodo and in pyscrew
SCENARIO_ID = "s01"  # "s01_variations-in-thread-degradation"
# SCENARIO_ID = "s02"  # "s02_variations-in-surface-friction"
# SCENARIO_ID = "s03"  # "s03_variations-in-assembly-conditions-1"
# SCENARIO_ID = "s04"  # "s04_variations-in-assembly-conditions-2"
# SCENARIO_ID = "s05"  # "s05_variations-in-upper-workpiece-fabrication"
# SCENARIO_ID = "s06"  # "s06_variations-in-lower-workpiece-fabrication"

# ZIP is the preferred format (better compression), but TAR is supported for compatibility
ARCHIVE_FORMATS = ["tar", "zip"]

# Path configuration
# -----------------
# Hardcoded project root
PROJECT_ROOT = Path("C:/repo/pyscrew/")

# Logging setup
# ------------
logger = get_logger(__name__, level="INFO")


class ArchiveFormat(Enum):
    """Supported archive formats."""

    TAR = ".tar"
    ZIP = ".zip"


class ArchiveCreationError(Exception):
    """Raised when archive creation fails."""

    pass


def create_scenario_archive(
    scenario_config: ScenarioConfig,
    archive_format: ArchiveFormat = ArchiveFormat.TAR,
    base_dir: Optional[Union[str, Path]] = None,
) -> None:
    """
    Create an archive for a specific scenario.

    Args:
        scenario_config: ScenarioConfig object with scenario information
        archive_format: Format to use (TAR or ZIP)
        base_dir: Optional base directory, defaults to PROJECT_ROOT

    Raises:
        ArchiveCreationError: If archive creation fails
    """
    try:
        # Get scenario full name
        scenario_full_name = scenario_config.get_full_name()

        # Set up paths
        base_path = Path(base_dir) if base_dir else PROJECT_ROOT

        # Source paths
        json_path = base_path / "data" / "json" / scenario_full_name
        csv_path = base_path / "data" / "csv" / f"{scenario_full_name}.csv"
        readme_file = (
            f"{scenario_config.scenario_id}_{scenario_config.get_name('long')}.md"
        )
        readme_path = base_path / "docs" / "scenarios" / readme_file

        # Target path
        target_dir = base_path / "data" / "archives"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{scenario_full_name}{archive_format.value}"

        # Validate source paths
        if not all(p.exists() for p in [json_path, csv_path, readme_path]):
            missing_paths = []
            if not json_path.exists():
                missing_paths.append(f"JSON: {json_path}")
            if not csv_path.exists():
                missing_paths.append(f"CSV: {csv_path}")
            if not readme_path.exists():
                missing_paths.append(f"README: {readme_path}")

            raise ArchiveCreationError(
                f"Missing required files for {scenario_full_name}. "
                f"Please ensure all source files exist:\n"
                f"{chr(10).join(missing_paths)}"
            )

        logger.info(f"Creating {archive_format.name} archive for {scenario_full_name}")

        if archive_format == ArchiveFormat.TAR:
            with tarfile.open(target_path, "w") as archive:
                archive.add(json_path, arcname="json")
                # Add CSV and README with standardized names
                archive.add(csv_path, arcname="labels.csv")
                archive.add(readme_path, arcname="README.md")

        elif archive_format == ArchiveFormat.ZIP:
            with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as archive:
                # Add JSON files
                for file_path in json_path.rglob("*"):
                    if file_path.is_file():
                        arcname = Path("json") / file_path.relative_to(json_path)
                        archive.write(file_path, arcname)
                # Add CSV and README with standardized names
                archive.write(csv_path, "labels.csv")
                archive.write(readme_path, "README.md")

        logger.info(f"Archive created successfully at {target_path}")

    except Exception as e:
        logger.error(f"Failed to create archive: {str(e)}")
        raise ArchiveCreationError(f"Archive creation failed: {str(e)}") from e


def main():
    """Create archives for the specified scenario in all formats."""
    try:
        # Load scenario configuration
        dir_scenarios = PROJECT_ROOT / "src" / "pyscrew" / "scenarios"

        # Convert format strings to enum values
        formats = [
            ArchiveFormat[fmt.upper()]
            for fmt in ARCHIVE_FORMATS
            if fmt.upper() in ArchiveFormat.__members__
        ]

        if not formats:
            logger.warning("No valid archive formats specified. Using TAR as default.")
            formats = [ArchiveFormat.TAR]

        logger.info(f"Processing scenario ID: {SCENARIO_ID}")

        # Load scenario configuration
        scenario_config = ScenarioConfig(
            scenario_id=SCENARIO_ID,
            base_dir=dir_scenarios,
        )

        logger.info(f"Using scenario configuration: {scenario_config}")

        # Create archives in all specified formats
        for archive_format in formats:
            create_scenario_archive(scenario_config, archive_format)

        logger.info(f"Scenario {SCENARIO_ID} processed successfully")

    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
