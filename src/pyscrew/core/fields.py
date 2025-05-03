"""
Field definitions for screw operation data.

This module contains dataclasses that define the field names used throughout the PyScrew package:
1. JSON fields: Raw data as found in the JSON measurement files
2. CSV fields: Metadata and classification information from labels.csv
3. Output fields: Standardized field names used in the processing pipeline output

These constants provide a centralized reference for accessing data consistently
throughout the codebase and help maintain a clear separation between raw input data
and processed output data.
"""

from dataclasses import dataclass


@dataclass
class JsonFields:
    """
    Constants for field names in the JSON files containing screw operation data.

    These classes define the naming conventions used in the raw JSON data files
    from the screw driving control system. The field names preserve the original
    structure and naming conventions from the source data.

    Note: The string values (e.g. "id code", "time values") are pre-defined by
    the screw driving control and cannot be changed. Our constant names use a
    more consistent style and align with the CSV field naming (e.g., mapping JSON's
    "result" to WORKPIECE_RESULT to match the CSV's "workpiece_result" field).
    """

    @dataclass
    class Run:
        """
        Run-level metadata fields in the JSON.

        These fields describe the overall properties of a complete screw operation run
        and are found at the top level of each JSON file.

        Attributes:
            ID: Unique cycle number as recorded by the screw station
            DATE: Timestamp when the run was performed
            WORKPIECE_RESULT: Overall result from the screw driving control ("OK"/"NOK")
            WORKPIECE_ID: Data matrix code identifying the workpiece (14-digit)
            STEPS: Collection of tightening steps in the run
        """

        ID: str = "cycle"
        DATE: str = "date"
        WORKPIECE_RESULT: str = "result"
        WORKPIECE_ID: str = "id code"
        STEPS: str = "tightening steps"

    @dataclass
    class Step:
        """
        Step-level metadata fields in the JSON.

        These fields describe individual steps within a screw operation run.
        A typical operation consists of four steps: finding, thread forming,
        pre-tightening, and final tightening.

        Attributes:
            NAME: Step identifier (e.g., "Finding", "Thread Forming")
            STEP_TYPE: Type classification (typically "standard")
            WORKPIECE_RESULT: Result status ("OK"/"NOK") for this specific step
            QUALITY_CODE: Quality assessment code from the control system
            GRAPH: Measurement data dictionary containing time, torque, angle, and gradient values
        """

        NAME: str = "name"
        STEP_TYPE: str = "step type"
        WORKPIECE_RESULT: str = "result"
        QUALITY_CODE: str = "quality code"
        GRAPH: str = "graph"

    @dataclass
    class Measurements:
        """
        Measurement field names in the JSON graph data.

        These are the keys used in the GRAPH dictionary for each measurement type.
        These field names preserve the space-based naming convention from the
        raw JSON data.

        Attributes:
            TIME: Time measurements (0.0012s increments) recording when each measurement was taken
            TORQUE: Torque measurements (Nm) representing the rotational force applied
            ANGLE: Angle measurements (0.25° amplitude) representing the rotational position
            GRADIENT: Gradient measurements tracking the rate of change in torque vs. angle

        Note:
            The raw data also includes "angleRed values" and "torqueRed values" which are
            always [0,...,0] and are not used in processing.

            STEP and CLASS fields are added during later processing and are not
            present in the raw JSON data.

            We need to keep the spaces in these names to match the raw data structure.
        """

        TIME: str = "time values"
        TORQUE: str = "torque values"
        ANGLE: str = "angle values"
        GRADIENT: str = "gradient values"


@dataclass
class CsvFields:
    """
    Constants for field names in the labels CSV file.

    These fields connect the JSON measurement data with metadata about runs
    and provide classification information. The CSV file serves as the primary
    source of metadata and experimental context for each screw operation.

    Attributes:
        # Identifier fields
        RUN_ID: Unique identifier for each screw operation
        FILE_NAME: Name of the corresponding JSON file containing measurements

        # Classification field
        CLASS_VALUE: Scenario-specific classification label (e.g., "001_control-group")

        # Workpiece-related fields
        WORKPIECE_ID: Data matrix code identifying the workpiece (14-digit)
        WORKPIECE_DATE: Timestamp when the operation was recorded
        WORKPIECE_USAGE: Count of previous operations on this workpiece (0-24)
        WORKPIECE_RESULT: Result from screw program ("OK"/"NOK")
        WORKPIECE_LOCATION: Screw position in workpiece ("left" or "right")

        # Experiment-related fields
        SCENARIO_CONDITION: Experimental condition ("normal" or "faulty")
        SCENARIO_EXCEPTION: Flag for experimental issues (0: none, 1: exception)
    """

    # Identifier fields
    RUN_ID: str = "run_id"
    FILE_NAME: str = "file_name"

    # Classification field
    CLASS_VALUE: str = "class_value"

    # Workpiece-related fields
    WORKPIECE_ID: str = "workpiece_id"
    WORKPIECE_DATE: str = "workpiece_date"
    WORKPIECE_USAGE: str = "workpiece_usage"
    WORKPIECE_RESULT: str = "workpiece_result"
    WORKPIECE_LOCATION: str = "workpiece_location"

    # Experiment-related fields
    SCENARIO_CONDITION: str = "scenario_condition"
    SCENARIO_EXCEPTION: str = "scenario_exception"


@dataclass
class OutputFields:
    """
    Field names for the processed output data structure.

    This class defines standardized field names for the output data structure
    that is produced by the processing pipeline. It represents the transformation
    from raw space-based JSON field names to more standard underscore-based
    Python naming conventions.

    The output fields encompass three types of data:
    1. Transformed measurement data from the raw JSON
    2. Derived fields calculated during processing
    3. Metadata fields from the CSV labels file

    This provides a unified and consistent interface for accessing all
    data fields in the pipeline output, regardless of their source.

    Attributes:
        # Transformed measurement fields (from JSON)
        TIME_VALUES: Time measurements (0.0012s increments)
        TORQUE_VALUES: Torque measurements (Nm)
        ANGLE_VALUES: Angle measurements (0.25° amplitude)
        GRADIENT_VALUES: Gradient measurements (rate of change)

        # Derived fields (calculated during processing)
        STEP_VALUES: Integer indicators tracking which step each measurement originated from

        # Metadata fields (from CSV labels)
        CLASS_VALUES: Classification labels identifying the experimental condition
        WORKPIECE_LOCATION: Screw position in workpiece ("left" or "right")
        WORKPIECE_USAGE: Count of previous operations on this workpiece (0-24)
        WORKPIECE_RESULT: Result from screw program ("OK"/"NOK")
        SCENARIO_CONDITION: Experimental condition ("normal" or "faulty")
        SCENARIO_EXCEPTION: Flag for experimental issues (0 for "no issues")
    """

    # Transformed measurement fields (from JSON)
    TIME_VALUES: str = "time_values"
    TORQUE_VALUES: str = "torque_values"
    ANGLE_VALUES: str = "angle_values"
    GRADIENT_VALUES: str = "gradient_values"

    # Derived fields (determined during processing)
    STEP_VALUES: str = "step_values"

    # Metadata fields (from CSV labels)
    CLASS_VALUES: str = "class_values"
    WORKPIECE_LOCATION: str = "workpiece_location"
    WORKPIECE_USAGE: str = "workpiece_usage"
    WORKPIECE_RESULT: str = "workpiece_result"
    SCENARIO_CONDITION: str = "scenario_condition"
    SCENARIO_EXCEPTION: str = "scenario_exception"
