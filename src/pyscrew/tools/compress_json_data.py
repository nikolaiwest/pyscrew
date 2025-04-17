"""
Tool to prepare and compress JSON data for scenario archives

This script handles the preparation of raw data for the pyscrew package's published datasets.
It performs file renaming (.txt to .json) and JSON compression to reduce file sizes.

While the script can be run, its main purpose is to document the process rather than
serve as a general-purpose tool. The configuration values are intentionally hardcoded
to match the published dataset versions. This is primarily provided for transparency
and documentation purposes, showing exactly how the dataset archives were prepared for
publication on Zenodo.

Dataset: A link to the newest version can be found in the pyscrew library.
Repository: https://github.com/nikolaiwest/pyscrew
"""

import json
from pathlib import Path

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

# File handling configuration
# --------------------------
# Converts .txt to .json for clarity in the file names since the
# screw program would always export screw runs as text files.
RENAME_FILES = True

# While we want to maintain the original configuration of the raw data,
# minimizing the JSON files by removing white space saves a lot of file size (~33%).
# This step takes more time and does nothing after the first run.
COMPRESS_FILES = True

# Path configuration
# -----------------
# Hardcoded project root
PROJECT_ROOT = Path("C:/repo/pyscrew/")
# Use your cached data if you want to reproduce the label creation
DEFAULT_CACHE_DIR = None  # e.g. ".cache/pyscrew/extracted"

# Logging setup
# ------------
logger = get_logger(__name__, level="INFO")


class DataPreparationError(Exception):
    """Raised when data preparation or validation fails."""

    pass


def minimize_json_files(dir_json_data: Path) -> None:
    """
    Load and resave JSON files without whitespace to reduce file size.
    Only processes files in class-specific directories (e.g., json/001_control-group).

    Args:
        dir_json_data: Path to JSON root directory containing class subdirectories
    """

    def _bytes_to_human_readable(bytes_size):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        unit_index = 0
        while bytes_size >= 1024 and unit_index < len(units) - 1:
            bytes_size /= 1024
            unit_index += 1
        return f"{bytes_size:.2f} {units[unit_index]}"

    try:
        # Clean up any leftover .tmp files from interrupted runs
        tmp_files = list(dir_json_data.rglob("*.tmp"))
        if tmp_files:
            logger.info(
                f"Found {len(tmp_files)} leftover .tmp files from previous runs"
            )
            for tmp_file in tmp_files:
                try:
                    tmp_file.unlink()
                    logger.debug(f"Cleaned up leftover temp file: {tmp_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {tmp_file}: {e}")

        # Find all class directories
        class_dirs = [d for d in dir_json_data.iterdir() if d.is_dir()]
        total_minimized = 0
        total_saved = 0
        problematic_files = []

        total_files = sum(len(list(d.glob("*.json"))) for d in class_dirs)
        if total_files == 0:
            logger.info("No JSON files found to minimize")
            return

        logger.info(f"Starting JSON minimization of {total_files} files...")

        for class_dir in class_dirs:
            class_name = class_dir.name
            json_files = list(class_dir.glob("*.json"))
            class_saved = 0

            for json_file in json_files:
                try:
                    original_size = json_file.stat().st_size

                    # First try to read the file content
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            file_content = f.read()
                    except UnicodeDecodeError:
                        # Try with a different encoding if UTF-8 fails
                        with open(json_file, "r", encoding="latin-1") as f:
                            file_content = f.read()

                    # Try to parse the JSON and identify problematic sections
                    try:
                        data = json.loads(file_content)
                    except json.JSONDecodeError as je:
                        # Get context around the error
                        error_context = file_content[
                            max(0, je.pos - 50) : min(len(file_content), je.pos + 50)
                        ]
                        logger.error(
                            f"JSON parse error in {json_file.name} (class {class_name}):\n"
                            f"Error: {str(je)}\n"
                            f"Context: ...{error_context}..."
                        )
                        problematic_files.append((json_file, je))
                        continue

                    # Write to temporary file in same directory
                    temp_file = json_file.with_suffix(".tmp")
                    with open(temp_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, separators=(",", ":"))

                    # Atomic replace
                    temp_file.replace(json_file)
                    new_size = json_file.stat().st_size
                    space_saved = original_size - new_size
                    class_saved += space_saved
                    total_minimized += 1

                    logger.debug(
                        f"Minimized {json_file.name} in class {class_name}: saved {_bytes_to_human_readable(space_saved)}"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to process {json_file} in class {class_name}: {e}"
                    )
                    problematic_files.append((json_file, e))

            total_saved += class_saved
            if class_saved > 0:
                logger.info(
                    f"Class {class_name}: saved {_bytes_to_human_readable(class_saved)} across {len(json_files)} files"
                )

        if total_minimized > 0:
            logger.info(
                f"Successfully minimized {total_minimized} JSON files, total space saved: {_bytes_to_human_readable(total_saved)}"
            )

        if problematic_files:
            logger.warning(f"Found {len(problematic_files)} problematic files:")
            for file_path, error in problematic_files:
                logger.warning(f"- {file_path.name}: {str(error)}")

    except Exception as e:
        logger.error(f"Error during JSON minimization: {e}")
        raise DataPreparationError(f"Failed to minimize JSON files: {e}") from e


