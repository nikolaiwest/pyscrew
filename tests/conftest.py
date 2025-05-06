from pathlib import Path

import pytest

from pyscrew.config import PipelineConfig
from pyscrew.core import ScrewDataset
from pyscrew.pipeline.transformers import UnpackStepsTransformer

# Constants for test data
TEST_DATA_DIR = Path("tests/data/")
TEST_SCENARIO = "s0X"


@pytest.fixture
def test_config():
    """Basic config pointing to test data."""
    return PipelineConfig(scenario_name=TEST_SCENARIO, cache_dir=TEST_DATA_DIR)


@pytest.fixture
def raw_test_dataset(test_config):
    """Raw test dataset loaded from test data."""
    return ScrewDataset.from_config(test_config)


@pytest.fixture
def unpacked_test_dataset(raw_test_dataset, test_config):
    """Test dataset after unpacking step."""
    transformer = UnpackStepsTransformer(test_config)
    return transformer.transform(raw_test_dataset)


# Optionally mark integration tests
def pytest_configure(config):
    config.addinivalue_line("markers", "integration: mark tests that require downloads")


# Skip integration tests by default
def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests that require downloads",
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(
            reason="need --run-integration option to run"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
