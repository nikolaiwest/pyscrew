[![PyPI version](https://badge.fury.io/py/pyscrew.svg)](https://badge.fury.io/py/pyscrew)
[![Python](https://img.shields.io/pypi/pyversions/pyscrew.svg)](https://pypi.org/project/pyscrew/)
[![License](https://img.shields.io/github/license/nikolaiwest/pyscrew.svg)](https://github.com/nikolaiwest/pyscrew/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/pyscrew)](https://pepy.tech/project/pyscrew)

# PyScrew

PyScrew is a Python package designed to simplify access to industrial research data from screw driving experiments. It provides a streamlined interface for downloading, validating, and preparing experimental datasets hosted on Zenodo.

More information on the data is available here: https://zenodo.org/records/14769379

## Features

- Data loading from various scenarios
- Handling duplicates and missing values
- Length normalization through padding and truncation
- Configurable data processing pipeline
- Comprehensive data validation and integrity checks
- Detailed logging and statistics tracking
- Support for multiple measurement types (torque, angle, time, gradient, step)

## Installation

To install PyScrew, use pip:

```bash
pip install pyscrew
```

## Usage

### Basic Usage
You can load data from a specific scenario using the `get_data` function with default settings:

```python 
import pyscrew

# Load data from the thread degradation scenario (s01)
data = pyscrew.get_data(scenario="s01")

# Access the measurements and labels
x_values = data["torque values"]
y_values = data["class values"]
```

### Advanced Usage
<details>
<summary>Click to expand for detailed configuration options</summary>

```python 
import pyscrew

# Load and process data with custom settings
data = pyscrew.get_data(
    scenario="assembly-conditions-2",  # or "s04" or "s04_assembly-conditions-2"
    cache_dir="~/.cache/pyscrew", # Specify custom directory (default: src/pyscrew/downloads)
    force_download=True,  # Force re-download even if cached
    handle_duplicates="first",  # How to handle duplicate time points
    handle_missings="mean",  # How to handle missing values
    target_length=1000,  # Target length for normalization
)

# Describe the data
print("Available measurements:", data.keys())
print("Number of torque measurements:", len(data["torque values"]))

# Access the data
x_values = data["torque values"]
y_values = data["class values"]

```
### Scenario Specification
The scenario parameter can be specified in three different ways:

1. **Short ID**: Use the scenario identifier (e.g., `"s01"`, `"s02"`, etc.)
2. **Full Name**: Use the descriptive name (e.g., `"thread-degradation"`, `"surface-friction"`)
3. **Full ID**: Use the complete identifier (e.g., `"s01_thread-degradation"`, `"s02_surface-friction"`)

All three formats are equivalent and will load the same dataset. For example, these all refer to the same scenario:
```python
data = pyscrew.get_data(scenario="s02")  # Short ID
data = pyscrew.get_data(scenario="surface-friction")  # Full name
data = pyscrew.get_data(scenario="s02_surface-friction")  # Full ID
```
</details>

--- 

You can find more info regarding the scenarios on [github](https://github.com/nikolaiwest/pyscrew/tree/main/docs/scenarios) and on [zenodo](https://doi.org/10.5281/zenodo.14729547), or you can simply list available scenarios with their descriptions like this: 

```python
scenarios = pyscrew.list_scenarios()
print("Available scenarios:", scenarios)
```

## Available Scenarios

Our datasets examine various aspects of screw driving operations in industrial settings. Each scenario focuses on specific experimental conditions and research questions:

| ID | Name | Description | Samples | Classes | Documentation |
|----|------|-------------|---------|---------|---------------|
| s01 | Thread Degradation | Examines thread degradation in plastic materials through repeated fastening operations | 5,000 | 1 | [Details](docs/scenarios/s01_thread-degradation.md) |
| s02 | Surface Friction | Investigates the impact of different surface conditions (water, lubricant, adhesive, etc.) on screw driving operations | 12,500 | 8 | [Details](docs/scenarios/s02_surface-friction.md) |
| s03 | Assembly Conditions 1 | Examines various screw and component faults including washer modifications, thread deformations, and alignment issues | 1,800 | 27 | [Details](docs/scenarios/s03_assembly-conditions-1.md) |
| s04 | Assembly Conditions 2 | Investigates thread modifications, surface conditions, component modifications, and process parameter changes | 5,000 | 25 | [Details](docs/scenarios/s04_assembly-conditions-2.md) |
| s05 | Upper Workpiece Fabrication | Analyzes variations in injection molding parameters for upper workpieces | 2,400 | 42 | [Details](docs/scenarios/s05_upper-workpiece.md) |
| s06 | Lower Workpiece Fabrication | Studies variations in injection molding parameters for lower workpieces | 7,482 | 44 | [Details](docs/scenarios/s06_lower-workpiece.md) |

## Package Structure

```bash
PyScrew/
├── docs/
│   └── scenarios/          
│       ├── s01_thread-degradation.md
│       ├── s02_surface-friction.md
│       ├── s03_assembly-conditions-1.md
│       ├── s04_assembly-conditions-2.md
│       ├── s05_upper-workpiece.md
│       └── s06_lower-workpiece.md
├── src/
│   └── pyscrew/
│       ├── __init__.py       # Package initialization and version
│       ├── main.py           # Main interface and high-level functions
│       ├── core/             # Core data model and structures
│       │   ├── __init__.py
│       │   ├── dataset.py    # ScrewDataset class
│       │   ├── run.py        # ScrewRun class
│       │   ├── step.py       # ScrewStep class
│       │   └── fields.py     # Field definitions
│       ├── config/           # Configuration management
│       │   ├── __init__.py
│       │   ├── pipeline.py   # Pipeline configuration
│       │   └── scenarios.py  # Scenario configuration
│       ├── pipeline/         # Data processing pipeline components
│       │   ├── __init__.py
│       │   ├── loading.py    # Data loading from Zenodo
│       │   ├── processing.py # Data processing functionality
│       │   ├── validating.py # Data validation after loading
│       │   └── transformers/ # Data transformation modules
│       ├── scenarios/        # Scenario-specific configurations
│       │   ├── __init__.py
│       │   ├── s01.yml      # Thread degradation scenario
│       │   ├── s02.yml      # Surface friction scenario
│       │   ├── s03.yml      # Assembly conditions 1
│       │   ├── s04.yml      # Assembly conditions 2
│       │   ├── s05.yml      # Upper workpiece
│       │   └── s06.yml      # Lower workpiece
│       ├── downloads/        # Default location for downloaded data
│       │   ├── archives/    # Compressed dataset archives
│       │   └── extracted/   # Extracted dataset files  
│       ├── tools/                      # Utility scripts and tools
│       │   ├── create_label_csv.py     # Label file generation
│       │   └── get_dataset_metrics.py  # Documentation metrics calculation
│       └── utils/                      # Utility functions and helpers
│           ├── data_model.py
│           └── logger.py
└── tests/                   # Test suite
```

## API Reference

### Main Functions

`get_data(scenario_name: str, cache_dir: Optional[Path] = None, force: bool = False) -> Path`

Downloads and extracts a specific dataset.

* `scenario_name`: Name of the dataset to download
* `cache_dir`: Optional custom cache directory (default: ~/.cache/pyscrew)
* `force`: Force re-download even if cached
* **Returns:** Path to extracted dataset

`list_scenarios() -> Dict[str, str]`

Lists all available datasets and their descriptions.

* Returns: Dictionary mapping scenario names to descriptions

## Cache Structure

Downloaded data is stored in:

```bash 
~/.cache/pyscrew/
├── archives/     # Compressed dataset archives
└── extracted/    # Extracted dataset files
    ├── s01_thread-degradation/
    ├── s02_surface-friction/
    ├── s03_assembly-conditions-1/
    ├── s04_assembly-conditions-2/
    ├── s05_upper-workpiece/
    ├── s06_lower-workpiece/
    └── ...
```

## Code Style

This project uses:
- [Black](https://black.readthedocs.io/en/stable/) for code formatting
- [Ruff](https://docs.astral.sh/ruff/) for fast linting and import sorting
- [MyPy](https://mypy.readthedocs.io/en/stable/) for static type checking
- [Pytest](https://docs.pytest.org/en/stable/) for testing

Configuration for these tools can be found in `pyproject.toml`.

## Development
The package is under active development. Further implementation will add data processing utilities and data validation tools. 

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Citation
If you use this package in your research, please cite either one of the following publications:
* West, N., & Deuse, J. (2024). A Comparative Study of Machine Learning Approaches for Anomaly Detection in Industrial Screw Driving Data. Proceedings of the 57th Hawaii International Conference on System Sciences (HICSS), 1050-1059. https://hdl.handle.net/10125/106504
* West, N., Trianni, A. & Deuse, J. (2024). Data-driven analysis of bolted joints in plastic housings with surface-based anomalies using supervised and unsupervised machine learning. CIE51 Proceedings. _(DOI will follow after publication of the proceedings)_

*A dedicated paper for this library is currently in progress.*