def rename_txt_to_json(dir_json_data: Path) -> None:
    """
    Rename .txt files to .json in class-specific directories.
    Ignores any .txt files in the root json/ directory.

    Args:
        dir_json_data: Path to JSON root directory containing class subdirectories
    """
    try:
        # Find all class directories
        class_dirs = [d for d in dir_json_data.iterdir() if d.is_dir()]
        total_renamed = 0

        for class_dir in class_dirs:
            class_name = class_dir.name
            txt_files = list(class_dir.glob("*.txt"))

            if txt_files:
                logger.info(f"Found {len(txt_files)} .txt files in class {class_name}")

                for txt_file in txt_files:
                    try:
                        json_path = txt_file.with_suffix(".json")
                        txt_file.rename(json_path)
                        total_renamed += 1
                        logger.info(
                            f"Renamed file in class {class_name}: {txt_file.stem} (.txt --> .json)"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to rename {txt_file} in class {class_name}: {e}"
                        )

        if total_renamed > 0:
            logger.info(
                f"Successfully renamed {total_renamed} .txt files to .json across all class directories"
            )

    except Exception as e:
        logger.error(f"Error during file renaming: {e}")
        raise DataPreparationError(f"Failed to rename .txt files: {e}") from e


def validate_directory_structure(
    dir_json_data: Path,
    scenario_config: ScenarioConfig,
) -> None:
    """
    Validate that directory structure matches scenario configuration.

    Args:
        dir_json_data: Path to JSON root directory
        scenario_config: ScenarioConfig object with class information

    Raises:
        DataPreparationError: If directory structure doesn't match expectations
    """
    try:
        # Get class information from the configuration
        class_counts = scenario_config.get_class_counts()

        if not class_counts:
            raise DataPreparationError(
                f"No class counts defined for scenario {scenario_config.scenario_id}"
            )

        # Get actual directories and file counts
        class_dirs = [d for d in dir_json_data.iterdir() if d.is_dir()]

        # Create a dictionary of {class_name: file_count}
        found_classes = {}
        for class_dir in class_dirs:
            class_name = class_dir.name
            file_count = len(list(class_dir.glob("*.json")))
            found_classes[class_name] = file_count

        # Check if all expected classes are present with the correct number of files
        missing_classes = []
        mismatched_counts = []

        for class_name, expected_count in class_counts.items():
            if class_name not in found_classes:
                missing_classes.append(class_name)
                continue

            actual_count = found_classes[class_name]
            if actual_count != expected_count:
                mismatched_counts.append(
                    f"{class_name}: found {actual_count}, expected {expected_count}"
                )

        # Report any issues found
        if missing_classes:
            missing_str = ", ".join(missing_classes)
            raise DataPreparationError(f"Missing class directories: {missing_str}")

        if mismatched_counts:
            mismatch_str = "; ".join(mismatched_counts)
            raise DataPreparationError(f"Mismatched file counts: {mismatch_str}")

        logger.info("Scenario directory structure validation successful")

    except Exception as e:
        if not isinstance(e, DataPreparationError):
            logger.error(f"Validation error: {e}")
            raise DataPreparationError(f"Directory structure validation failed: {e}")
        raise


def compress_json_data(
    dir_json_data: Path,
    scenario_config: ScenarioConfig,
    rename_files: bool = True,
    compress_files: bool = True,
) -> None:
    """
    Process scenario data by renaming files, compressing JSON, and validating structure.

    Args:
        dir_json_data: Directory containing class-specific JSON subdirectories
        scenario_config: ScenarioConfig object with scenario information
        rename_files: Whether to rename .txt files to .json
        compress_files: Whether to minimize JSON files by removing whitespace

    Raises:
        DataPreparationError: If processing fails
    """
    try:
        # Optional file renaming
        if rename_files:
            logger.info("Renaming .txt files to .json...")
            rename_txt_to_json(dir_json_data)

        # Optional file compression
        if compress_files:
            logger.info("Compressing JSON files...")
            minimize_json_files(dir_json_data)

        # Validate structure after processing
        logger.info("Validating dataset structure...")
        validate_directory_structure(dir_json_data, scenario_config)

        logger.info("Data processing complete")

    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        raise DataPreparationError(f"Failed to process scenario data: {e}") from e


def main():
    """
    Process JSON measurement data files for scenario archive.

    This function prepares the raw data by renaming files and compressing JSON
    to create the exact file structure as published with the dataset.
    """
    try:
        # Load scenario configuration from scenarios directory
        dir_scenarios = PROJECT_ROOT / "src" / "pyscrew" / "scenarios"
        scenario_config = ScenarioConfig(
            scenario_id=SCENARIO_ID, base_dir=dir_scenarios
        )
        scenario_full_name = scenario_config.get_full_name()

        # Use cached data if specified by user, otherwise use project data
        if DEFAULT_CACHE_DIR:
            dir_json_data = (
                Path.home() / DEFAULT_CACHE_DIR / scenario_full_name / "json"
            )
        else:
            dir_json_data = PROJECT_ROOT / "data" / "json" / scenario_full_name

        if not dir_json_data.exists():
            raise DataPreparationError(f"Data directory not found: {dir_json_data}")

        # Process data using the scenario configuration
        logger.info(f"Processing JSON files from {dir_json_data}")
        logger.info(f"Using scenario configuration: {scenario_config}")
        compress_json_data(
            dir_json_data,
            scenario_config,
            rename_files=RENAME_FILES,
            compress_files=COMPRESS_FILES,
        )

    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
