import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from pyscrew.loading import DataLoader, DatasetRegistry

# Basic fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_config():
    """Sample dataset configuration."""
    return {
        'datasets': {
            'thread-degradation': {
                'record_id': '14729548',
                'file_name': 'S01_thread-degradation.tar',
                'md5_checksum': '55a7585109e20fb7792b669aaaf9d841',
                'description': 'Thread degradation analysis dataset'
            }
        }
    }

@pytest.fixture
def mock_yaml(temp_dir, sample_config):
    """Create a mock scenarios.yml file."""
    yaml_path = temp_dir / "scenarios.yml"
    with open(yaml_path, 'w') as f:
        yaml.dump(sample_config, f)
    return yaml_path

# Basic tests
def test_dataset_registry_load(mock_yaml):
    """Test basic loading of dataset configuration."""
    with patch('pathlib.Path.__new__', return_value=mock_yaml):
        configs = DatasetRegistry._load_scenarios()
        assert 'thread-degradation' in configs
        assert configs['thread-degradation'].record_id == '14729548'

def test_dataloader_init(temp_dir):
    """Test DataLoader initialization and cache directory creation."""
    loader = DataLoader('thread-degradation', cache_dir=temp_dir)
    assert loader.cache_dir == temp_dir
    assert loader.archive_cache.exists()
    assert loader.data_cache.exists()

def test_dataset_registry_invalid_scenario():
    """Test handling of invalid scenario names."""
    with pytest.raises(ValueError, match="Unknown scenario"):
        DatasetRegistry.get_config('nonexistent-scenario')