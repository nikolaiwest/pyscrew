from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture(scope="session")
def temp_cache_dir():
    """Provide a temporary directory for test cache that persists across the test session."""
    with TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to the test data directory."""
    return Path(__file__).parent / "test_data"
