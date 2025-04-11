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
# SCENARIO_ID = "s02" # "s02_variations-in-surface-friction"
# SCENARIO_ID = "s03" # "s03_variations-in-assembly-conditions-1"
# SCENARIO_ID = "s04"  # "s04_variations-in-assembly-conditions-2"
# SCENARIO_ID = "s05" # "s05_variations-in-upper-workpiece-fabrication"
# SCENARIO_ID = "s06" # "s06_variations-in-lower-workpiece-fabrication"

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


def generate_labels(
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
        # Get class counts from scenario configuration
        class_counts: dict = scenario_config.get_class_counts()

        if not class_counts:
            raise LabelGenerationError(
                f"No class counts defined for scenario {scenario_config.scenario_id}"
            )

        # Process JSON files
        rows = []
        workpiece_generators: Dict[str, Generator[tuple[int, int], None, None]] = {}

        for class_dir in dir_json_data.iterdir():
            if not class_dir.is_dir():
                logger.error(f"{class_dir} is not a valid file directory.")
                raise LabelGenerationError(f"Found invalid file in {class_dir}") from e

            all_json_paths = sorted(class_dir.glob("*.json"))

            logger.info(
                f"- Processing class {class_dir.name}: {len(all_json_paths)} files ({len(workpiece_generators)})"
            )

            for json_path in all_json_paths:
                # Load JSON data
                with open(json_path) as file:
                    json_data = json.load(file)

                # Extract workpiece ID
                try:
                    workpiece_id = str(json_data[JsonFields.Run.WORKPIECE_ID])
                except KeyError as e:
                    logger.error(f"Missing workpiece ID in {json_path}")
                    raise LabelGenerationError(f"Required field missing: {e}") from e

                # Get position and usage from generator
                if workpiece_id not in workpiece_generators:
                    workpiece_generators[workpiece_id] = position_usage_generator()
                workpiece_location, workpiece_usage = next(
                    workpiece_generators[workpiece_id]
                )

                # Create row with usage and position info
                row = {
                    CsvFields.RUN_ID: json_data[JsonFields.Run.ID],
                    CsvFields.FILE_NAME: json_path.name,
                    CsvFields.CLASS_VALUE: class_dir.name,
                    CsvFields.WORKPIECE_ID: workpiece_id,
                    CsvFields.WORKPIECE_DATE: json_data[JsonFields.Run.DATE],
                    CsvFields.WORKPIECE_USAGE: workpiece_usage,
                    CsvFields.WORKPIECE_RESULT: json_data[JsonFields.Run.RESULT_VALUE],
                    CsvFields.WORKPIECE_LOCATION: workpiece_location,
                }
                rows.append(row)

        # Create DataFrame with explicit column order
        columns = [
            CsvFields.RUN_ID,
            CsvFields.FILE_NAME,
            CsvFields.CLASS_VALUE,
            CsvFields.WORKPIECE_ID,
            CsvFields.WORKPIECE_DATE,
            CsvFields.WORKPIECE_USAGE,
            CsvFields.WORKPIECE_RESULT,
            CsvFields.WORKPIECE_LOCATION,
        ]
        df = pd.DataFrame(rows, columns=columns)

        logger.info(
            f"Generated labels for {len(df)} files from {len(workpiece_generators)} unique workpieces"
        )
        return df

    except Exception as e:
        logger.error(f"Label generation failed: {e}")
        raise LabelGenerationError(f"Failed to generate labels: {e}") from e


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
        labels_df = generate_labels(dir_json_data, scenario_config)

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
