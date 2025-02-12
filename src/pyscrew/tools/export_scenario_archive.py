"""
Tool to generate scenario label files

This script documents the archive creation process for the pyscrew package's published datasets.
It is primarily provided for transparency and documentation purposes, showing exactly how
the dataset archives were created for publication on Zenodo.

We decided to keep this tool separate from the main package to maintain independence and
preserve documentation of the exact process used for published datasets. The tools are
not included in __init__ as they are meant for dataset preparation rather than usage.

Two-Step Process (run label creation first!):
1. Step: Label creation (create_label_csv.py)
    * Handles file renaming (.txt to .json)
    * Performs JSON compression if needed
    * Generates scenario-specific CSV files
2. Step: Archive creation (this script)
    * Combines JSON data, labels, and documentation
    * Creates archives in multiple formats

Suggested workflow: Individual scenario processing
- Each scenario can be processed separately
- Allows careful verification of each dataset
- Supports iterative addition of new scenarios
- Prevents batch processing errors
- Just adjust the globals in this script to the scenario

While combining both steps into a single script might seem more convenient, keeping them 
separate allows for thorough validation between steps and better matches the actual 
workflow used in dataset preparation.

Note: While this script can be run, its main purpose is to document the process.
The configuration values are intentionally hardcoded to match the published dataset versions.

Dataset: A link to the newest version can be found in the pyscrew library.
Repository: https://github.com/nikolaiwest/pyscrew
"""

import tarfile
import zipfile
from enum import Enum
from pathlib import Path
from typing import Optional, Union

import rarfile

from pyscrew.utils.logger import get_logger

# Configuration
# -------------

# Scenarios to process as published on Zenodo and in pyscrew
# Check out the scenario.yml for more info on available datasets
SCENARIOS = [
    "s01_thread-degradation",
    "s02_surface-friction",
    # "s03_error-collection-1",  # Future scenarios
    # "s04_error-collection-2",
]

# TAR is the preferred format, but ZIP and RAR are supported for compatibility
# Note: RAR requires WinRAR (Windows) or unrar (Linux/Mac) to be installed
ARCHIVE_FORMATS = [
    "tar",  # Preferred format
    "zip",
    "rar",
]

# Expected directory structure:
#   data/
#   ├── json/{scenario}/    # JSON measurement files
#   └── csv/{scenario}.csv  # Generated labels
#   docs/
#   └── scenarios/{scenario}.md  # Documentation

# Logging setup
logger = get_logger(__name__, level="INFO")


class ArchiveFormat(Enum):
    """Supported archive formats."""

    TAR = ".tar"
    ZIP = ".zip"
    RAR = ".rar"


class ArchiveCreationError(Exception):
    """Raised when archive creation fails.

    Args:
        message: Explanation of the error
    """

    pass


def create_scenario_archive(
    scenario_name: str,
    archive_format: ArchiveFormat = ArchiveFormat.TAR,
    base_dir: Optional[Union[str, Path]] = None,
) -> None:
    """
    Create an archive for a specific scenario.

    Args:
        scenario_name: Name of the scenario (e.g., "thread-degradation")
        archive_format: Format to use (TAR, ZIP, or RAR)
        base_dir: Optional base directory, defaults to current directory

    Raises:
        ArchiveCreationError: If archive creation fails
    """
    try:
        # Set up paths
        base_path = Path(base_dir) if base_dir else Path.cwd()

        # Source paths
        json_path = base_path / "data" / "json" / scenario_name
        csv_path = base_path / "data" / "csv" / f"{scenario_name}.csv"
        readme_path = base_path / "docs" / "scenarios" / f"{scenario_name}.md"

        # Target path
        target_dir = base_path / "data" / "archives"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{scenario_name}{archive_format.value}"

        # Validate source paths
        if not all(p.exists() for p in [json_path, csv_path, readme_path]):
            raise ArchiveCreationError(
                f"Missing required files for {scenario_name}. "
                f"Please ensure all source files exist:\n"
                f"JSON: {json_path}\n"
                f"CSV: {csv_path}\n"
                f"README: {readme_path}"
            )

        logger.info(f"Creating {archive_format.name} archive for {scenario_name}")

        if archive_format == ArchiveFormat.TAR:
            with tarfile.open(target_path, "w") as archive:
                archive.add(json_path, arcname="json")
                archive.add(csv_path, arcname=f"{scenario_name}.csv")
                archive.add(readme_path, arcname=f"{scenario_name}.md")

        elif archive_format == ArchiveFormat.ZIP:
            with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as archive:
                # Add JSON files
                for file_path in json_path.rglob("*"):
                    if file_path.is_file():
                        arcname = "json" / file_path.relative_to(json_path)
                        archive.write(file_path, arcname)
                # Add CSV and README
                archive.write(csv_path, f"{scenario_name}.csv")
                archive.write(readme_path, f"{scenario_name}.md")

        elif archive_format == ArchiveFormat.RAR:
            # Note: This requires the 'rarfile' package and WinRAR/unrar installed
            with rarfile.RarFile(target_path, "w") as archive:
                # Add JSON files
                for file_path in json_path.rglob("*"):
                    if file_path.is_file():
                        arcname = "json" / file_path.relative_to(json_path)
                        archive.write(file_path, arcname)
                # Add CSV and README
                archive.write(csv_path, f"{scenario_name}.csv")
                archive.write(readme_path, f"{scenario_name}.md")

        logger.info(f"Archive created successfully at {target_path}")

    except Exception as e:
        logger.error(f"Failed to create archive: {str(e)}")
        raise ArchiveCreationError(f"Archive creation failed: {str(e)}")


def main():
    """Create archives for all scenarios in all formats."""
    try:
        scenarios = [
            "s01_thread-degradation",
            "s02_surface-friction",
            # "s03_error-collection-1",
            # "s04_error-collection-2",
        ]

        formats = [
            ArchiveFormat.TAR,  # Preferred format
            ArchiveFormat.ZIP,
            ArchiveFormat.RAR,
        ]

        for scenario in scenarios:
            logger.info(f"Processing scenario: {scenario}")
            for archive_format in formats:
                create_scenario_archive(scenario, archive_format)

    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
