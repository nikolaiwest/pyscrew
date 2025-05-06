from pathlib import Path
from typing import Dict, List, Optional, Union

from pyscrew.config import PipelineConfig, ScenarioConfig
from pyscrew.pipeline import load_data, process_data, validate_data
from pyscrew.utils import get_logger, resolve_scenario_name

logger = get_logger(__name__)


def list_scenarios() -> None:
    """
    List all available scenarios and their descriptions.

    Returns:
        Dictionary mapping scenario IDs to their descriptions.
    """

    # Get the directory where scenario YAML files are stored
    scenarios_dir = Path(__file__).parent / "scenarios"

    # Print header
    print("\n" + "=" * 135)
    print(
        f"{'ID':<6} {'NAME':<25} {'CLASSES':<10} {'OBSERVATIONS':<15} {'DESCRIPTION'}"
    )
    print("-" * 135)

    # Loop through the six scenario files (s01.yml to s06.yml)
    for scenario_id in ["s01", "s02", "s03", "s04", "s05", "s06"]:
        config_path = scenarios_dir / f"{scenario_id}.yml"

        if config_path.exists():
            try:
                # Load the scenario config
                scenario_config = ScenarioConfig(scenario_id)

                # Get scenario details
                long_name = scenario_config.get_name("long")
                class_count = len(scenario_config.classes)
                total_observations = scenario_config.get_total_observations()

                # Get first sentence of description (truncated if needed)
                full_desc = scenario_config.metadata.get("description", "")
                desc_first_sentence = full_desc.split(".")[0]
                if len(desc_first_sentence) > 50:
                    description = desc_first_sentence[:83] + "..."
                else:
                    description = desc_first_sentence

                # Print row with formatted columns
                print(
                    f"{scenario_id:<6} {long_name:<25} {class_count:<10} {total_observations:<15} {description[13:]}"
                )

            except Exception as e:
                print(f"{scenario_id:<6} {'ERROR: Could not load configuration':<80}")

    print("=" * 135)
    print(
        f"Learn more about the data here: {'https://github.com/nikolaiwest/screw_data'} \n"
    )


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
        cache_dir: Directory for caching downloaded data. If None, uses "src/pyscrew/downloads". The `cache_dir`
            parameter supports tilde expansion (e.g., "~/my_cache") which will be automatically expanded to the
            user's home directory.
        force_download: Force re-download even if cached

    Returns:
        Processed data in the requested format
    """
    # Resolve scenario name to standardized identifiers
    short_name, long_name, full_name = resolve_scenario_name(scenario)

    logger.info(f"Starting data retrieval for scenario: {short_name} ({long_name})")

    # Process cache_dir - we handle tilde expansion ONCE here at the entry point
    if cache_dir is not None:
        cache_dir_str = str(cache_dir)
        if cache_dir_str.startswith("~"):
            # Replace the tilde with the actual home directory
            expanded_path = str(Path.home()) + cache_dir_str[1:]
            cache_path = Path(expanded_path)
        else:
            cache_path = Path(cache_dir)
    else:
        # Use the default path
        package_root = Path(__file__).parent.parent  # This reaches src/pyscrew/
        cache_path = package_root / "pyscrew" / "downloads"

    logger.debug(f"Using cache directory: {cache_path}")

    # Initialize scenario config with short name and pass the resolved cache_path
    scenario_config = ScenarioConfig(
        short_name,
        cache_dir=cache_path,
        force_download=force_download,
    )

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
        cache_dir=cache_path,
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

    for s in ["s04", "s05", "s06"]:

        list_scenarios()

        data = get_data(scenario=s)

        print(f"Data retrieved successfully: n={len(data['torque_values'])}")
