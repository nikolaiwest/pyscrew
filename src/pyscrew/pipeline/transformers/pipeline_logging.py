"""
Pipeline state logging transformer for monitoring data processing stages.

This transformer provides visibility into data flow through the scikit-learn pipeline
by logging dataset characteristics at different processing stages. It can be inserted
at key points in the pipeline to track:
- Number of runs being processed
- Measurement availability and completeness
- Data structure consistency
- Metadata field presence

The transformer is passive (does not modify data) and is primarily used for:
- Debugging pipeline issues
- Validating data transformations
- Monitoring processing progress
- Confirming metadata preservation
"""

from sklearn.base import BaseEstimator, TransformerMixin

from pyscrew.config import PipelineConfig
from pyscrew.core import OutputFields, ScrewDataset
from pyscrew.utils import get_logger

logger = get_logger(__name__)


class PipelineLoggingTransformer(BaseEstimator, TransformerMixin):
    """
    Logs data structure and state during pipeline execution.

    This transformer can be inserted at any point in a scikit-learn pipeline
    to monitor the state of data as it flows through different processing stages.
    It performs no modifications to the data, only logging information about
    dataset size, measurement completeness, and metadata presence.

    Args:
        config: PipelineConfig object containing processing settings
        name: Optional identifier for this logging point in the pipeline, used to
              distinguish between multiple logging transformers in the same pipeline

    Attributes:
        config: Configuration settings for the pipeline
        outputs: OutputFields instance for accessing standardized field names
        name: String identifier for this transformer instance

    Example:
        >>> from sklearn.pipeline import Pipeline
        >>> pipeline = Pipeline([
        ...     ("input_state", PipelineLoggingTransformer(config, "Input")),
        ...     # ... processing transformers ...
        ...     ("output_state", PipelineLoggingTransformer(config, "Output"))
        ... ])
        >>> pipeline.fit_transform(dataset)
        Input - Fit: Dataset contains 100 runs
        Input - Transform: Processing 100 runs
        Output - Fit: Dataset contains 100 runs
        Output - Transform: Processing 100 runs
    """

    def __init__(self, config: PipelineConfig, name: str = "Pipeline logging"):
        """
        Initialize the transformer with config and a name for identification in logs.

        Args:
            config: PipelineConfig object containing processing settings
            name: Optional identifier for logging clarity
        """
        self.config = config
        self.outputs = OutputFields()
        self.name = name

    def fit(self, dataset: ScrewDataset, y=None) -> "PipelineLoggingTransformer":
        """
        Log dataset structure during pipeline fitting.

        This method logs:
        - Total number of runs in the dataset
        - Number of runs containing each measurement type
        - Presence of metadata fields
        - Selected configuration parameters relevant to this stage

        Args:
            dataset: ScrewDataset instance being processed
            y: Ignored, included for scikit-learn compatibility

        Returns:
            self, following scikit-learn transformer convention
        """
        logger.info(f"{self.name} - Fit: Dataset contains {len(dataset)} runs")

        # Check if processed_data exists
        if hasattr(dataset, "processed_data") and dataset.processed_data:
            # Log measurements information from processed_data
            measurement_fields = [
                self.outputs.TIME_VALUES,
                self.outputs.TORQUE_VALUES,
                self.outputs.ANGLE_VALUES,
                self.outputs.GRADIENT_VALUES,
                self.outputs.STEP_VALUES,
            ]

            for field in measurement_fields:
                if field in dataset.processed_data:
                    field_data = dataset.processed_data[field]
                    if isinstance(field_data, list):
                        logger.info(f"{field}: {len(field_data)} runs")
                    else:
                        logger.info(f"{field}: Present (not list type)")
                else:
                    logger.info(f"{field}: Not present")

            # Log metadata field presence
            metadata_fields = [
                self.outputs.CLASS_VALUES,
                self.outputs.WORKPIECE_LOCATION,
                self.outputs.WORKPIECE_USAGE,
                self.outputs.WORKPIECE_RESULT,
                self.outputs.SCENARIO_CONDITION,
                self.outputs.SCENARIO_EXCEPTION,
            ]

            for field in metadata_fields:
                if field in dataset.processed_data:
                    field_data = dataset.processed_data[field]
                    if isinstance(field_data, list):
                        logger.info(f"{field}: {len(field_data)} values")
                    else:
                        logger.info(f"{field}: Present (not list type)")
                else:
                    logger.info(f"{field}: Not present")
        else:
            # Log measurement info using get_values for raw dataset
            for measurement in [
                "time values",
                "torque values",
                "angle values",
                "gradient values",
            ]:
                try:
                    values = dataset.get_values(measurement)
                    logger.info(f"{measurement}: {len(values)} runs")
                except Exception as e:
                    logger.warning(f"Could not get values for {measurement}: {str(e)}")

        # Log relevant configuration parameters
        if self.config.measurements:
            logger.info(f"Selected measurements: {self.config.measurements}")
        if self.config.screw_phases:
            logger.info(f"Selected screw phases: {self.config.screw_phases}")

        return self

    def transform(self, dataset: ScrewDataset) -> ScrewDataset:
        """
        Log dataset state during transformation and return unchanged.

        Args:
            dataset: ScrewDataset instance to examine

        Returns:
            Unmodified dataset, following scikit-learn transformer convention
        """
        logger.info(f"{self.name} - Transform: Processing {len(dataset)} runs")

        # Check if processed_data has been populated
        if hasattr(dataset, "processed_data") and dataset.processed_data:
            field_count = len(dataset.processed_data)
            measurement_fields = [
                field
                for field in dataset.processed_data.keys()
                if field.endswith("_values")
            ]
            metadata_fields = [
                field
                for field in dataset.processed_data.keys()
                if not field.endswith("_values")
            ]

            logger.info(
                f"Dataset contains {field_count} fields: "
                f"{len(measurement_fields)} measurements, "
                f"{len(metadata_fields)} metadata fields"
            )

            # Log measurement dimensions if available
            for field in measurement_fields:
                if field in dataset.processed_data and dataset.processed_data[field]:
                    field_data = dataset.processed_data[field]
                    if isinstance(field_data, list) and field_data:
                        first_item = field_data[0]
                        if isinstance(first_item, list):
                            avg_length = sum(len(item) for item in field_data) / len(
                                field_data
                            )
                            logger.info(
                                f"{field}: {len(field_data)} runs, avg {avg_length:.1f} points per run"
                            )

        return dataset
