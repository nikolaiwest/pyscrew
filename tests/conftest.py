from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from pyscrew.core import JsonFields, ScrewDataset


@pytest.fixture(scope="session")
def temp_cache_dir():
    """Provide a temporary directory for test cache that persists across the test session."""
    with TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to the test data directory."""
    return Path(__file__).parent / "test_data"


class MockStep:
    """Mock ScrewStep for testing."""

    def __init__(self, step_number, time, torque, angle, gradient):
        self.step_number = step_number
        self.time = time
        self.torque = torque
        self.angle = angle
        self.gradient = gradient

    def get_values(self, measurement_name):
        return {
            JsonFields.Measurements.TIME: self.time,
            JsonFields.Measurements.TORQUE: self.torque,
            JsonFields.Measurements.ANGLE: self.angle,
            JsonFields.Measurements.GRADIENT: self.gradient,
        }[measurement_name]


class MockRun:
    """Mock ScrewRun for testing."""

    def __init__(self, steps, class_value):
        self.steps = steps
        self.class_value = class_value


@pytest.fixture
def basic_screw_dataset():
    """Basic dataset with single run, four steps of varying lengths."""
    # Initialize empty processed data structure
    processed_data = {
        JsonFields.Measurements.TIME: [],
        JsonFields.Measurements.TORQUE: [],
        JsonFields.Measurements.ANGLE: [],
        JsonFields.Measurements.GRADIENT: [],
    }

    dataset = ScrewDataset.__new__(ScrewDataset)
    dataset.processed_data = processed_data

    # Step 1 - base times
    step1_times = [round(0.0 + i * 0.0012, 4) for i in range(5)]
    step1 = MockStep(
        step_number=0,
        time=step1_times,
        torque=[1.0 + i * 0.5 for i in range(5)],
        angle=[0.0 + i * 0.25 for i in range(5)],
        gradient=[0.1 + i * 0.1 for i in range(5)],
    )

    # Step 2 - starts at last time of step1
    step2_times = [round(step1_times[-1] + i * 0.0012, 4) for i in range(15)]
    step2 = MockStep(
        step_number=1,
        time=step2_times,
        torque=[3.5 + i * 0.5 for i in range(15)],
        angle=[1.25 + i * 0.25 for i in range(15)],
        gradient=[0.6 + i * 0.1 for i in range(15)],
    )

    # Step 3 - starts at last time of step2
    step3_times = [round(step2_times[-1] + i * 0.0012, 4) for i in range(10)]
    step3 = MockStep(
        step_number=2,
        time=step3_times,
        torque=[11.0 + i * 0.5 for i in range(10)],
        angle=[5.0 + i * 0.25 for i in range(10)],
        gradient=[2.1 + i * 0.1 for i in range(10)],
    )

    # Step 4 - starts at last time of step3
    step4_times = [round(step3_times[-1] + i * 0.0012, 4) for i in range(5)]
    step4 = MockStep(
        step_number=3,
        time=step4_times,
        torque=[16.0 + i * 0.5 for i in range(5)],
        angle=[7.5 + i * 0.25 for i in range(5)],
        gradient=[3.1 + i * 0.1 for i in range(5)],
    )

    run = MockRun(steps=[step1, step2, step3, step4], class_value=0)
    dataset.screw_runs = [run]

    # Initialize processed_data with the step data
    for step in [step1, step2, step3, step4]:
        processed_data[JsonFields.Measurements.TIME].append(step.time)
        processed_data[JsonFields.Measurements.TORQUE].append(step.torque)
        processed_data[JsonFields.Measurements.ANGLE].append(step.angle)
        processed_data[JsonFields.Measurements.GRADIENT].append(step.gradient)

    return dataset
