import pytest

import pyscrew as ps
from pyscrew.utils.data_model import JsonFields


@pytest.mark.integration
class TestMainAPI:
    """Integration tests for the main PyScrew API functionality."""

    def test_list_scenarios(self):
        """Test that available scenarios can be listed correctly."""
        scenarios = ps.list_scenarios()
        # Verify we get a dictionary
        assert isinstance(
            scenarios, dict
        ), "Scenarios should be returned as a dictionary"

        # Verify expected scenarios are present
        expected_scenarios = {
            "thread-degradation": "Thread degradation analysis dataset",
            "surface-friction": "Surface friction analysis dataset",
        }
        assert scenarios == expected_scenarios, "Unexpected scenarios list"

    def test_get_data_with_filters(self, temp_cache_dir):
        """Test data retrieval with specific filters applied."""
        data = ps.get_data(
            "surface-friction",
            screw_positions="left",
            screw_cycles=[1, 2, 3],
            cache_dir=temp_cache_dir,
        )

        # Verify we get data for all expected measurements
        measurements = JsonFields.Measurements()
        expected_measurements = {
            measurements.TIME,
            measurements.TORQUE,
            measurements.ANGLE,
            measurements.GRADIENT,
            measurements.STEP,
        }

        assert isinstance(data, dict), "Data should be returned as a dictionary"
        assert (
            set(data.keys()) == expected_measurements
        ), "Missing expected measurements"

        # Verify data arrays are non-empty
        for measurement in data:
            assert len(data[measurement]) > 0, f"No data for {measurement}"

        # Verify filtered data properties
        for measurement in data:
            # Since we filtered for left position and cycles 1-3,
            # verify the number of runs matches expectations
            run_count = len(data[measurement])
            assert run_count > 0, f"No runs found for {measurement}"
            # You might want to add more specific assertions about the expected
            # number of runs based on your knowledge of the dataset

    @pytest.mark.parametrize(
        "scenario_name", ["thread-degradation", "surface-friction"]
    )
    def test_get_data_basic(self, temp_cache_dir, scenario_name):
        """Test basic data retrieval for each scenario without filters."""
        data = ps.get_data(scenario_name, cache_dir=temp_cache_dir)

        # Get expected measurement fields
        measurements = JsonFields.Measurements()
        expected_measurements = {
            measurements.TIME,
            measurements.TORQUE,
            measurements.ANGLE,
            measurements.GRADIENT,
            measurements.STEP,
        }

        # Verify basic data structure
        assert isinstance(data, dict), "Data should be returned as a dictionary"
        assert (
            set(data.keys()) == expected_measurements
        ), "Missing expected measurements"
        assert all(
            isinstance(data[k], list) for k in data
        ), "All values should be lists"

        # Verify data is non-empty
        assert all(len(data[k]) > 0 for k in data), "All measurements should have data"

    def test_invalid_filters(self, temp_cache_dir):
        """Test that invalid filters raise appropriate errors."""
        with pytest.raises(ValueError):
            ps.get_data(
                "surface-friction",
                screw_positions="invalid",  # Invalid position
                cache_dir=temp_cache_dir,
            )

        with pytest.raises(ValueError):
            ps.get_data(
                "nonexistent-scenario", cache_dir=temp_cache_dir  # Invalid scenario
            )
