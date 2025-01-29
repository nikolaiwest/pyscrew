"""
Centralized logging configuration for PyScrew.

This module provides consistent logging across the PyScrew library with:
    - Configurable log levels
    - Formatted output for both file and console
    - Context-aware logger names
    - Default log file location in utils/logs directory
    
Usage:
    from pyscrew.utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Starting process...")
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union

# Default format includes timestamp, level, module, and message
DEFAULT_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Environment variable to control log level and file
LOG_LEVEL_ENV = 'PYSCREW_LOG_LEVEL'
LOG_FILE_ENV = 'PYSCREW_LOG_FILE'

# Default log directory in utils/logs
DEFAULT_LOG_DIR = Path(__file__).parent / 'logs'
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / 'pyscrew.log'

# Mapping of string log levels to logging constants
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def get_log_level() -> int:
    """Get log level from environment or default to INFO."""
    level_name = os.environ.get(LOG_LEVEL_ENV, 'INFO').upper()
    return LOG_LEVELS.get(level_name, logging.INFO)

def get_log_file() -> Path:
    """
    Get the log file path from environment or use default.
    
    If PYSCREW_LOG_FILE is set in environment, uses that path.
    Otherwise uses DEFAULT_LOG_FILE in utils/logs directory.
    """
    env_log_file = os.environ.get(LOG_FILE_ENV)
    if env_log_file:
        return Path(env_log_file)
    return DEFAULT_LOG_FILE

def setup_file_handler(log_file: Optional[Union[str, Path]] = None) -> logging.FileHandler:
    """
    Create and configure a file handler for logging.
    
    Args:
        log_file: Optional path to log file, defaults to utils/logs/pyscrew.log
        
    Returns:
        Configured FileHandler instance
    """
    log_path = Path(log_file) if log_file else get_log_file()
    
    # Create logs directory if it doesn't exist
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT))
    
    return file_handler

def setup_console_handler() -> logging.StreamHandler:
    """
    Create and configure a console handler for logging.
    
    Returns:
        Configured StreamHandler instance
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT))
    
    return console_handler

def get_logger(
    name: str,
    level: Optional[Union[str, int]] = None,
    log_file: Optional[Union[str, Path]] = None,
    console: bool = True
) -> logging.Logger:
    """
    Get a logger configured for use in PyScrew.
    
    This function provides a consistent logging interface across the library:
    - Creates a logger with the specified name
    - Sets appropriate log level from arguments or environment
    - Configures console output by default
    - Sets up file logging in utils/logs by default
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        level: Optional log level (default: from environment or INFO)
        log_file: Optional custom path to log file
        console: Whether to enable console output (default: True)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process...")
        2024-01-29 10:30:45 - INFO - my_module - Starting process...
    """
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Only configure if the logger hasn't been set up
    if not logger.handlers:
        # Determine log level
        if level is None:
            level = get_log_level()
        elif isinstance(level, str):
            level = LOG_LEVELS.get(level.upper(), logging.INFO)
            
        logger.setLevel(level)
        
        # Add console handler if enabled
        if console:
            logger.addHandler(setup_console_handler())
        
        # Add file handler
        logger.addHandler(setup_file_handler(log_file))
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger