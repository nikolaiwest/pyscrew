from pathlib import Path

import pytest


def test_dataset_loading(raw_test_dataset):
    """Test loading the dataset from test directory."""
    # Verify dataset loaded correctly
    assert len(raw_test_dataset) > 0
    assert len(raw_test_dataset.file_names) == 14  # Based on your labels.csv

    # Check class distribution
    class_counts = {}
    for run in raw_test_dataset.screw_runs:
        class_counts[run.class_value] = class_counts.get(run.class_value, 0) + 1

    assert class_counts["001_test-class-1"] == 6
    assert class_counts["101_test-class-2"] == 4
    assert class_counts["201_test-class-3"] == 4


def test_dataset_filtering(test_config):
    """Test filtering operations on the dataset."""
    from pyscrew.core import ScrewDataset

    # Create dataset with filters
    dataset = ScrewDataset(
        data_path=Path("tests/data/extracted/s0X_mock-data"),
        scenario_classes=["001_test-class-1"],
        screw_positions="left",
    )

    # Verify filtering
    assert len(dataset) == 3  # Only left positions of class 1

    for run in dataset.screw_runs:
        assert run.class_value == "001_test-class-1"
        assert run.workpiece_location == "left"
