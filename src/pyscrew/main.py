from pathlib import Path
from typing import Dict, Optional, Union

from pyscrew.loading import DataLoader, DatasetRegistry


def get_data(scenario_name: str, cache_dir: Optional[Union[str, Path]] = None, force: bool = False) -> Path:
    """ Simple interface to get a dataset for a specific scenario."""
    loader = DataLoader(scenario_name, cache_dir)
    return loader.extract_data(force=force)

def list_scenarios() -> Dict[str, str]:
    """
    List all available scenarios and their descriptions.
    
    Returns:
        Dictionary mapping scenario names to their descriptions
    """
    return {name: config.description 
            for name, config in DatasetRegistry.DATASETS.items()}

def main(): 
    data = get_data("thread-degradation")
    print("Download finished")

if __name__ == "__main__":
    main()