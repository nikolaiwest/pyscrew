"""
Transformer for organizing raw screw step data into measurement collections.

This transformer restructures the hierarchical step-based data from ScrewDataset
into measurement-oriented collections for easier analysis. It handles the
transformation from:

    ScrewRun
        └── ScrewStep
            └── Measurements (time, torque, angle, gradient)

to:

    processed_data
        ├── time_values: List[List[float]]     # Outer list: runs, Inner list: values
        ├── torque_values: List[List[float]]
        ├── angle_values: List[List[float]]
        ├── gradient_values: List[List[float]]
        ├── step_values: List[List[int]]       # Tracks measurement origins
        ├── class_values: List[str]            # Class labels for each run
        ├── workpiece_location: List[str]      # Screw position (left/right)
        ├── workpiece_usage: List[int]         # Previous operations count
        ├── workpiece_result: List[str]        # Operation result (OK/NOK)
        ├── scenario_condition: List[str]      # Experiment condition (normal/faulty)
        └── scenario_exception: List[int]      # Exception flags (0: none)
"""

from sklearn.base import BaseEstimator, TransformerMixin

from pyscrew.config import PipelineConfig
from pyscrew.core import JsonFields, OutputFields, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class UnpackStepsTransformer(BaseEstimator, TransformerMixin):
    """
    Organizes raw step-based data into measurement collections.

    This transformer flattens the hierarchical step structure of ScrewDataset
    into measurement-oriented collections, making the data more suitable for
    analysis and processing. It maintains the run-level organization while
    concatenating measurements from individual steps.

    The transformer uses configuration parameters to determine:
    - Which measurements to include (config.measurements), e.g. "torque"
    - Which screw phases to include (config.screw_phases), e.g. 1, 2, etc.

    Note: Filtering by scenario_classes and screw_positions is already
    handled at the dataset creation level.

    Args:
        config: PipelineConfig object containing processing settings

    Attributes:
        config: Configuration settings for the pipeline
        measurements: JsonFields.Measurements instance for accessing raw field names
        outputs: OutputFields instance for accessing standardized output field names
    """

    def __init__(self, config: PipelineConfig):
        """Initialize transformer with pipeline configuration."""
        self.config = config
        self.measurements = JsonFields.Measurements()
        self.outputs = OutputFields()

    def fit(self, dataset: ScrewDataset, y=None) -> "UnpackStepsTransformer":
        """
        Implement fit method for scikit-learn compatibility.

        This transformer is stateless, so fit() does nothing but return self.

        Args:
            dataset: Input dataset (unused)
            y: Ignored, included for scikit-learn compatibility

        Returns:
            self, following scikit-learn transformer convention
        """
        return self

    def _get_selected_measurements(self) -> list:
        """
        Get the list of measurements to include based on config.

        Returns:
            List of measurement field names to include
        """
        all_measurements = [
            self.measurements.TIME,
            self.measurements.TORQUE,
            self.measurements.ANGLE,
            self.measurements.GRADIENT,
        ]

        # If no measurements specified, include all
        if not self.config.measurements:
            return all_measurements

        # Map from string names (user inputs) to JsonFields constants
        measurement_map = {
            "time": self.measurements.TIME,
            "torque": self.measurements.TORQUE,
            "angle": self.measurements.ANGLE,
            "gradient": self.measurements.GRADIENT,
        }

        # Return only the selected measurements
        return [
            measurement_map[m] for m in self.config.measurements if m in measurement_map
        ]

    def _get_output_field_for_measurement(self, measurement: str) -> str:
        """
        Map raw measurement name to standardized output field name.

        Args:
            measurement: Raw measurement field name from JsonFields.Measurements

        Returns:
            Corresponding standardized field name from OutputFields
        """
        # Map from raw JSON measurement fields to standardized output fields
        mapping = {
            self.measurements.TIME: self.outputs.TIME_VALUES,
            self.measurements.TORQUE: self.outputs.TORQUE_VALUES,
            self.measurements.ANGLE: self.outputs.ANGLE_VALUES,
            self.measurements.GRADIENT: self.outputs.GRADIENT_VALUES,
        }
        return mapping.get(measurement)

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """
        Transform step-based data into measurement collections.

        This method:
        1. Selects measurements based on configuration
        2. Filters steps based on phase
        3. Flattens and organizes the data into measurement collections
        4. Adds output fields from each run

        Args:
            dataset: Input dataset containing step-based measurements
            (Already filtered by scenario_classes and screw_positions)

        Returns:
            Dataset with populated processed_data containing filtered measurements and metadata
        """
        # Get measurements to include based on config
        selected_measurements = self._get_selected_measurements()
        logger.info(f"Selected measurements: {selected_measurements}")

        # Initialize processed data dictionary with output field names
        dataset.processed_data = {
            self._get_output_field_for_measurement(m): [] for m in selected_measurements
        }

        # Add output fields to provide metadata for the run
        dataset.processed_data[self.outputs.STEP_VALUES] = []
        dataset.processed_data[self.outputs.CLASS_VALUES] = []
        dataset.processed_data[self.outputs.WORKPIECE_LOCATION] = []
        dataset.processed_data[self.outputs.WORKPIECE_USAGE] = []
        dataset.processed_data[self.outputs.WORKPIECE_RESULT] = []
        dataset.processed_data[self.outputs.SCENARIO_CONDITION] = []
        dataset.processed_data[self.outputs.SCENARIO_EXCEPTION] = []

        # Process each run in the dataset (already filtered by scenario_classes)
        for run in dataset.screw_runs:
            # Initialize data structures for this run using output field names
            run_data = {
                self._get_output_field_for_measurement(m): []
                for m in selected_measurements
            }
            run_steps = []

            # Process each step in the run
            for step_idx, step in enumerate(run.steps):
                # Filter by phase if specified
                phase_num = step_idx + 1  # Convert 0-based to 1-based
                if (
                    self.config.screw_phases
                    and phase_num not in self.config.screw_phases
                ):
                    continue

                # Get step length once for efficiency
                step_length = len(step.get_values(self.measurements.TIME))

                # Extract and append measurements for this step
                for measurement in selected_measurements:
                    values = step.get_values(measurement)
                    output_field = self._get_output_field_for_measurement(measurement)
                    run_data[output_field].extend(values)

                # Record step origins
                run_steps.extend([step_idx] * step_length)

            # Only include the run if it has data after filtering
            if run_data[
                self._get_output_field_for_measurement(selected_measurements[0])
            ]:
                # Add the run's data to the dataset
                for measurement in selected_measurements:
                    output_field = self._get_output_field_for_measurement(measurement)
                    dataset.processed_data[output_field].append(run_data[output_field])

                # Add step values and class value
                dataset.processed_data[self.outputs.STEP_VALUES].append(run_steps)
                dataset.processed_data[self.outputs.CLASS_VALUES].append(
                    run.class_value
                )

                # Add metadata fields
                dataset.processed_data[self.outputs.WORKPIECE_LOCATION].append(
                    run.workpiece_location
                )
                dataset.processed_data[self.outputs.WORKPIECE_USAGE].append(
                    run.workpiece_usage
                )
                dataset.processed_data[self.outputs.WORKPIECE_RESULT].append(
                    run.workpiece_result
                )
                dataset.processed_data[self.outputs.SCENARIO_CONDITION].append(
                    run.scenario_condition
                )
                dataset.processed_data[self.outputs.SCENARIO_EXCEPTION].append(
                    run.scenario_exception
                )

        # Log the results
        num_runs = len(dataset.processed_data[self.outputs.CLASS_VALUES])
        if num_runs > 0:
            first_field = self._get_output_field_for_measurement(
                selected_measurements[0]
            )
            total_points = sum(
                len(values) for values in dataset.processed_data[first_field]
            )
            logger.info(
                f"Unpacked {num_runs} runs with {total_points:,} total measurements"
            )

            # Log phase filtering effects if applicable
            if self.config.screw_phases:
                logger.info(
                    f"Applied phase filtering: included phases {self.config.screw_phases}"
                )
        else:
            logger.warning("No data remains after filtering. Check filter criteria.")

        return dataset
