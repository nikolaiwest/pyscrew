# pyscrew
Loads and prepares screw driving data from various experiments. Currently, work in progress.

PyScrew/
├── LICENSE
├── README.md
├── pyproject.toml
├── src/
│   └── pyscrew/
│       ├── __init__.py      # Package initialization and version
│       ├── main.py          # Main interface and high-level functions
│       ├── loading.py       # Data loading from Zenodo
│       ├── processing.py    # Data processing functionality
│       └── validation.py    # Data validation and integrity checks
└── tests/                   # Corresponding test files
    ├── __init__.py
    ├── test_main.py
    ├── test_loading.py
    ├── test_processing.py
    └── test_validation.py