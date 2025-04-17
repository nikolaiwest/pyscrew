"""
Tool to create CSV labels for scenario archives

This script generates the labels.csv file for the pyscrew package's published datasets.
It maps JSON measurement files to the correct class labels and extracts metadata.

While the script can be run, its main purpose is to document the process rather than
serve as a general-purpose tool. The configuration values are intentionally hardcoded
to match the published dataset versions. This is primarily provided for transparency
and documentation purposes, showing exactly how the dataset labels were created for
publication on Zenodo.

Dataset: A link to the newest version can be found in the pyscrew library.
Repository: https://github.com/nikolaiwest/pyscrew
"""

import json
from itertools import cycle
from pathlib import Path
from typing import Dict, Generator

import pandas as pd

from pyscrew.core import CsvFields, JsonFields
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

# Path configuration
# -----------------
# Hardcoded project root
PROJECT_ROOT = Path("C:/repo/pyscrew/")
# Use your cached data if you want to reproduce the label creation
DEFAULT_CACHE_DIR = None  # e.g. ".cache/pyscrew/extracted"

# Logging setup
# ------------
logger = get_logger(__name__, level="INFO")


class LabelGenerationError(Exception):
    """Raised when label file generation fails."""

    pass


def position_usage_generator() -> Generator[tuple[int, int], None, None]:
    """
    Generate position and usage count for workpieces.

    Yields:
        Tuple of (position, usage_count) where:
        - position alternates between "left" and "right"
        - usage_count increments after each right position
    """
    usage = 0
    for position in cycle(["left", "right"]):
        yield position, usage
        if position == 1:  # After right position
            usage += 1


def generate_csv_labels(
    dir_json_data: Path,
    scenario_config: ScenarioConfig,
) -> pd.DataFrame:
    """
    Generate labels DataFrame from JSON measurement files.

    Args:
        dir_json_data: Directory containing class-specific JSON subdirectories
        scenario_config: ScenarioConfig object with scenario information

    Returns:
        DataFrame with columns matching CsvFields structure
    """
    try:
        # Validate scenario configuration
        _validate_scenario_config(scenario_config)

        # Determine if this is scenario s04 which requires special handling
        is_s04 = scenario_config.scenario_id == "s04"

        # Load metadata from experiment notes (for s04 we load more fields)
        metadata_dict = _load_metadata_from_notes(scenario_config.scenario_id, is_s04)

        # Process JSON files to create DataFrame rows
        rows = _process_json_files(
            dir_json_data, scenario_config, metadata_dict, is_s04
        )

        # Create DataFrame with explicit column order
        columns = _get_csv_column_order()
        df = pd.DataFrame(rows, columns=columns)

        # Log statistics about exceptions
        exception_count = df[df[CsvFields.SCENARIO_EXCEPTION] == 1].shape[0]
        workpiece_count = len(_get_unique_workpieces(rows))

        logger.info(f"Applied {exception_count} exceptions from notes")
        logger.info(
            f"Generated labels for {len(df)} files from {workpiece_count} unique workpieces"
        )

        return df

    except Exception as e:
        logger.error(f"Label generation failed: {e}")
        raise LabelGenerationError(f"Failed to generate labels: {e}") from e


def _validate_scenario_config(scenario_config: ScenarioConfig) -> None:
    """Validate the scenario configuration has required data."""
    class_counts = scenario_config.get_class_counts()
    if not class_counts:
        raise LabelGenerationError(
            f"No class counts defined for scenario {scenario_config.scenario_id}"
        )


def _load_metadata_from_notes(scenario_id: str, is_s04: bool = False) -> dict:
    """
    Load metadata from experiment notes.

    For most scenarios, this just loads exception files.
    For s04, it loads full metadata including class_value, workpiece_location, and scenario_condition.

    Args:
        scenario_id: The ID of the scenario (e.g., 's04', 's05')
        is_s04: Whether this is scenario s04 which requires special handling

    Returns:
        Dictionary with metadata by file name
    """
    metadata_dict = {}
    notes_file_path = (
        PROJECT_ROOT / "data" / "notes" / f"{scenario_id}_experiment-notes.csv"
    )

    if notes_file_path.exists():
        try:
            notes_df = pd.read_csv(notes_file_path)

            if is_s04:
                # For s04, store all metadata columns by file name
                for _, row in notes_df.iterrows():
                    metadata_dict[row["file_name"]] = {
                        "class_value": row["class_value"],
                        "workpiece_location": row["workpiece_location"],
                        "scenario_condition": row["scenario_condition"],
                        "scenario_exception": row["scenario_exception"],
                    }
                logger.info(
                    f"Loaded full metadata for {len(metadata_dict)} files from {notes_file_path}"
                )
            else:
                # For other scenarios, just track exception files
                exception_files = set(
                    notes_df[notes_df["scenario_exception"] == 1]["file_name"].tolist()
                )
                for file_name in exception_files:
                    metadata_dict[file_name] = {"scenario_exception": 1}
                logger.info(
                    f"Loaded {len(metadata_dict)} exception files from {notes_file_path}"
                )
        except Exception as e:
            logger.warning(
                f"Failed to load experiment notes: {e}. No metadata will be applied."
            )
    else:
        logger.info(
            f"No experiment notes found at {notes_file_path}. No metadata will be applied."
        )

    return metadata_dict


