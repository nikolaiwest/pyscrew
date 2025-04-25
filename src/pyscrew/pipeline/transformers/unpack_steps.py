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
        ├── time values: List[List[float]]     # Outer list: runs, Inner list: values
        ├── torque values: List[List[float]]
        ├── angle values: List[List[float]]
        ├── gradient values: List[List[float]]
        ├── step values: List[List[int]]       # Optional, tracks measurement origins
        └── class labels: List[int]     # Class labels for each run
"""

from sklearn.base import BaseEstimator, TransformerMixin

from pyscrew.core import JsonFields, ScrewDataset
from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class UnpackStepsTransformer(BaseEstimator, TransformerMixin):
    """
    Organizes raw step-based data into measurement collections.

    This transformer flattens the hierarchical step structure of ScrewDataset
    into measurement-oriented collections, making the data more suitable for
    analysis and processing. It maintains the run-level organization while
    concatenating measurements from individual steps.

    Args:
        include_steps: If True, adds step indicators that map each measurement
                      back to its originating step number (0,1,2,3)
        include_classes: If True, adds class labels for each run

    Attributes:
        include_steps: Boolean controlling step indicator inclusion
        include_classes: Boolean controlling class label inclusion
        measurements: JsonFields.Measurements instance for accessing field names

    Example:
        >>> transformer = UnpackStepsTransformer(include_steps=True, include_classes=True)
        >>> processed = transformer.fit_transform(dataset)
        >>> # Access measurements for first run
        >>> first_run_torque = processed.processed_data[measurements.TORQUE][0]
        >>> first_run_steps = processed.processed_data[measurements.STEP][0]
        >>> first_run_class = processed.processed_data["class_value"][0]
        >>> print(f"Run has {len(first_run_torque)} measurements")
        >>> print(f"From steps: {set(first_run_steps)}")  # e.g., {0,1,2,3}
        >>> print(f"Class label: {first_run_class}")
    """

    def __init__(self, include_steps: bool = True, include_classes: bool = True):
        """Initialize transformer with step tracking configuration."""
        self.include_steps = include_steps
        self.include_classes = include_classes
        self.measurements = JsonFields.Measurements()

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

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """
        Transform step-based data into measurement collections.

        This method:
        1. Initializes measurement collections for each type
        2. Pre-allocates lists for each run
        3. Processes each run's steps, concatenating measurements
        4. Optionally adds step indicators
        5. Adds class labels for each run

        Args:
            dataset: Input dataset containing step-based measurements

        Returns:
            Dataset with populated processed_data containing measurement collections
        """
        # Initialize all measurement lists (as provided by JsonFields)
        measurements = [
            self.measurements.TIME,
            self.measurements.TORQUE,
            self.measurements.ANGLE,
            self.measurements.GRADIENT,
        ]

        # Initialize processed data dictionary
        dataset.processed_data = {m: [] for m in measurements}

        if self.include_steps:
            dataset.processed_data[self.measurements.STEP] = []

        if self.include_classes:
            dataset.processed_data[self.measurements.CLASS] = []

        # Pre-allocate lists for each run
        for _ in dataset.screw_runs:
            for measurement in measurements:
                dataset.processed_data[measurement].append([])
            if self.include_steps:
                dataset.processed_data[self.measurements.STEP].append([])

        # Process runs and steps
        for run_idx, run in enumerate(dataset.screw_runs):
            for step_idx, step in enumerate(run.steps):
                # Get length once since we'll use it multiple times
                step_length = len(step.get_values(self.measurements.TIME))

                # Process all measurements for this step
                for measurement in measurements:
                    values = step.get_values(measurement)
                    dataset.processed_data[measurement][run_idx].extend(values)

                # Add step indicators if requested
                if self.include_steps:
                    dataset.processed_data[self.measurements.STEP][run_idx].extend(
                        [step_idx] * step_length
                    )
            # Add class indicators if requested (one per run)
            if self.include_classes:
                dataset.processed_data[self.measurements.CLASS].append(run.class_value)

        return dataset
