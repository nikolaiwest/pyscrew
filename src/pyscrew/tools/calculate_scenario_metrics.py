"""
Tool for metric calculation for the pyscrew dataset documentation

This module processes dataset files and calculates standardized metrics for
documentation. It handles both label files (CSV) and measurement data (JSON)
to generate statistics for the following documentation sections:
    - Sample Distribution
    - Class Distribution
    - Data Quality
    - Key Characteristics
    - Collection Timeline

The metrics are used to populate scenario-specific README files in the
docs/scenarios/ directory. Each function is mapped to a specific section
of the documentation template. It was the main source for the details in
all readme files and is provided as reference for future users.

While the script can be run, its main purpose is to document the process rather than
serve as a general-purpose tool. The configuration values are intentionally hardcoded
to match the published dataset versions.

Dataset: A link to the newest version can be found in the pyscrew library.
Repository: https://github.com/nikolaiwest/pyscrew
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from pyscrew.config import ScenarioConfig
from pyscrew.core import CsvFields, JsonFields
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
# Use your cached data if you want to reproduce the metrics calculation
DEFAULT_CACHE_DIR = None  # ".cache/pyscrew/extracted"

# Logging setup
# ------------
logger = get_logger(__name__, level="INFO")


class MetricsCalculationError(Exception):
    """Exception raised for errors in metrics calculation process."""

    pass


# Data Loading and Validation
def load_scenario_data(
    scenario_config: ScenarioConfig,
) -> Tuple[pd.DataFrame, List[Path]]:
    """Load and validate scenario data files.

    Args:
        scenario_config: ScenarioConfig object with scenario information

    Returns:
        Tuple containing:
            - DataFrame with labels
            - List of paths to JSON measurement files

    Raises:
        MetricsCalculationError: If data loading or validation fails
    """
    try:
        scenario_full_name = scenario_config.get_full_name()

        # Set up paths
        if DEFAULT_CACHE_DIR:
            base_dir = Path.home() / DEFAULT_CACHE_DIR
        else:
            base_dir = PROJECT_ROOT / "data"

        labels_path = base_dir / "csv" / f"{scenario_full_name}.csv"
        json_dir = base_dir / "json" / scenario_full_name

        if not labels_path.exists():
            raise MetricsCalculationError(f"Labels file not found: {labels_path}")

        if not json_dir.exists():
            raise MetricsCalculationError(f"JSON directory not found: {json_dir}")

        # Load labels
        labels_df = pd.read_csv(labels_path)

        # Find JSON files in class directories
        json_files = []
        class_dirs = [d for d in json_dir.iterdir() if d.is_dir()]

        for class_dir in class_dirs:
            json_files.extend(class_dir.glob("*.json"))

        if not json_files:
            raise MetricsCalculationError(f"No JSON files found in {json_dir}")

        logger.info(
            f"Loaded {len(labels_df)} labels and found {len(json_files)} JSON files"
        )
        return labels_df, json_files

    except Exception as e:
        logger.error(f"Data loading error: {e}")
        raise MetricsCalculationError(f"Failed to load scenario data: {e}") from e


# Sample Distribution Metrics (Sample Distribution section)
def _calculate_basic_metrics(labels_df: pd.DataFrame) -> Dict:
    """Calculate core dataset distribution metrics.

    Args:
        labels_df: DataFrame containing scenario labels

    Returns:
        Dictionary containing basic distribution metrics:
            - total_operations: Total number of operations
            - unique_workpieces: Number of unique workpieces
            - operations_per_workpiece: Average operations per workpiece
            - ok_count: Number of successful operations
            - nok_count: Number of failed operations
            - ok_percentage: Percentage of successful operations
            - nok_percentage: Percentage of failed operations
    """
    total = len(labels_df)
    ok_count = len(labels_df[labels_df[CsvFields.WORKPIECE_RESULT] == "OK"])
    nok_count = len(labels_df[labels_df[CsvFields.WORKPIECE_RESULT] == "NOK"])

    unique_workpieces = labels_df[CsvFields.WORKPIECE_ID].nunique()
    ops_per_workpiece = total / unique_workpieces if unique_workpieces > 0 else 0

    metrics = {
        "total_operations": total,
        "unique_workpieces": unique_workpieces,
        "operations_per_workpiece": round(ops_per_workpiece, 2),
        "ok_count": ok_count,
        "nok_count": nok_count,
        "ok_percentage": round(ok_count / total * 100, 2) if total > 0 else 0,
        "nok_percentage": round(nok_count / total * 100, 2) if total > 0 else 0,
    }

    logger.info("Sample Distribution Metrics calculated")
    return metrics


# Class Distribution Analysis (Distribution by Class section)
def _calculate_class_metrics(labels_df: pd.DataFrame) -> Dict:
    """Calculate distribution metrics for each class.

    Args:
        labels_df: DataFrame containing scenario labels

    Returns:
        Dictionary containing per-class metrics:
            - total_samples: Total samples in class
            - ok_count: Successful operations in class
            - nok_count: Failed operations in class
            - ok_ratio: Success ratio for class
            - nok_ratio: Failure ratio for class
    """
    metrics = {}

    for class_value in labels_df[CsvFields.CLASS_VALUE].unique():
        class_data = labels_df[labels_df[CsvFields.CLASS_VALUE] == class_value]
        total = len(class_data)
        ok_count = len(class_data[class_data[CsvFields.WORKPIECE_RESULT] == "OK"])
        nok_count = len(class_data[class_data[CsvFields.WORKPIECE_RESULT] == "NOK"])

        metrics[f"class_{class_value}"] = {
            "total_samples": total,
            "ok_count": ok_count,
            "nok_count": nok_count,
            "ok_ratio": round(ok_count / total * 100, 2) if total > 0 else 0,
            "nok_ratio": round(nok_count / total * 100, 2) if total > 0 else 0,
        }

    logger.info("Class Distribution Metrics calculated")
    return metrics


# Data Quality Assessment (Data Quality section)
def _calculate_sampling_metrics(json_files: List[Path], sample_size: int = 100) -> Dict:
    """Calculate sampling frequency and data quality metrics.

    Args:
        json_files: List of paths to JSON measurement files
        sample_size: Number of files to sample for calculations

    Returns:
        Dictionary containing sampling metrics:
            - sampling_frequency_hz: Average sampling frequency
            - missing_values_percentage: Percentage of missing values
            - data_completeness_percentage: Overall data completeness
    """
    time_diffs = []
    total_points = 0
    expected_points = 0

    # Limit to sample size or available files, whichever is smaller
    files_to_process = json_files[: min(sample_size, len(json_files))]

    for filepath in files_to_process:
        try:
            with open(filepath) as f:
                data = json.load(f)

            # Process each tightening step
            for step in data.get(JsonFields.Run.STEPS, []):
                if JsonFields.Step.GRAPH not in step:
                    continue

                measurements = step[JsonFields.Step.GRAPH]
                if JsonFields.Measurements.TIME not in measurements:
                    continue

                time_values = measurements[JsonFields.Measurements.TIME]

                if len(time_values) > 1:
                    # Calculate time differences between consecutive measurements
                    step_diffs = np.diff(time_values)
                    time_diffs.extend(step_diffs)

                    # Count actual data points
                    total_points += len(time_values)

                    # Estimate expected points based on duration and median sampling rate
                    if len(step_diffs) > 0:
                        expected_duration = time_values[-1] - time_values[0]
                        expected_step_points = int(
                            expected_duration / np.median(step_diffs)
                        )
                        expected_points += expected_step_points

        except Exception as e:
            logger.warning(f"Error processing file {filepath}: {e}")
            continue

    # Calculate metrics if we have sufficient data
    if time_diffs:
        median_diff = np.median(time_diffs)
        sampling_freq = 1 / median_diff if median_diff > 0 else 0
        completeness = (
            (total_points / expected_points * 100) if expected_points > 0 else 0
        )
    else:
        sampling_freq = 0
        completeness = 0

    metrics = {
        "sampling_frequency_hz": round(sampling_freq, 2),
        "missing_values_percentage": (
            round(100 - completeness, 2) if completeness <= 100 else 0
        ),
        "data_completeness_percentage": (
            round(completeness, 2) if completeness <= 100 else 100
        ),
    }

    logger.info("Data Quality Metrics calculated")
    return metrics


# Operation Analysis (Key Characteristics section)
def _calculate_operation_metrics(labels_df: pd.DataFrame) -> Dict:
    """Calculate operation-specific anomaly metrics.

    Args:
        labels_df: DataFrame containing scenario labels

    Returns:
        Dictionary containing operation metrics:
            - initial_anomaly_rate: Anomaly rate in initial cycles
            - peak_anomaly_rate: Maximum observed anomaly rate
            - peak_anomaly_cycle: Cycle number with highest anomaly rate
    """
    labels_df["is_nok"] = labels_df[CsvFields.WORKPIECE_RESULT] == "NOK"

    # Group by usage cycle and calculate anomaly rates
    cycle_stats = labels_df.groupby(CsvFields.WORKPIECE_USAGE)["is_nok"].agg(
        ["mean", "count"]
    )

    # Handle empty dataset gracefully
    if cycle_stats.empty:
        metrics = {
            "initial_anomaly_rate": 0,
            "peak_anomaly_rate": 0,
            "peak_anomaly_cycle": 0,
        }
    else:
        metrics = {
            "initial_anomaly_rate": (
                round(cycle_stats["mean"].iloc[1] * 100, 2)
                if len(cycle_stats) > 1
                else 0
            ),
            "peak_anomaly_rate": round(cycle_stats["mean"].max() * 100, 2),
            "peak_anomaly_cycle": int(cycle_stats["mean"].idxmax()),
        }

    logger.info("Operation Metrics calculated")
    return metrics


# Collection Timeline Analysis (Collection Timeline section)
def _calculate_collection_timeline(json_files: List[Path]) -> Dict:
    """Generate timeline of data collection by class.

    Args:
        json_files: List of paths to JSON measurement files

    Returns:
        Dictionary mapping class values to collection dates and sample counts
    """
    timeline = {}

    for filepath in json_files:
        try:
            # Extract class from directory name
            class_value = filepath.parent.name

            # Load JSON data
            with open(filepath) as f:
                data = json.load(f)

            # Extract date (first 10 characters for YYYY-MM-DD format)
            date_field = JsonFields.Run.DATE
            if date_field in data and data[date_field]:
                date = data[date_field][:10]

                # Initialize class entry if needed
                if class_value not in timeline:
                    timeline[class_value] = {}

                # Increment count for this date
                timeline[class_value][date] = timeline[class_value].get(date, 0) + 1

        except Exception as e:
            logger.warning(f"Error processing timeline data for {filepath}: {e}")
            continue

    logger.info("Collection Timeline calculated")
    return timeline


def calculate_scenario_metrics(scenario_config: ScenarioConfig) -> Dict:
    """Calculate and collect all metrics for README documentation.

    Args:
        scenario_config: ScenarioConfig object with scenario information

    Returns:
        Dictionary containing all calculated metrics organized by README section

    Raises:
        MetricsCalculationError: If any metrics calculation fails
    """
    try:
        scenario_full_name = scenario_config.get_full_name()
        logger.info(f"Starting metrics calculation for {scenario_full_name}")

        # Load data
        labels_df, json_files = load_scenario_data(scenario_config)

        # Calculate metrics for each documentation section
        metrics = {
            "sample_distribution": _calculate_basic_metrics(labels_df),
            "class_distribution": _calculate_class_metrics(labels_df),
            "data_quality": _calculate_sampling_metrics(json_files),
            "key_characteristics": _calculate_operation_metrics(labels_df),
            "collection_timeline": _calculate_collection_timeline(json_files),
        }

        logger.info(f"All metrics calculated successfully for {scenario_full_name}")
        return metrics

    except Exception as e:
        logger.error(f"Failed to calculate metrics: {e}")
        raise MetricsCalculationError(f"Metrics calculation failed: {e}") from e


def main():
    """Calculate metrics for README documentation."""
    try:
        # Load scenario configuration
        dir_scenarios = PROJECT_ROOT / "src" / "pyscrew" / "scenarios"
        scenario_config = ScenarioConfig(
            scenario_id=SCENARIO_ID,
            base_dir=dir_scenarios,
        )

        logger.info(f"Processing documentation metrics for {scenario_config}")

        # Calculate metrics
        metrics = calculate_scenario_metrics(scenario_config)

        # Print metrics summary
        print("\nFinal metrics summary:")
        print(json.dumps(metrics, indent=2))

        # Optional: Save metrics to file
        metrics_dir = PROJECT_ROOT / "data" / "metrics"
        metrics_dir.mkdir(parents=True, exist_ok=True)

        metrics_file = metrics_dir / f"{scenario_config.get_full_name()}_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"Metrics saved to {metrics_file}")

    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
