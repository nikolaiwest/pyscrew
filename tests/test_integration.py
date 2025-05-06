import tempfile
from pathlib import Path

import numpy as np
import pytest

from pyscrew.config import PipelineConfig, ScenarioConfig
from pyscrew.pipeline import load_data, process_data


@pytest.mark.integration
def test_all_scenarios_integration():
    """Test downloading and processing all six datasets with default parameters."""
    # Create a temporary directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Scenario expectations based on README documentation
        scenario_expectations = {
            "s01": {"samples": 5000, "classes": 1, "name": "Thread Degradation"},
            "s02": {"samples": 12500, "classes": 8, "name": "Surface Friction"},
            # "s03": {"samples": 1800, "classes": 27, "name": "Assembly Conditions 1"},
            "s04": {"samples": 5000, "classes": 25, "name": "Assembly Conditions 2"},
            "s05": {"samples": 2400, "classes": 42, "name": "Upper Workpiece"},
            "s06": {"samples": 7482, "classes": 44, "name": "Lower Workpiece"},
        }
        for scenario_id, expected in scenario_expectations.items():
            try:
                print(f"Processing scenario {scenario_id} ({expected['name']})...")

                # Step 1: Create scenario config and load the data
                scenario_config = ScenarioConfig(
                    scenario_id=scenario_id, cache_dir=temp_path, force_download=True
                )

                # Explicitly load and extract the data
                print(f"  - Downloading and extracting data...")
                load_data(scenario_config)

                # Step 2: Create pipeline config and process the data
                pipeline_config = PipelineConfig(
                    scenario_name=scenario_id,
                    cache_dir=temp_path,
                    force_download=False,  # Already downloaded in step 1
                    output_format="list",  # Ensure we get lists, not NumPy arrays
                )

                print(f"  - Processing data...")
                result = process_data(pipeline_config)

                # Validation checks
                print(f"  - Validating results...")

                # Basic validation of results structure
                assert "time_values" in result
                assert "torque_values" in result
                assert "angle_values" in result
                assert "gradient_values" in result
                assert "step_values" in result
                assert "class_values" in result

                # Validate number of samples
                sample_count = len(result["class_values"])
                print(f"    Found {sample_count} samples")

                # Validate number of unique classes
                unique_classes = set(result["class_values"])
                print(f"    Found {len(unique_classes)} unique classes")

                # Check first few samples to verify data quality
                num_to_check = min(5, sample_count)
                print(f"    Checking {num_to_check} samples for data quality...")

                for i in range(num_to_check):
                    # Handle different result formats safely
                    time_values = result["time_values"][i]
                    torque_values = result["torque_values"][i]

                    if isinstance(time_values, np.ndarray):
                        assert time_values.size > 0, f"Empty time values in sample {i}"
                    else:
                        assert len(time_values) > 0, f"Empty time values in sample {i}"

                    if isinstance(torque_values, np.ndarray):
                        assert (
                            torque_values.size > 0
                        ), f"Empty torque values in sample {i}"
                    else:
                        assert (
                            len(torque_values) > 0
                        ), f"Empty torque values in sample {i}"

                print(
                    f"✓ Successfully processed {scenario_id}: {sample_count} samples with {len(unique_classes)} classes"
                )

            except Exception as e:
                pytest.fail(f"Failed to process scenario {scenario_id}: {str(e)}")
