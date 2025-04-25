from pathlib import Path
from typing import Dict, List, Optional, Union

from pyscrew.config import PipelineConfig, ScenarioConfig
from pyscrew.pipeline import load_data, process_data, validate_data
from pyscrew.utils import get_logger, resolve_scenario_name

logger = get_logger(__name__)


def list_scenarios() -> Dict[str, str]:
    """List all available scenarios and their descriptions."""
    # Implementation to be added
    pass


def get_data(
    scenario: str,
    *,
    # Filtering options
    scenario_classes: Optional[List[str]] = None,
    return_measurements: Optional[List[str]] = None,
    screw_phase: Optional[List[int]] = None,
    screw_cycles: Optional[List[int]] = None,
    screw_positions: str = "both",
    # Processing options
    handle_duplicates: str = "first",
    handle_missings: str = "mean",
    target_length: int = 1000,
    padding_value: float = 0.0,
    padding_position: str = "post",
    cutoff_position: str = "post",
    output_format: str = "list",
    # System options
    cache_dir: Optional[Union[str, Path]] = None,
    force_download: bool = False,
) -> Dict[str, List[float]]:
    """
    Load and process screw driving data from a specific scenario.

    Args:
        scenario: Name of the scenario to load (short code, long name, or full name)
        scenario_classes: List of scenario classes to include. None means "all"
        return_measurements: List of measurements to return. Options are ["torque", "angle", "gradient", "time"].
            None means "all measurements"
        screw_phase: List of screw phases to include. Options are [1,2,3,4]. None means "all phases"
        screw_cycles: List of cycle numbers to include. None means "all cycles"
        screw_position: Position to analyze. Options are ["left", "right" or "both"]
        handle_duplicates: How to remove negative values and what to keep. Options are ["first", "last", "mean", None].
            None means no duplicates are removed.
        handle_missings: Whether to interpolate missing values. Options are ["mean", "zero" or a float value]
            Time is recorded at 0.0012s intervals. None means no values are interpolated.
        target_length: Desired length for all sequences (int)
        padding_value: Value to use for padding shorter sequences (default: 0.0)
        padding_position: Position to add padding ('pre' or 'post', default: 'post')
        cutoff_position: Position to truncate longer sequences ('pre' or 'post', default: 'post')
        output_format: Format of the output data. Current option is only "list".
            "numpy" and "dataframe" will be added in a future release, but require equal time series lengths.
        cache_dir: Directory for caching downloaded data
        force_download: Force re-download even if cached

    Returns:
        Processed data in the requested format

    Examples:
        >>> # Get all data for a scenario using short code
        >>> data = get_data("s01")

        >>> # Get all data for a scenario using long name
        >>> data = get_data("thread-degradation")

        >>> # Get all data for a scenario using full name
        >>> data = get_data("variations-in-thread-degradation")

        >>> # Get specific measurements for certain phases
        >>> data = get_data(
        ...     "s01",
        ...     return_measurements=["torque", "angle"],
        ...     screw_phase=[1, 2],
        ...     output_format="dataframe"
        ... )
    """
    # Resolve scenario name to standardized identifiers
    short_name, long_name, full_name = resolve_scenario_name(scenario)

    logger.info(f"Starting data retrieval for scenario: {short_name} ({long_name})")

    # Initialize scenario config with short name (for YAML file lookup in scenarios/)
    scenario_config = ScenarioConfig(short_name)

    # Initialize pipeline config
    pipeline_config = PipelineConfig(
        scenario_name=short_name,
        scenario_classes=scenario_classes,
        measurements=return_measurements,
        screw_phases=screw_phase,
        screw_cycles=screw_cycles,
        screw_positions=screw_positions,
        handle_duplicates=handle_duplicates,
        handle_missings=handle_missings,
        target_length=target_length,
        padding_value=padding_value,
        padding_position=padding_position,
        cutoff_position=cutoff_position,
        output_format=output_format,
        cache_dir=Path(cache_dir) if cache_dir else None,
        force_download=force_download,
    )

    try:
        # Step 1: Load and extract data if needed
        logger.debug("Loading raw data")
        load_data(scenario_config)

        # Step 2: Process the data according to config
        logger.debug("Processing raw data")
        data = process_data(pipeline_config)

        # Step 3: Validate processed data
        logger.debug("Validating processed data")
        validate_data(data, pipeline_config)

        return data

    except Exception as e:
        logger.error(f"Error processing scenario {scenario_config.scenario_id}: {e}")
        raise


if __name__ == "__main__":
    data = get_data(scenario="s01")
    print(f"Data retrieved successfully: n={len(data.get('torque_values', []))}")
