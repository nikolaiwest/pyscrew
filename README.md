# PyScrew

PyScrew is a Python package designed to simplify access to industrial research data from screw driving experiments. It provides a streamlined interface for downloading, validating, and preparing experimental datasets hosted on Zenodo.

More information on the data is available here: https://zenodo.org/records/14769379

## Features

- Data loading from various scenarios
- Handling duplicates and missing values
- Length normalization through padding and truncation
- Configurable data processing pipeline

## Installation

To install PyScrew, use pip:

```bash
pip install pyscrew
```

## Quck start

```python 
import pyscrew

# List available scenarios with their descriptions
scenarios = pyscrew.list_scenarios()
print("Available scenarios:", scenarios)

# Load and process data from a specific scenario
data = pyscrew.get_data(
    "surface-friction", # or "thread-degradation"
    handle_duplicates="first",
    handle_missings="mean",
    target_length=800,
) 

# Describe the data
print("Available measurements:", data.keys())
print("Number of torque measurements:", len(data["torque values"]))

# Access the data 
x_values = data["torque values"]
y_values = data["class values"]
```

## Available Scenarios

Our datasets examine various aspects of screw driving operations in industrial settings. Each scenario focuses on specific experimental conditions and research questions:

| ID | Name | Description | Samples | Classes | Documentation |
|----|------|-------------|---------|---------|---------------|
| s01 | Thread Degradation | Examines thread degradation in plastic materials through repeated fastening operations | 5,000 | 1 | [Details](docs/scenarios/s01_thread-degradation.md) |
| s02 | Surface Friction | Investigates the impact of different surface conditions (water, lubricant, adhesive, etc.) on screw driving operations | 12,500 | 8 | [Details](docs/scenarios/s02_surface-friction.md) |
| s03 | Error Collection 1 | Current place holder doc for the upcoming scenario 3 with multiple error classes | TBD | TBD | [Details](docs/scenarios/s03_error-collection-1.md) |

## Package structure

```bash
PyScrew/
├── docs/
│   └── scenarios/           # Detailed scenario documentation
│       ├── s01_thread-degradation.md
│       ├── s02_surface-friction.md
│       └── s03_error-collection-1.md
├── src/
│   └── pyscrew/
│       ├── __init__.py      # Package initialization and version
│       ├── main.py          # Main interface and high-level functions
│       ├── loading.py       # Data loading from Zenodo
│       ├── processing.py    # Data processing functionality
│       ├── tools/           # Utility scripts and tools
│       │   ├── create_label_csv.py    # Label file generation
│       │   └── get_dataset_metrics.py  # Documentation metrics calculation
│       └── utils/           # Utility functions and helpers
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
    ├── s03_error-collection-1/
    └── ...
```

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