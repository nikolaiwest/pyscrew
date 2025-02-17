from pyscrew.transformers import UnpackStepsTransformer
from pyscrew.utils.data_model import JsonFields


def test_basic_unpacking(basic_screw_dataset):
    """Test basic unpacking of steps into measurements."""
    transformer = UnpackStepsTransformer()
    result = transformer.transform(basic_screw_dataset)

    # Check that we have one run's worth of data
    assert len(result.processed_data[JsonFields.Measurements.TIME]) == 1

    # Check total length
    first_run = 0
    assert len(result.processed_data[JsonFields.Measurements.TIME][first_run]) == 35

    # Check some key values from different steps
    time_values = result.processed_data[JsonFields.Measurements.TIME][first_run]
    # torque_values = result.processed_data[JsonFields.Measurements.TORQUE][first_run]

    # Start of each step
    assert time_values[0] == 0.0  # Start of step 1
    assert time_values[5] == 0.0048  # Start of step 2 (was step1's end)
    assert time_values[20] == 0.0216  # Start of step 3 (was step2's end)
    assert time_values[30] == 0.0324  # Start of step 4 (was step3's end)
    assert time_values[-1] == 0.0372  # Last time point (end of sequence)

    # Check torque values from different steps
    torque_values = result.processed_data[JsonFields.Measurements.TORQUE][first_run]
    assert torque_values[0] == 1.0  # Start of step 1 (initial)
    assert torque_values[5] == 3.5  # Start of step 2
    assert torque_values[20] == 11.0  # Start of step 3
    assert torque_values[30] == 16.0  # Start of step 4
    assert torque_values[-1] == 18.0  # Last torque point

    # Check step indicators are added correctly
    step_values = result.processed_data[JsonFields.Measurements.STEP][first_run]
    assert len(step_values) == 35  # Same length as measurements
    assert step_values[:5] == [0] * 5  # First 5 from step 1
    assert step_values[5:20] == [1] * 15  # Next 15 from step 2
    assert step_values[20:30] == [2] * 10  # Next 10 from step 3
    assert step_values[30:] == [3] * 5  # Last 5 from step 4

    # Check class labels are preserved
    assert JsonFields.Measurements.CLASS in result.processed_data
    # We shoudl see one label per run
    assert result.processed_data[JsonFields.Measurements.CLASS] == [0]
