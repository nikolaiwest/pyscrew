def test_validate_data(scenario_name="s05"):
    """
    Test validate_data with a minimal approach that mocks the data structure.

    Args:
        scenario_name: Short name of the scenario to test

    Returns:
        True if test passes, False otherwise
    """
    from pyscrew.config import PipelineConfig
    from pyscrew.pipeline.validating import validate_data

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
        # Create mock data with dummy values using nested lists
        mock_data = {
            "time_values": [[0.0, 0.1, 0.2], [0.0, 0.1, 0.2], [0.0, 0.1, 0.2]],
            "torque_values": [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]],
            "angle_values": [[0.5, 1.0, 1.5], [0.5, 1.0, 1.5], [0.5, 1.0, 1.5]],
            "gradient_values": [[0.1, 0.2, 0.3], [0.1, 0.2, 0.3], [0.1, 0.2, 0.3]],
            "step_values": [1, 1, 1],
            "class_labels": ["normal", "normal", "normal"],
        }

        # Call the function under test
        validate_data(mock_data, pipeline_config)
        return True

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
    test_validate_data()
