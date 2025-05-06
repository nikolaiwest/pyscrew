"""
Scenario name resolver for PyScrew.
This module provides functionality to resolve different scenario name formats
(short codes, long names, and full names) to standardized name tuples.
"""

from typing import Dict, List, Tuple

from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)

# Direct scenario mappings with integer keys
# Format: ID: [short_name, long_name, full_name]
SCENARIO_MAPPINGS = {
    1: ["s01", "thread-degradation", "variations-in-thread-degradation"],
    2: ["s02", "surface-friction", "variations-in-surface-friction"],
    3: ["s03", "assembly-conditions-1", "variations-in-assembly-conditions-1"],
    4: ["s04", "assembly-conditions-2", "variations-in-assembly-conditions-2"],
    5: ["s05", "upper-workpiece", "variations-in-upper-workpiece-fabrication"],
    6: ["s06", "lower-workpiece", "variations-in-lower-workpiece-fabrication"],
}

# Test scenario mappings (won't be included in error messages)
TEST_SCENARIO_MAPPINGS = {
    99: ["s0X", "mock-data", "mock-data"],
}

# Build a flattened dictionary for direct name lookup
_NAME_TO_TUPLE: Dict[str, List[str]] = {}

# Add production scenarios
for _, name_tuple in SCENARIO_MAPPINGS.items():
    short_name, long_name, full_name = name_tuple
    _NAME_TO_TUPLE[short_name.lower()] = name_tuple
    _NAME_TO_TUPLE[long_name.lower()] = name_tuple
    _NAME_TO_TUPLE[full_name.lower()] = name_tuple

# Add test scenarios
for _, name_tuple in TEST_SCENARIO_MAPPINGS.items():
    short_name, long_name, full_name = name_tuple
    _NAME_TO_TUPLE[short_name.lower()] = name_tuple
    _NAME_TO_TUPLE[long_name.lower()] = name_tuple
    _NAME_TO_TUPLE[full_name.lower()] = name_tuple


def resolve_scenario_name(scenario: str) -> Tuple[str, str, str]:
    """
    Resolve any scenario identifier to standardized set of names.

    Args:
        scenario: A scenario identifier (short code, long name, or full name)

    Returns:
        Tuple of (short_name, long_name, full_name)

    Raises:
        ValueError: If the scenario identifier is not recognized
    """
    # Normalize input
    scenario_str = str(scenario).lower().strip()

    # Direct lookup in the mapping
    if scenario_str in _NAME_TO_TUPLE:
        result = _NAME_TO_TUPLE[scenario_str]

        # Log if input wasn't the short name
        if scenario_str != result[0].lower():
            logger.debug(
                f"Resolved scenario '{scenario}' to standard identifier '{result[0]}'"
            )

        return tuple(result)

    # If not found, provide helpful error message
    # Only show production scenario names in error message
    valid_names = sorted(set([v[0] for _, v in SCENARIO_MAPPINGS.items()]))
    raise ValueError(
        f"Unknown scenario identifier: '{scenario}'. "
        f"Valid identifiers include: {', '.join(valid_names)}"
    )
