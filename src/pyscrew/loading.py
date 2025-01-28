import os
import tarfile
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from tqdm import tqdm


class DataLoader:
    def __init__(self, cache_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the Zenodo loader for the test dataset.
        
        Args:
            cache_dir: Optional directory for storing downloaded and extracted files.
                      Defaults to ~/.cache/pyscrew
        """
        # TODO: Set up the Zenodo record ID, file name, and download URL
        self.record_id = "14729548"
        self.file_name = "test_upload.tar"
        self.download_url = f"https://zenodo.org/records/{self.record_id}/files/{self.file_name}?download=1"
        
        # Set up cache directory structure
        if cache_dir is None:
            cache_dir = Path.home() / '.cache' / 'pyscrew'
        self.cache_dir = Path(cache_dir)
        self.tar_cache = self.cache_dir / 'archives'  # For storing TAR files
        self.data_cache = self.cache_dir / 'extracted'  # For extracted contents
        
        # Create cache directories
        self.tar_cache.mkdir(parents=True, exist_ok=True)
        self.data_cache.mkdir(parents=True, exist_ok=True)

    def get_data(self, force_download: bool = False) -> Path:
        """
        Download the TAR file if needed and extract its contents.
        
        Args:
            force_download: If True, redownload even if already in cache
        
        Returns:
            Path to the directory containing extracted files
        """
        tar_path = self.tar_cache / self.file_name
        
        # Check if we need to download
        if force_download or not tar_path.exists():
            self._download_tar(tar_path)
        
        # Check if we need to extract
        if force_download or not self._is_extracted():
            self._extract_tar(tar_path)
            
        return self.data_cache

    def _download_tar(self, target_path: Path) -> None:
        """
        Download the TAR file from Zenodo with progress tracking.
        
        Args:
            target_path: Where to save the downloaded file
        """
        print(f"Downloading {self.file_name} from Zenodo...")
        
        response = requests.get(self.download_url, stream=True)
        response.raise_for_status()
        
        # Get file size for progress bar
        total_size = int(response.headers.get('content-length', 0))
        
        # Download with progress bar
        with open(target_path, 'wb') as file, \
             tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    size = file.write(chunk)
                    pbar.update(size)

    def _extract_tar(self, tar_path: Path) -> None:
        """
        Extract the contents of the TAR file to the data cache directory.
        
        Args:
            tar_path: Path to the downloaded TAR file
        """
        print(f"Extracting {self.file_name}...")
        
        # Clear the extraction directory first
        for item in self.data_cache.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                import shutil
                shutil.rmtree(item)
        
        # Extract with progress tracking
        with tarfile.open(tar_path, 'r') as tar:
            members = tar.getmembers()
            for member in tqdm(members, desc="Extracting files"):
                tar.extract(member, self.data_cache)

    def _is_extracted(self) -> bool:
        """
        Check if the TAR contents are already extracted in the cache.
        
        Returns:
            True if the contents appear to be extracted, False otherwise
        """
        # Simple check - see if the extraction directory has any contents
        return any(self.data_cache.iterdir())

    def list_available_files(self) -> List[str]:
        """
        List all files available in the extracted data.
        
        Returns:
            List of filenames in the extracted data directory
        """
        # Ensure data is available
        self.get_data()
        
        # Recursively list all files
        files = []
        for path in self.data_cache.rglob('*'):
            if path.is_file():
                files.append(str(path.relative_to(self.data_cache)))
        return files