"""
Core data model for screw operation analysis.

This module implements a hierarchical data structure for analyzing screw operations:

ScrewDataset
    └── ScrewRun (multiple)
        └── ScrewStep (multiple)
            └── Measurements (time, torque, angle, gradient) + "step" to track measurement origin

The data comes from two sources:
1. JSON files: Contain measurement data and step information
2. CSV file: Contains metadata and classification information
"""

from .dataset import ScrewDataset
from .run import ScrewRun
from .step import ScrewStep
from .fields import JsonFields, CsvFields

__all__ = [
    "ScrewDataset",
    "ScrewRun",
    "ScrewStep",
    "JsonFields",
    "CsvFields",
]
