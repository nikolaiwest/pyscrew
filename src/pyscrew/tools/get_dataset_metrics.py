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
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from pyscrew.utils.data_model import CsvFields, JsonFields
from pyscrew.utils.logger import get_logger

# Configuration
# ------------
# SCENARIO_NAME = "s01_thread-degradation"
# SCENARIO_NAME = "s02_surface-friction"
# SCENARIO_NAME = "s03_error-collection-1"
SCENARIO_NAME = "s05_injection-molding-manipulations-upper-workpiece"

# Use your cached data if you want to reproduce the label creation
DEFAULT_CACHE_DIR = None  # ".cache/pyscrew/extracted"

# Logging setup
logger = get_logger(__name__, level="INFO")


class MetricsCalculationError(Exception):
    """Exception raised for errors in metrics calculation process.

    Args:
        message: Explanation of the error
    """

    pass


# Data Loading and Validation (Dataset Structure section)
def load_scenario_data(base_path: str) -> Tuple[pd.DataFrame, List[Path]]:
    """Load and validate scenario data files.

    Args:
        base_path: Path to scenario directory containing labels.csv and json/

    Returns:
        Tuple containing:
            - DataFrame with labels
            - List of paths to JSON measurement files

    Raises:
        MetricsCalculationError: If data loading or validation fails
    """
    try:
        scenario_name = Path(base_path).parts[-1]
        labels_path = Path(base_path).parent / "csv" / f"{scenario_name}.csv"
        labels_df = pd.read_csv(labels_path.resolve())

        json_dir = Path(base_path).parent / "json" / scenario_name
        json_files = []
        for class_value in labels_df[CsvFields.CLASS_VALUE].unique():
            class_dir = json_dir / str(class_value)
            json_files.extend(class_dir.rglob("*.json"))

        if not json_files:
            raise MetricsCalculationError(f"No JSON files found in {json_dir}")

        logger.info(
            f"Loaded {len(labels_df)} labels and found {len(json_files)} JSON files"
        )
        return labels_df, json_files

    except Exception as e:
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
    ok_count = len(labels_df[labels_df[CsvFields.RESULT_VALUE] == "OK"])
    nok_count = len(labels_df[labels_df[CsvFields.RESULT_VALUE] == "NOK"])

    unique_workpieces = labels_df[CsvFields.WORKPIECE_ID].nunique()
    ops_per_workpiece = total / unique_workpieces if unique_workpieces > 0 else 0

    metrics = {
        "total_operations": total,
        "unique_workpieces": unique_workpieces,
        "operations_per_workpiece": round(ops_per_workpiece, 2),
        "ok_count": ok_count,
        "nok_count": nok_count,
        "ok_percentage": round(ok_count / total * 100, 2),
        "nok_percentage": round(nok_count / total * 100, 2),
    }

    logger.info("Sample Distribution Metrics calculated:")
    logger.info(json.dumps(metrics, indent=2))
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
        ok_count = len(class_data[class_data[CsvFields.RESULT_VALUE] == "OK"])
        nok_count = len(class_data[class_data[CsvFields.RESULT_VALUE] == "NOK"])

        metrics[f"class_{class_value}"] = {
            "total_samples": total,
            "ok_count": ok_count,
            "nok_count": nok_count,
            "ok_ratio": round(ok_count / total * 100, 2) if total > 0 else 0,
            "nok_ratio": round(nok_count / total * 100, 2) if total > 0 else 0,
        }

    logger.info("Class Distribution Metrics calculated:")
    logger.info(json.dumps(metrics, indent=2))
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

    for filepath in json_files[:sample_size]:
        with open(filepath) as f:
            data = json.load(f)

        for step in data[JsonFields.Run.STEPS]:
            measurements = step[JsonFields.Step.GRAPH]
            time_values = measurements[JsonFields.Measurements.TIME]

            if len(time_values) > 1:
                time_diffs.extend(np.diff(time_values))
                total_points += len(time_values)
                expected_duration = time_values[-1] - time_values[0]
                expected_points += int(
                    expected_duration / np.median(np.diff(time_values))
                )

    median_diff = np.median(time_diffs)
    sampling_freq = 1 / median_diff if median_diff > 0 else 0
    completeness = (total_points / expected_points * 100) if expected_points > 0 else 0

    metrics = {
        "sampling_frequency_hz": round(sampling_freq, 2),
        "missing_values_percentage": round(100 - completeness, 2),
        "data_completeness_percentage": round(completeness, 2),
    }

    logger.info("Data Quality Metrics calculated:")
    logger.info(json.dumps(metrics, indent=2))
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
    labels_df["is_nok"] = labels_df[CsvFields.RESULT_VALUE] == "NOK"
    cycle_stats = labels_df.groupby(CsvFields.WORKPIECE_USAGE)["is_nok"].agg(
        ["mean", "count"]
    )

    metrics = {
        "initial_anomaly_rate": (
            round(cycle_stats["mean"].iloc[1] * 100, 2) if len(cycle_stats) > 1 else 0
        ),
        "peak_anomaly_rate": round(cycle_stats["mean"].max() * 100, 2),
        "peak_anomaly_cycle": int(cycle_stats["mean"].idxmax()),
    }

    logger.info("Operation Metrics calculated:")
    logger.info(json.dumps(metrics, indent=2))
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
        class_value = int(filepath.parts[-2])

        with open(filepath) as f:
            data = json.load(f)

        date = data.get(JsonFields.Run.DATE)[:10]
        if date:
            if class_value not in timeline:
                timeline[class_value] = {}
            timeline[class_value][date] = timeline[class_value].get(date, 0) + 1

    logger.info("Collection Timeline calculated:")
    logger.info(json.dumps(timeline, indent=2))
    return timeline


def calculate_scenario_metrics(base_path: str) -> Dict:
    """Calculate and collect all metrics for README documentation.

    Args:
        base_path: Path to scenario directory

    Returns:
        Dictionary containing all calculated metrics organized by README section

    Raises:
        MetricsCalculationError: If any metrics calculation fails
    """
    try:
        logger.info(f"Starting metrics calculation for {base_path}")
        labels_df, json_files = load_scenario_data(base_path)

        metrics = {
            "sample_distribution": _calculate_basic_metrics(labels_df),
            "class_distribution": _calculate_class_metrics(labels_df),
            "data_quality": _calculate_sampling_metrics(json_files),
            "key_characteristics": _calculate_operation_metrics(labels_df),
            "collection_timeline": _calculate_collection_timeline(json_files),
        }

        logger.info("All metrics calculated successfully")
        return metrics

    except Exception as e:
        logger.error(f"Failed to calculate metrics: {e}")
        raise MetricsCalculationError(f"Metrics calculation failed: {e}") from e


def main():
    """Calculate metrics for README documentation."""
    try:
        if DEFAULT_CACHE_DIR:
            data_dir = Path.home() / DEFAULT_CACHE_DIR / SCENARIO_NAME
        else:
            data_dir = (
                Path(__file__).parent / "../../../data" / SCENARIO_NAME
            ).resolve()

        logger.info(f"Processing documentation metrics for {SCENARIO_NAME}")

        metrics = calculate_scenario_metrics(data_dir)
        # Print all
        print("\nFinal metrics summary:")
        print(json.dumps(metrics, indent=2))

    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
