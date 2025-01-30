# PyScrew

PyScrew is a Python package designed to simplify access to industrial research data from screw driving experiments. It provides a streamlined interface for downloading, validating, and preparing experimental datasets hosted on Zenodo.

More information on the data is available here: https://zenodo.org/records/14769379

## Features

- **Easy Data Access**: Simple interface to download and extract screw driving datasets
- **Data Integrity**: Automatic checksum verification and secure extraction
- **Caching System**: Smart caching to prevent redundant downloads
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Memory Efficient**: Handles large datasets through streaming operations
- **Secure**: Implements protection against common security vulnerabilities

## Installation

Install PyScrew directly from PyPI:

```bash
pip install pyscrew
```

## Quck start

```python 
import pyscrew

# List available datasets
scenarios = pyscrew.list_scenarios()
print("Available datasets:", scenarios)

# Download and extract a specific dataset
data_path = pyscrew.get_data("thread-degradation")
print(f"Data extracted to: {data_path}")
```

## Package structure

```bash
PyScrew/
├── src/
│   └── pyscrew/
│       ├── __init__.py      # Package initialization and version
│       ├── main.py          # Main interface and high-level functions
│       ├── loading.py       # Data loading from Zenodo
│       ├── processing.py    # Data processing functionality (planned)
│       └── validation.py    # Data validation checks (planned)
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

**A dedicated paper for this library is currently in progress.**