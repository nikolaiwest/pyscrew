from pathlib import Path
from .loading import DataLoader

class PyScrew:
    """
    Main class for handling research data through PyScrew.
    Provides a simplified interface for downloading and accessing data from Zenodo.
    """
    
    def __init__(self, cache_dir: Path = None):
        """
        Initialize PyScrew with optional custom cache directory.
        
        Args:
            cache_dir: Optional custom directory for caching data.
                      If not provided, defaults to ~/.cache/pyscrew
        """
        self.loader = DataLoader(cache_dir=cache_dir)

    def get_data_directory(self) -> Path:
        """
        Download and extract the data if needed, then return the path to the data directory.
        
        Returns:
            Path to the directory containing the extracted data files
        """
        return self.loader.get_data()

    def list_files(self) -> list[str]:
        """
        List all available files in the dataset.
        
        Returns:
            List of filenames available in the extracted data
        """
        return self.loader.list_available_files()