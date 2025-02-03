"""
Data loading module for PyScrew.

This module provides functionality for downloading and extracting datasets from Zenodo.
It handles secure file operations, archive extraction, and dataset management.

Key features:
    - Secure downloading and extraction of archives (ZIP, TAR, RAR)
    - Checksum verification for data integrity
    - Caching mechanism to prevent redundant downloads
    - Protection against path traversal attacks
    - Cross-platform compatibility (Windows/Unix)

Usage:
    loader = DataLoader("scenario_name")
    extracted_path = loader.extract_data()

The module maintains a two-tier cache structure:
    ~/.cache/pyscrew/
    ├── archives/     # Stores downloaded compressed files
    └── extracted/    # Stores extracted datasets
"""

import hashlib
import os
import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union

import rarfile
import requests
import yaml
from tqdm import tqdm

from pyscrew.utils.logger import get_logger

logger = get_logger(__name__)


class SecurityError(Exception):
    """
    Raised when a security violation is detected during extraction.

    Common triggers:
        - Path traversal attempts in archive files
        - Insufficient permissions
        - Suspicious file attributes
    """

    pass


class ExtractionError(Exception):
    """
    Raised when archive extraction fails.

    Common triggers:
        - Corrupted archive files
        - Unsupported compression methods
        - Missing system dependencies
        - Insufficient disk space
    """

    pass


class ChecksumError(Exception):
    """
    Raised when file checksum verification fails.

    Common triggers:
        - MD5 hash mismatch
        - Incomplete downloads
        - File corruption during transfer
        - File system errors
    """

    pass


class DownloadError(Exception):
    """
    Raised when file download fails.

    Common triggers:
        - Network connectivity issues
        - Server errors (5xx responses)
        - Authentication failures
        - Invalid or missing resources
    """

    pass


@dataclass(frozen=True)
class DatasetConfig:
    """
    Configuration for a Zenodo dataset.

    Attributes:
        record_id: Unique identifier for the Zenodo record
        file_name: Name of the file to download
        md5_checksum: Expected MD5 hash for verification
        description: Human-readable description of the dataset
    """

    record_id: str
    file_name: str
    md5_checksum: str
    description: str


class ArchiveFormat(Enum):
    """
    Supported archive formats.

    Using Enum ensures type safety and prevents string comparison errors.
    The values correspond to file extensions including the dot.
    """

    TAR = ".tar"
    ZIP = ".zip"
    RAR = ".rar"


class DatasetRegistry:
    """
    Registry of all available datasets.

    This class manages the catalog of available datasets and their configurations.
    Dataset definitions are loaded from a YAML file in the same directory.

    The YAML structure should be:
    ```yaml
    datasets:
      scenario_name:
        record_id: "1234567"
        file_name: "data.tar"
        md5_checksum: "abc123..."
        description: "Dataset description"
    ```
    """

    # Base URL for Zenodo API (unlikely to change but kept as class variable)
    # for easier updates if needed
    ZENODO_BASE_URL = "https://zenodo.org/records"
    _datasets: Optional[Dict[str, DatasetConfig]] = None

    @classmethod
    def _load_scenarios(cls) -> Dict[str, DatasetConfig]:
        """
        Load scenarios from YAML file.

        Returns:
            Dictionary mapping scenario names to their configurations

        Raises:
            FileNotFoundError: If scenarios.yml is not found
            ValueError: If YAML structure is invalid
        """
        try:
            # Look for scenarios.yml in the same directory as this file
            yaml_path = Path(__file__).parent / "scenarios.yml"

            if not yaml_path.exists():
                raise FileNotFoundError(f"Scenarios file not found: {yaml_path}")

            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict) or "datasets" not in data:
                raise ValueError("Invalid scenarios.yml format: missing 'datasets' key")

            # Convert dictionary to DatasetConfig objects
            return {
                name: DatasetConfig(**config)
                for name, config in data["datasets"].items()
            }

        except Exception as e:
            logger.error(f"Error loading scenarios: {str(e)}")
            raise

    @classmethod
    def get_datasets(cls) -> Dict[str, DatasetConfig]:
        """Get all dataset configurations, loading from file if necessary."""
        if cls._datasets is None:
            cls._datasets = cls._load_scenarios()
        return cls._datasets

    @classmethod
    def get_config(cls, scenario_name: str) -> DatasetConfig:
        """Get configuration for a specific scenario."""
        datasets = cls.get_datasets()

        if scenario_name not in datasets:

            available = ", ".join(f"'{name}'" for name in datasets.keys())
            raise ValueError(
                f"Unknown scenario: '{scenario_name}'. "
                f"Available scenarios are: {available}"
            )
        return datasets[scenario_name]

    @classmethod
    def get_download_url(cls, scenario_name: str) -> str:
        """Generate download URL for a dataset."""
        config = cls.get_config(scenario_name)
        return f"{cls.ZENODO_BASE_URL}/{config.record_id}/files/{config.file_name}?download=1"