def _process_json_files(
    dir_json_data: Path,
    scenario_config: ScenarioConfig,
    metadata_dict: dict,
    is_s04: bool = False,
) -> list:
    """
    Process JSON files and create data rows.

    Args:
        dir_json_data: Directory containing class-specific JSON subdirectories
        scenario_config: ScenarioConfig object with scenario information
        metadata_dict: Dictionary containing metadata by file name
        is_s04: Whether this is scenario s04 which requires special handling

    Returns:
        List of dictionaries containing row data for DataFrame
    """
    rows = []
    workpiece_generators = {}
    class_conditions = scenario_config.get_class_conditions()

    for class_dir in dir_json_data.iterdir():
        if not class_dir.is_dir():
            logger.error(f"{class_dir} is not a valid file directory.")
            raise LabelGenerationError(f"Found invalid file in {class_dir}")

        all_json_paths = sorted(class_dir.glob("*.json"))

        logger.info(
            f"- Processing class {class_dir.name}: {len(all_json_paths)} files ({len(workpiece_generators)})"
        )

        for json_path in all_json_paths:
            row = _create_row_from_json(
                json_path,
                class_dir.name,
                class_conditions,
                workpiece_generators,
                metadata_dict,
                is_s04,
            )
            rows.append(row)

    return rows


def _create_row_from_json(
    json_path: Path,
    class_name: str,
    class_conditions: dict,
    workpiece_generators: dict,
    metadata_dict: dict,
    is_s04: bool = False,
) -> dict:
    """
    Create a single row of data from a JSON file.

    Args:
        json_path: Path to the JSON file
        class_name: Name of the class directory
        class_conditions: Dictionary mapping class names to conditions
        workpiece_generators: Dictionary of workpiece generators
        metadata_dict: Dictionary containing metadata by file name
        is_s04: Whether this is scenario s04 which requires special handling

    Returns:
        Dictionary containing row data
    """
    # Load JSON data
    with open(json_path) as file:
        json_data = json.load(file)

    # Extract workpiece ID
    try:
        workpiece_id = str(json_data[JsonFields.Run.WORKPIECE_ID])
    except KeyError as e:
        logger.error(f"Missing workpiece ID in {json_path}")
        raise LabelGenerationError(f"Required field missing: {e}") from e

    file_name = json_path.name

    # For s04, get metadata from experiment notes
    if is_s04 and file_name in metadata_dict:
        metadata = metadata_dict[file_name]
        class_value = metadata["class_value"]
        workpiece_location = metadata["workpiece_location"]
        scenario_condition = metadata["scenario_condition"]
        scenario_exception = int(metadata["scenario_exception"])

        # Verify that we're in the right class directory
        if class_value != class_name:
            logger.warning(
                f"Metadata mismatch: File {file_name} is in directory {class_name} "
                f"but metadata indicates it should be in {class_value}"
            )
    else:
        # For other scenarios, use normal logic
        class_value = class_name

        # Get position and usage from generator
        if workpiece_id not in workpiece_generators:
            workpiece_generators[workpiece_id] = position_usage_generator()
        workpiece_location, workpiece_usage = next(workpiece_generators[workpiece_id])

        # Get scenario condition
        scenario_condition = class_conditions[class_name]

        # Check if the file is marked as an exception
        scenario_exception = metadata_dict.get(file_name, {}).get(
            "scenario_exception", 0
        )

    # Create row with all information
    row = {
        CsvFields.RUN_ID: json_data[JsonFields.Run.ID],
        CsvFields.FILE_NAME: file_name,
        CsvFields.CLASS_VALUE: class_value,
        CsvFields.WORKPIECE_ID: workpiece_id,
        CsvFields.WORKPIECE_DATE: json_data[JsonFields.Run.DATE],
        CsvFields.WORKPIECE_USAGE: (
            0 if is_s04 else workpiece_usage
        ),  # No usage tracking for s04
        CsvFields.WORKPIECE_RESULT: json_data[JsonFields.Run.RESULT_VALUE],
        CsvFields.WORKPIECE_LOCATION: workpiece_location,
        CsvFields.SCENARIO_CONDITION: scenario_condition,
        CsvFields.SCENARIO_EXCEPTION: scenario_exception,
    }

    return row


def _get_csv_column_order() -> list:
    """Get the standardized column order for the CSV file."""
    return [
        CsvFields.RUN_ID,
        CsvFields.FILE_NAME,
        CsvFields.CLASS_VALUE,
        CsvFields.WORKPIECE_ID,
        CsvFields.WORKPIECE_DATE,
        CsvFields.WORKPIECE_USAGE,
        CsvFields.WORKPIECE_RESULT,
        CsvFields.WORKPIECE_LOCATION,
        CsvFields.SCENARIO_CONDITION,
        CsvFields.SCENARIO_EXCEPTION,
    ]


def _get_unique_workpieces(rows: list) -> set:
    """Extract unique workpiece IDs from the row data."""
    return {row[CsvFields.WORKPIECE_ID] for row in rows}


def main():
    """Generate labels.csv file from JSON measurement data.

    This function uses the configuration defined at module level to reproduce
    the exact labels.csv file published with the dataset.
    """
    try:
        # Load scenario configuration from scenarios directory
        dir_scenarios = PROJECT_ROOT / "src" / "pyscrew" / "scenarios"
        scenario_config = ScenarioConfig(
            scenario_id=SCENARIO_ID,
            base_dir=dir_scenarios,
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
            raise LabelGenerationError(f"Data directory not found: {dir_json_data}")

        # Generate labels using the scenario configuration
        logger.info(f"Processing JSON files from {dir_json_data}")
        logger.info(f"Using scenario configuration: {scenario_config}")
        labels_df = generate_csv_labels(dir_json_data, scenario_config)

        # Save to CSV
        dir_csv_target = PROJECT_ROOT / "data" / "csv"
        dir_csv_target.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        dir_csv_output = dir_csv_target / f"{scenario_full_name}.csv"
        labels_df.to_csv(dir_csv_output, index=False)
        logger.info(f"Labels saved to {dir_csv_output}")

    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
