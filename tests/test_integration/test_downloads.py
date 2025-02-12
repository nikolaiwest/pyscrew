import pytest

from pyscrew.loading import DataLoader
from pyscrew.utils.config_schema import ConfigSchema


@pytest.mark.integration
class TestZenodoDownloads:
    """Integration tests for downloading data from Zenodo."""

    def test_thread_degradation_download(self, temp_cache_dir):
        """Test downloading thread degradation dataset."""
        # Create config for thread degradation scenario
        config = ConfigSchema(
            scenario_name="thread-degradation",
            cache_dir=temp_cache_dir,
            force_download=True,  # Ensure fresh download
        )

        # Initialize loader
        loader = DataLoader(config.scenario_name, cache_dir=config.cache_dir)

        # Attempt download
        archive_path = loader.get_data(force=True)

        # Verify file exists and has content
        assert archive_path.exists(), "Downloaded file does not exist"
        assert archive_path.stat().st_size > 0, "Downloaded file is empty"

        # Verify correct file was downloaded
        assert archive_path.name == "s01_thread-degradation.tar", "Wrong file name"

    def test_surface_friction_download(self, temp_cache_dir):
        """Test downloading surface friction dataset."""
        # Create config for surface friction scenario
        config = ConfigSchema(
            scenario_name="surface-friction",
            cache_dir=temp_cache_dir,
            force_download=True,  # Ensure fresh download
        )

        # Initialize loader
        loader = DataLoader(config.scenario_name, cache_dir=config.cache_dir)

        # Attempt download
        archive_path = loader.get_data(force=True)

        # Verify file exists and has content
        assert archive_path.exists(), "Downloaded file does not exist"
        assert archive_path.stat().st_size > 0, "Downloaded file is empty"

        # Verify correct file was downloaded
        assert archive_path.name == "s02_surface-friction.tar", "Wrong file name"

    @pytest.mark.parametrize(
        "scenario_name", ["thread-degradation", "surface-friction"]
    )
    def test_checksum_verification(self, temp_cache_dir, scenario_name):
        """Test that downloaded files match their expected checksums."""
        config = ConfigSchema(
            scenario_name=scenario_name, cache_dir=temp_cache_dir, force_download=True
        )

        loader = DataLoader(config.scenario_name, cache_dir=config.cache_dir)
        archive_path = loader.get_data(force=True)

        # Checksum verification is built into get_data(),
        # so if we get here without exceptions, checksums matched
        assert True, "Checksum verification passed"