class DataLoader:
    """
    Handles downloading and extracting datasets from Zenodo.

    This class manages the entire lifecycle of dataset retrieval:
    1. Downloads the archive if not cached
    2. Verifies the checksum
    3. Extracts the contents securely
    4. Manages the cache structure

    The cache structure uses two directories:
    - archives/: For storing downloaded compressed files
    - extracted/: For storing the extracted data

    Args:
        scenario_name: Name of the scenario to load
        cache_dir: Optional directory for storing downloaded and extracted files.
                  Defaults to ~/.cache/pyscrew

    Security features:
        - Checksum verification
        - Path traversal protection
        - Secure file permissions
        - Safe archive extraction
    """

    # Using a large chunk size (8MB) optimizes both download speed and memory usage
    # Small chunks = more iterations and overhead
    # Large chunks = more memory usage and potential timeout issues
    CHUNK_SIZE = 8 * 1024 * 1024

    def __init__(
        self, scenario_name: str, cache_dir: Optional[Union[str, Path]] = None
    ):
        """
        Initialize the data loader for a specific scenario.

        Args:
            scenario_name: Name of the scenario to load
            cache_dir: Optional directory for storing downloaded and extracted files.
                      Defaults to ~/.cache/pyscrew
        """
        config = DatasetRegistry.get_config(scenario_name)

        self.scenario_name = scenario_name
        self.record_id = config.record_id
        self.file_name = config.file_name
        self.download_url = DatasetRegistry.get_download_url(scenario_name)
        self.md5_checksum = config.md5_checksum

        # Set up cache directory structure
        # Using Path objects throughout for cross-platform compatibility
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "pyscrew"
        self.cache_dir = Path(cache_dir)
        self.archive_cache = self.cache_dir / "archives"
        self.data_cache = self.cache_dir / "extracted"

        # Create cache directories with secure permissions to prevent tampering
        self._create_secure_directory(self.archive_cache)
        self._create_secure_directory(self.data_cache)

    def get_data(self, force: bool = False) -> Path:
        """
        Get the dataset, downloading if necessary.

        This method manages the complete dataset acquisition process:
        1. Validates the archive format is supported
        2. Downloads the file if needed (or if force=True)
        3. Verifies archive integrity
        4. Implements a single retry on verification failure

        The retry mechanism provides resilience against:
        - Corrupted downloads
        - Network interruptions
        - Incomplete transfers

        Args:
            force: If True, force new download even if files exist

        Returns:
            Path to the downloaded and verified file

        Raises:
            DownloadError: If download fails after retry
            ChecksumError: If checksum verification fails
            ExtractionError: If archive verification fails
            ValueError: If archive format is not supported
        """
        try:
            # First verify we can handle this archive format
            # This prevents unnecessary downloads of unsupported formats
            archive_format = self._get_archive_format()

            # Download file if needed or if force=True
            archive_path = self._download_file(force=force)

            # Verify archive integrity with retry mechanism
            try:
                self._verify_archive(archive_path, archive_format)
            except ExtractionError:
                logger.error("Archive verification failed")
                # Remove potentially corrupted file
                archive_path.unlink()

                # Implement single retry unless force was specified
                # force=True typically indicates user expects fresh download
                if not force:
                    logger.info("Retrying download...")
                    archive_path = self._download_file(force=True)
                    self._verify_archive(archive_path, archive_format)

            return archive_path

        except Exception as e:
            logger.error(f"Error getting data: {str(e)}")
            raise

    def extract_data(self, force: bool = False) -> Path:
        """
        Extract the downloaded archive.

        Args:
            force: If True, force re-extraction even if files exist

        Returns:
            Path to the extracted data directory
        """
        logger.info(f"Extracting data with force={force}")
        archive_path = self.get_data(force=force)
        archive_format = self._get_archive_format()
        extract_to = self.data_cache / self.file_name.rsplit(".", 1)[0]

        if not force and extract_to.exists() and any(extract_to.iterdir()):
            logger.info(f"Using existing extracted data at {extract_to}")
            return extract_to

        try:
            # Clean up existing directory if it exists
            if extract_to.exists():
                self._clean_directory(extract_to)

            logger.info(f"Extracting {archive_path} to {extract_to}")
            self._extract_archive(archive_path, archive_format, extract_to)
            logger.info(f"Extraction completed successfully")
            return extract_to

        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            if extract_to.exists():
                # Clean up on failure
                self._clean_directory(extract_to)
            raise

    def _create_secure_directory(self, path: Path, mode: int = 0o750) -> None:
        """
        Create a directory with secure permissions.

        Mode 0o750 provides:
        - Owner: read/write/execute (7)
        - Group: read/execute (5)
        - Others: no permissions (0)
        """
        logger.debug(f"Creating directory {path} with mode {oct(mode)}")
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(mode)

    def _check_file_exists(self, file_path: Path) -> bool:
        """
        Check if a file exists and is not empty.
        Empty files could indicate interrupted downloads or extraction.
        """
        exists = file_path.exists() and file_path.stat().st_size > 0
        logger.debug(f"File {file_path} exists: {exists}")
        return exists

    def _get_archive_path(self) -> Path:
        """Get the full path for the archive file in cache."""
        return self.archive_cache / self.file_name

    def _get_archive_format(self) -> ArchiveFormat:
        """Determine the archive format from the file extension."""
        for format in ArchiveFormat:
            if self.file_name.endswith(format.value):
                return format
        raise ValueError(f"Unsupported archive format for file: {self.file_name}")

    def _calculate_md5(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of a file using streaming.

        Uses chunked reading to handle large files efficiently:
        - Prevents loading entire file into memory
        - Maintains consistent memory usage regardless of file size
        - Allows for progress monitoring if needed
        """
        logger.debug(f"Calculating MD5 for {file_path}")
        md5_hash = hashlib.md5()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(self.CHUNK_SIZE), b""):
                md5_hash.update(chunk)

        return md5_hash.hexdigest()

    def _verify_checksum(self, file_path: Path) -> bool:
        """Verify the MD5 checksum of downloaded file."""
        logger.info("Verifying MD5 checksum...")
        calculated_hash = self._calculate_md5(file_path)

        if calculated_hash != self.md5_checksum:
            logger.error(f"Checksum verification failed!")
            logger.error(f"Expected: {self.md5_checksum}")
            logger.error(f"Got: {calculated_hash}")
            raise ChecksumError(f"File checksum mismatch for {file_path}")

        logger.info("Checksum verification successful")
        return True

    def _download_file(self, force: bool = False) -> Path:
        """
        Download and verify file from Zenodo.

        The download process:
        1. Check if file exists and has valid checksum (unless force=True)
        2. Download to temporary file with progress bar
        3. Set secure permissions
        4. Verify checksum
        5. Move to final location

        Args:
            force: If True, force new download even if file exists

        Returns:
            Path to the downloaded file

        Raises:
            DownloadError: If download fails
            ChecksumError: If verification fails
        """
        archive_path = self._get_archive_path()

        # Only check existing file if not forcing re-download
        if not force and archive_path.exists():
            try:
                if self._verify_checksum(archive_path):
                    logger.info(f"Using existing verified file at {archive_path}")
                    return archive_path
            except ChecksumError:
                logger.warning("Existing file failed checksum verification")
                logger.info("Will download fresh copy")
                archive_path.unlink()

        logger.info(f"Downloading {self.file_name} from Zenodo...")
        try:
            # Start streaming download
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            # Use temporary file for atomic operation
            temp_path = archive_path.with_suffix(".tmp")

            with open(temp_path, "wb") as f:
                with tqdm(
                    total=total_size, unit="iB", unit_scale=True, desc="Downloading"
                ) as pbar:
                    for data in response.iter_content(self.CHUNK_SIZE):
                        size = f.write(data)
                        pbar.update(size)

            # Set secure permissions before moving to final location
            # Owner: rw, Group: r, Others: none
            temp_path.chmod(0o640)

            # Atomic move to final location
            if archive_path.exists():
                archive_path.unlink()  # Required for Windows
            temp_path.rename(archive_path)

            logger.info(f"Download completed. Verifying checksum...")
            self._verify_checksum(archive_path)
            return archive_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Download failed: {str(e)}")
            if archive_path.exists():
                archive_path.unlink()
            raise DownloadError(f"Failed to download {self.file_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during download: {str(e)}")
            if archive_path.exists():
                archive_path.unlink()
            raise

    def _clean_directory(self, path: Path):
        """
        Recursively remove a directory and all its contents.
        Handles Windows file locking and permission issues.
        """
        if not path.exists():
            return

        try:
            shutil.rmtree(path, ignore_errors=False)
        except Exception as e:
            logger.warning(f"Failed to remove directory {path}: {e}")
            # If rmtree fails, try manual removal
            try:
                for item in path.iterdir():
                    if item.is_file():
                        item.unlink(missing_ok=True)
                    elif item.is_dir():
                        self._clean_directory(item)
                path.rmdir()
            except Exception as e:
                logger.error(f"Failed to clean directory {path}: {e}")

    def _verify_archive(
        self, archive_path: Path, archive_format: ArchiveFormat
    ) -> bool:
        """
        Verify the integrity of the downloaded archive.

        This method performs format-specific integrity checks:
        - TAR: Streams through all members to verify structure (prefered format)
        - ZIP: Uses built-in testzip() to check CRC32 checksums
        - RAR: Uses rarfile's testrar() to verify integrity

        Memory-efficient approach:
        - Streams through archive contents instead of loading entirely
        - Maintains constant memory usage regardless of archive size
        - Prevents potential out-of-memory issues with large archives

        Args:
            archive_path: Path to the archive file
            archive_format: Format of the archive (TAR/ZIP/RAR)

        Returns:
            True if verification succeeds

        Raises:
            ExtractionError: If archive is corrupted or invalid
        """
        try:
            if archive_format == ArchiveFormat.TAR:
                with tarfile.open(archive_path, "r") as tar:
                    # Stream through members without extraction
                    # This catches structural corruption while being memory-efficient
                    for member in tar:
                        pass
            elif archive_format == ArchiveFormat.ZIP:
                with zipfile.ZipFile(archive_path, "r") as zip:
                    # testzip() returns None if all CRC32 checksums match
                    if zip.testzip() is not None:
                        raise ExtractionError("ZIP archive is corrupted")
            elif archive_format == ArchiveFormat.RAR:
                with rarfile.RarFile(archive_path, "r") as rar:
                    # testrar() verifies CRC32 checksums and archive structure
                    rar.testrar()
            return True
        except Exception as e:
            logger.error(f"Archive verification failed: {str(e)}")
            raise ExtractionError(f"Archive verification failed: {str(e)}")

    def _check_path_traversal(self, path: Union[str, Path]) -> bool:
        """Check if a path attempts directory traversal."""
        path_str = str(Path(path))
        normalized = os.path.normpath(path_str)

        # Check for absolute paths (both Unix and Windows)
        if os.path.isabs(path_str):
            return False

        return not (path_str != normalized or ".." in normalized.split(os.sep))

    def _set_secure_attributes(
        self,
        member: Union[tarfile.TarInfo, zipfile.ZipInfo],
    ) -> None:
        """
        Set secure attributes for archive members.

        Critical for security:
        - Prevents extracted files from running with elevated permissions
        - Ensures consistent ownership
        - Blocks potential privilege escalation attacks

        Cross-platform compatible between Windows and Unix systems.
        """
        if isinstance(member, tarfile.TarInfo):
            member.mode = 0o640  # rw-r-----
            # Use cross-platform approach for ownership
            if hasattr(os, "getuid"):  # Unix systems
                member.uid = os.getuid()
                member.gid = os.getgid()
            else:  # Windows systems
                member.uid = 0
                member.gid = 0

    def _extract_tar(self, archive_path: Path, extract_to: Path) -> None:
        """
        Extract a TAR archive securely with comprehensive safety checks.

        Security measures:
        1. Path traversal prevention
            - Blocks relative paths (../file.txt)
            - Blocks absolute paths (/etc/passwd)
            - Normalizes paths for consistent checking
        2. Permission hardening
            - Sets safe file permissions (0o640)
            - Enforces consistent ownership
            - Prevents setuid/setgid bits
        3. Pre-extraction validation
            - Checks all paths before any extraction
            - Fails early if any file is suspicious
            - Maintains atomic operation (all or nothing)

        Args:
            archive_path: Path to the TAR archive
            extract_to: Destination directory for extracted files

        Raises:
            SecurityError: If any security check fails
            ExtractionError: If extraction fails
        """
        with tarfile.open(archive_path, "r") as tar:
            # First pass: validate all paths before extracting anything
            # This ensures atomic operation - either all files are safe or none extract
            for member in tar.getmembers():
                if not self._check_path_traversal(member.name):
                    raise SecurityError(
                        f"Path traversal attempt detected: {member.name}"
                    )
                # Apply security hardening to all members
                self._set_secure_attributes(member)

            # Second pass: actual extraction
            # Only proceeds if all files passed security checks
            tar.extractall(path=extract_to)

    def _extract_zip(self, archive_path: Path, extract_to: Path):
        """
        Extract a ZIP archive securely with comprehensive safety checks.

        Key differences from TAR extraction:
        - Uses ZipInfo objects instead of TarInfo
        - Different path separator handling (/ vs os.sep)
        - No built-in permission attributes in ZIP format

        Security measures:
        1. Path validation
            - Blocks directory traversal attempts
            - Handles ZIP-specific path separators
            - Cross-platform path normalization
        2. Controlled extraction
            - Pre-validates all paths
            - Atomic operation (all or nothing)

        Note: ZIP format has limited permission/ownership support
        compared to TAR, so some security features are unavailable.

        Args:
            archive_path: Path to the ZIP archive
            extract_to: Destination directory

        Raises:
            SecurityError: On security check failures
            ExtractionError: On extraction failures
        """
        with zipfile.ZipFile(archive_path, "r") as zip:
            # Validate all paths before extraction begins
            for zip_info in zip.filelist:
                if not self._check_path_traversal(zip_info.filename):
                    raise SecurityError(
                        f"Path traversal attempt detected: {zip_info.filename}"
                    )

            # All paths validated, proceed with extraction
            zip.extractall(path=extract_to)

    def _extract_rar(self, archive_path: Path, extract_to: Path) -> None:
        """
        Extract a RAR archive securely with comprehensive safety checks.

        RAR-specific considerations:
        1. Format characteristics
            - Uses own compression algorithm
            - Limited metadata compared to TAR
            - No built-in permission handling
            - Cross-platform path encodings
        2. Dependencies
            - Requires external 'unrar' tool on system
            - May fail if unrar is not installed

        Security measures:
        1. Path validation
            - Prevents directory traversal
            - Handles RAR-specific path encodings
            - Blocks absolute paths
            - Cross-platform path normalization
        2. Extraction safety
            - Pre-validates all paths before extraction
            - Atomic operation (all or nothing)
            - Maintains secure permissions

        Args:
            archive_path: Path to the RAR archive
            extract_to: Destination directory for extracted files

        Raises:
            SecurityError:
            ExtractionError:
        """
        with rarfile.RarFile(archive_path, "r") as rar:
            # First pass: validate all paths before extraction
            # This ensures atomic operation - either all files are safe or none extract
            for member in rar.namelist():
                if not self._check_path_traversal(member):
                    raise SecurityError(f"Path traversal attempt detected: {member}")

            # All paths validated, proceed with extraction
            # Note: RAR doesn't support permission modifications like TAR
            rar.extractall(path=extract_to)

    def _extract_archive(
        self, archive_path: Path, archive_format: ArchiveFormat, extract_to: Path
    ) -> None:
        """
        Extract the archive based on its format.

        Raises:
            SecurityError: If path traversal attempt is detected
            ExtractionError: If extraction fails
        """
        try:
            if archive_format == ArchiveFormat.TAR:
                self._extract_tar(archive_path, extract_to)
            elif archive_format == ArchiveFormat.ZIP:
                self._extract_zip(archive_path, extract_to)
            elif archive_format == ArchiveFormat.RAR:
                self._extract_rar(archive_path, extract_to)
            else:
                raise ValueError(f"Unsupported archive format: {archive_format}")
        except (SecurityError, ExtractionError) as e:
            raise
        except Exception as e:
            raise ExtractionError(f"Failed to extract {archive_path}: {str(e)}")


def load_data():
    pass
