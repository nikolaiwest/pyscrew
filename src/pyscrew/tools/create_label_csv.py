import json
from itertools import cycle
from pathlib import Path
from typing import Dict, Generator

import pandas as pd
import yaml
from tqdm import tqdm

from pyscrew.utils.data_model import CsvFields, JsonFields
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class LabelGenerationError(Exception):
    """Raised when label file generation fails."""

    pass


def minimize_json_files(json_dir: Path) -> None:
    """
    Load and resave JSON files without whitespace to reduce file size.
    Only processes files in class-specific directories (json/0, json/1, etc.).

    Args:
        json_dir: Path to JSON root directory containing class subdirectories
    """

    def _bytes_to_human_readable(bytes_size):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        unit_index = 0
        while bytes_size >= 1024 and unit_index < len(units) - 1:
            bytes_size /= 1024
            unit_index += 1
        return f"{bytes_size:.2f} {units[unit_index]}"

    try:
        class_dirs = [d for d in json_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        total_minimized = 0
        total_saved = 0

        # First count total files for progress bar
        total_files = sum(len(list(d.glob("*.json"))) for d in class_dirs)

        if total_files == 0:
            logger.info("No JSON files found to minimize")
            return

        logger.info(f"Starting JSON minimization of {total_files} files...")

        with tqdm(total=total_files, desc="Minimizing JSON files", leave=False) as pbar:
            for class_dir in class_dirs:
                class_value = int(class_dir.name)
                json_files = list(class_dir.glob("*.json"))
                class_saved = 0

                for json_file in json_files:
                    try:
                        original_size = json_file.stat().st_size

                        with open(json_file, "r") as f:
                            data = json.load(f)

                        with open(json_file, "w") as f:
                            json.dump(data, f, separators=(",", ":"))

                        new_size = json_file.stat().st_size
                        space_saved = original_size - new_size
                        class_saved += space_saved
                        total_minimized += 1

                        if space_saved > 0:
                            logger.debug(
                                f"Minimized {json_file.name} in class {class_value}: saved {_bytes_to_human_readable(space_saved)}"
                            )

                        pbar.update(1)

                    except Exception as e:
                        logger.error(
                            f"Failed to minimize {json_file} in class {class_value}: {e}"
                        )
                        pbar.update(1)

                total_saved += class_saved
                if class_saved > 0:
                    logger.info(
                        f"Class {class_value}: saved {class_saved} bytes across {len(json_files)} files"
                    )

        if total_minimized > 0:
            logger.info(
                f"Successfully minimized {total_minimized} JSON files, total space saved: {total_saved} bytes"
            )

    except Exception as e:
        logger.error(f"Error during JSON minimization: {e}")
        raise LabelGenerationError(f"Failed to minimize JSON files: {e}")


def rename_txt_to_json(json_dir: Path) -> None:
    """
    Rename .txt files to .json in class-specific directories (json/0, json/1, etc.).
    Ignores any .txt files in the root json/ directory.

    Args:
        json_dir: Path to JSON root directory containing class subdirectories
    """
    try:
        class_dirs = [d for d in json_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        total_renamed = 0

        for class_dir in class_dirs:
            class_value = int(class_dir.name)
            txt_files = list(class_dir.glob("*.txt"))

            if txt_files:
                logger.info(f"Found {len(txt_files)} .txt files in class {class_value}")

                for txt_file in txt_files:
                    try:
                        json_path = txt_file.with_suffix(".json")
                        txt_file.rename(json_path)
                        total_renamed += 1
                        logger.info(
                            f"Renamed file in class {class_value}: {txt_file.stem} (.txt --> .json)"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to rename {txt_file} in class {class_value}: {e}"
                        )

        if total_renamed > 0:
            logger.info(
                f"Successfully renamed {total_renamed} .txt files to .json across all class directories"
            )

    except Exception as e:
        logger.error(f"Error during file renaming: {e}")
        raise LabelGenerationError(f"Failed to rename .txt files: {e}")


def validate_scenario_structure(
    json_dir: Path,
    scenario_config: dict,
    rename_files: bool = True,
    compress_files: bool = True,
) -> None:
    """
    Validate that directory structure matches scenario configuration.

    Args:
        json_dir: Path to JSON root directory
        scenario_config: Dictionary containing scenario configuration with class_counts
        rename_files: Whether to rename .txt files to .json
        compress_files: Whether to minimize JSON files by removing whitespace

    Raises:
        LabelGenerationError: If directory structure doesn't match expectations
    """
    try:
        # Optional file renaming
        if rename_files:
            rename_txt_to_json(json_dir)

        # Optional file compression
        if compress_files:
            minimize_json_files(json_dir)

        # Get actual file counts
        class_dirs = [d for d in json_dir.iterdir() if d.is_dir()]
        found_classes = {int(d.name): len(list(d.glob("*.json"))) for d in class_dirs}

        # Get expected counts from config
        expected_classes = {
            int(k): v for k, v in scenario_config["class_counts"].items()
        }

        # Compare
        for class_id, expected_count in expected_classes.items():
            if class_id not in found_classes:
                raise LabelGenerationError(f"Missing directory for class {class_id}")

            actual_count = found_classes[class_id]
            if actual_count != expected_count:
                raise LabelGenerationError(
                    f"Class {class_id} has {actual_count} files, expected {expected_count}"
                )

        logger.info("Scenario structure validation successful")

    except ValueError as e:
        raise LabelGenerationError(f"Invalid class directory name: {e}")


def generate_labels(
    data_dir: Path,
    config_path: Path,
    scenario_name: str,
    rename_files: bool = True,
    compress_files: bool = True,
) -> pd.DataFrame:
    """
    Generate labels DataFrame from JSON measurement files.

    Args:
        data_dir: Directory containing class-specific JSON subdirectories
        config_path: Path to scenarios.yml configuration file
        scenario_name: Name of the scenario to process
        rename_files: Whether to rename .txt files to .json
        compress_files: Whether to minimize JSON files by removing whitespace

    Returns:
        DataFrame with columns matching CsvFields structure
    """
    try:
        # Load config
        with open(config_path) as f:
            config = yaml.safe_load(f)

        if scenario_name not in config["datasets"]:
            raise LabelGenerationError(f"Scenario {scenario_name} not found in config")

        scenario_config = config["datasets"][scenario_name]
        if "class_counts" not in scenario_config:
            raise LabelGenerationError(f"No class_counts defined for {scenario_name}")

        # Validate directory structure with optional operations
        validate_scenario_structure(
            data_dir, scenario_config, rename_files, compress_files
        )

        # Process JSON files
        rows = []
        workpiece_generators: Dict[str, Generator[tuple[int, int], None, None]] = {}

        for class_dir in data_dir.iterdir():
            if not class_dir.is_dir():
                continue

            class_value = int(class_dir.name)
            json_files = sorted(class_dir.glob("*.json"))

            logger.info(f"Processing class {class_value}: {len(json_files)} files")

            for file_path in json_files:
                # Load JSON data
                with open(file_path) as f:
                    data = json.load(f)

                # Extract workpiece ID
                try:
                    workpiece_id = str(data[JsonFields.Run.WORKPIECE_ID])
                except KeyError as e:
                    logger.error(f"Missing workpiece ID in {file_path}")
                    raise LabelGenerationError(f"Required field missing: {e}")

                # Get position and usage from generator
                if workpiece_id not in workpiece_generators:
                    workpiece_generators[workpiece_id] = position_usage_generator()

                position, usage = next(workpiece_generators[workpiece_id])

                # Create row with usage and position info
                row = {
                    CsvFields.RUN_ID: data[JsonFields.Run.ID],
                    CsvFields.FILE_NAME: file_path.name,
                    CsvFields.CLASS_VALUE: class_value,
                    CsvFields.RESULT_VALUE: data[JsonFields.Run.RESULT_VALUE],
                    CsvFields.WORKPIECE_ID: workpiece_id,
                    CsvFields.WORKPIECE_USAGE: usage,
                    CsvFields.WORKPIECE_LOCATION: position,
                }
                rows.append(row)

        # Create DataFrame with explicit column order
        columns = [
            CsvFields.RUN_ID,
            CsvFields.FILE_NAME,
            CsvFields.CLASS_VALUE,
            CsvFields.RESULT_VALUE,
            CsvFields.WORKPIECE_ID,
            CsvFields.WORKPIECE_USAGE,
            CsvFields.WORKPIECE_LOCATION,
        ]
        df = pd.DataFrame(rows, columns=columns)

        logger.info(f"Generated labels for {len(df)} files")
        logger.info(f"Found {len(workpiece_generators)} unique workpieces")

        return df

    except Exception as e:
        logger.error(f"Label generation failed: {e}")
        raise LabelGenerationError(f"Failed to generate labels: {e}")


def position_usage_generator() -> Generator[tuple[int, int], None, None]:
    """
    Generate position and usage count for workpieces.

    Yields:
        Tuple of (position, usage_count) where:
        - position alternates between 0 (left) and 1 (right)
        - usage_count increments after each right position
    """
    usage = 0
    for position in cycle([0, 1]):
        yield position, usage
        if position == 1:  # After right position
            usage += 1


def main():
    """Generate labels.csv file from JSON measurement data."""
    try:
        # User Selection
        rename_files = False  # Change .txt suffix to .json for clarity
        compress_files = False  # Remove whitespace in screw runs to save disc space
        scenario_name = "S02_surface-friction"

        # Configure paths relative to repo structure
        script_dir = Path(__file__).parent
        config_path = script_dir / "../scenarios.yml"
        config_path = config_path.resolve()  # Clean up the path

        # Default location for the imports
        data_dir = Path.home() / f".cache/pyscrew/extracted/{scenario_name}/json"

        if not all(p.exists() for p in [data_dir, config_path]):
            raise LabelGenerationError("Required paths not found")

        # Generate labels
        logger.info(f"Processing JSON files from {data_dir}")
        labels_df = generate_labels(
            data_dir,
            config_path,
            scenario_name[4:],  # Remove any "S01_" prefix
            rename_files=rename_files,
            compress_files=compress_files,
        )

        # Save to CSV
        output_path = script_dir / "labels.csv"
        labels_df.to_csv(output_path, index=False)
        logger.info(f"Labels saved to {output_path}")

    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
