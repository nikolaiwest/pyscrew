def test_process_data(scenario_name="s05"):
    """
    Test process_data with a minimal approach that mocks dataset creation.

    Args:
        scenario_name: Short name of the scenario to test

    Returns:
        True if test passes, False otherwise
    """
    import unittest.mock as mock

    from pyscrew.config import PipelineConfig
    from pyscrew.pipeline.processing import process_data

    # Create a minimal pipeline config
    pipeline_config = PipelineConfig(
        scenario_name=scenario_name,
        scenario_classes=None,
        measurements=None,
        screw_phases=None,
        screw_cycles=None,
        screw_positions="both",
        handle_duplicates="first",
        handle_missings="mean",
        target_length=1000,
        padding_value=0.0,
        padding_position="post",
        cutoff_position="post",
        output_format="list",
        cache_dir=None,
        force_download=False,
    )

    try:
        # Create mock dataset with dummy data
        with mock.patch("pyscrew.core.ScrewDataset.from_config") as mock_from_config:
            # Create a mock dataset that will be returned
            mock_dataset = mock.MagicMock()
            mock_dataset.processed_data = {
                "time_values": [0.0, 0.1, 0.2],
                "torque_values": [1.0, 2.0, 3.0],
                "angle_values": [0.5, 1.0, 1.5],
                "gradient_values": [0.1, 0.2, 0.3],
                "step_values": [1, 1, 1],
                "class_labels": ["normal", "normal", "normal"],
            }
            mock_from_config.return_value = mock_dataset

            # Also mock the pipeline's fit_transform to return the same mock dataset
            with mock.patch(
                "sklearn.pipeline.Pipeline.fit_transform", return_value=mock_dataset
            ):
                # Call the function under test
                result = process_data(pipeline_config)

                if result == mock_dataset.processed_data:
                    return True
                else:
                    return False

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False


if __name__ == "__main__":
    # Fix imports for running as a standalone script
    import os
    import sys

    # Ensure the pyscrew package is importable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Now we can import pyscrew modules

    # Run the test
    test_process_data()
