# Screw Driving Dataset - [SCENARIO_NAME]

<!-- Dataset Information -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14769379.svg)](https://zenodo.org/uploads/14769379)
[![Dataset Size](https://img.shields.io/badge/Dataset_Size-[NUMBER_OF_SAMPLES]_samples-blue)](https://github.com/nikolaiwest/pyscrew)

<!-- Version Information -->
[![Version](https://img.shields.io/badge/Version-[VERSION]-blue)](https://github.com/nikolaiwest/pyscrew)
[![Updated](https://img.shields.io/badge/Updated-[UPDATE_DATE]-blue)](https://github.com/nikolaiwest/pyscrew)

<!-- Publication Information -->
[![Paper](https://img.shields.io/badge/DOI-10.24251%2FHICSS.2024.126-green)](https://hdl.handle.net/10125/106504)
[![ResearchGate](https://img.shields.io/badge/ResearchGate-00CCBB?logo=ResearchGate&logoColor=white)]([RESEARCHGATE_LINK])

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Dataset Structure](#dataset-structure)
- [Experimental Setup](#experimental-setup)
- [Dataset Statistics](#dataset-statistics)
- [Usage Guidelines](#usage-guidelines)
- [Citations](#citations)
- [Repository](#repository)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview
<!-- Provide clear statements for:
   1. What: The specific problem/phenomenon being studied
   2. How: The method of data generation
   3. Why: The relevance/importance of this scenario -->
[WHAT_STUDIED]
[HOW_GENERATED]
[WHY_RELEVANT]

Collection Date: [MONTH_YEAR] - [MONTH_YEAR]

## Quick Start

```python
from pyscrew import get_data

# Load and prepare the data (returns a dictionary)
data = get_data(scenario_name=[SCENARIO_NAME])

# Access measurements and labels
x_values = data["torque values"] # Available: torque, angle, time, gradient, step, class
y_values = data["class values"]
```

## Dataset Structure

The dataset consists of three primary components:

1. `/json` directory: Contains [NUMBER_OF_SAMPLES] individual JSON files of unprocessed screw driving operations, each recording the complete measurement data of a single screwing process.
2. `labels.csv`: A metadata file that collects key information from each operation (e.g. for classification). More Details are displayed in the table below.
3. `README.md`: This readme-file providing stand-alone context for the dataset.

### Labels File Structure

The `labels.csv` contains seven columns:

| Column             | Type    | Description                                                      |
|--------------------|---------|------------------------------------------------------------------|
| run_id             | int     | Unique cycle number as recorded by the screw station             |
| file_name          | string  | Name of corresponding JSON file with the measurements            |
| class_value        | integer | Specifies the [respective class](#classification-labels-classes) |
| result_value       | string  | Operation outcome (OK/NOK) as determined by the station          |
| workpiece_id       | string  | Unique workpiece identifier (14-digit) as data matrix code       |
| workpiece_usage    | integer | Previous operations count (0-24): number of screw runs           |
| workpiece_location | integer | Screw position (0: left, 1: right)                               |

### Classification Labels (Classes)

<!-- List all classes with descriptions. Example formatas table :
| Value  | Name      | Amount | Description                               |
|--------|-----------|--------|-------------------------------------------|
| 0      | Baseline  | 5000   | No additional manipulations, only wear down from repeated use |
-->
[LIST_OF_CLASSES]

### JSON File Structure
<!--Same for all datasets, but required for stand-alone usage -->
Each JSON file represents a complete screw driving operation with the following structure:

#### System Configuration
- `format`: Data format specification
- `node id`: System identifier
- `hardware`: Hardware model (e.g., "CS351")
- `sw version`: Software version
- `MCE factor`: Measurement calibration factor
- `max. speed`: Maximum speed capability
- `nominal torque`: System's nominal torque setting

#### Operation Parameters
- `prg name`: Program name used for the operation
- `prg date`: Program creation/modification date
- `cycle`: Operation cycle number
- `date`: Timestamp of the operation
- `id code`: Work piece identifier (14-digit DMC)
- `torque unit`: Unit of measurement for torque (Nm)
- `total time`: Total operation duration (seconds)
- `tool serial`: Tool identifier

#### Tightening Steps
Each operation consists of four tightening steps:
1. Finding
2. Thread forming
3. Pre-tightening
4. Final tightening (1.4 Nm)

Each step contains:
- `step type`: Type of tightening step
- `name`: Step identifier
- `speed`: Angular velocity (degrees/minute)
- `result`: Step outcome (OK/NOK)
- `tightening functions`: Array of control parameters including:
  - Target values (`nom`)
  - Actual values (`act`)
  - Thresholds and limits

#### Time Series Data
Each step includes detailed measurement graphs containing:
- `angle values`: Rotation angle in degrees
- `torque values`: Applied torque in Nm
- `gradient values`: Rate of change
- `time values`: Timestamp for each measurement (seconds)
- Additional monitoring values (`torqueRed`, `angleRed`)

## Data Processing

The dataset is provided raw and underwent no additional preprocessing steps.

## Experimental Setup

### Equipment
- Automatic screwing station (EV motor control unit assembly)
- Delta PT 40x12 screws (thermoplastic-optimized)
- Target torque: 1.4 Nm (range: 1.2-1.6 Nm)
- Thermoplastic housing components
<!-- Add any scenario-specific equipment -->
[ADDITIONAL_EQUIPMENT]

### Test Protocol
- Each workpiece uniquely identified via DMC
- Two test locations per workpiece (left/right)
<!-- Essential information for all scenarios -->
- Base Protocol:
  - Workpiece identification: DMC
  - Test locations: [LOCATION_COUNT]
  - Cycles per location: [CYCLES_PER_LOCATION]
<!-- Scenario-specific details -->
- Specific Conditions:
  [SPECIFIC_CONDITIONS]

## Dataset Statistics

### Sample Distribution
<!-- Use consistent metrics across all scenarios -->
- Sample Metrics:
  - Total operations: [TOTAL_OPERATIONS]
  - Unique workpieces: [WORKPIECE_COUNT]
  - Operations per workpiece: [OPERATIONS_PER_PIECE]
- Quality Distribution:
  - Normal (OK): [OK_COUNT] ([OK_PERCENTAGE]%)
  - Anomalous (NOK): [NOK_COUNT] ([NOK_PERCENTAGE]%)

<!-- If applicable, add class-specific distribution -->
### Distribution by Class
<!-- Example format:
| Value  | Name      | Samples | #OK  | #NOK | %OK   | %NOK  |
|--------|-----------|---------|------|------|-------|-------|
| 0      | Baseline  | 5000    | 4089 |  911 | 81.78 | 18.22 |
[CLASS_DISTRIBUTION]

### Collection Timeline
<!-- List significant collection periods and what was collected -->
[COLLECTION_TIMELINE]

### Data Quality
- Sampling frequency: [SAMPLING_FREQUENCY] Hz
- Missing values: [MISSING_VALUE_PERCENTAGE]%
- Data completeness: [COMPLETENESS_PERCENTAGE]%

### Key Characteristics
<!-- List 4-6 key characteristics specific to this scenario. Example:
- Natural degradation progression
- Balanced workpiece location distribution
- Complete lifecycle coverage -->
[KEY_CHARACTERISTICS]

## Usage Guidelines

### Data Access
Recommended approaches:
- Either via JSON library for operation data and Pandas/CSV readers for labels file
- Or via our custom `PyScrew` Python package (available in [this repository](https://github.com/nikolaiwest/pyscrew))

### Analysis Suggestions
<!-- List 4-6 scenario-specific suggestions. Include:
   1. Time-series analysis approaches
   2. Statistical investigations
   3. Comparative studies
   4. Specific phenomena to examine -->
- [SUGGESTION_1]
- [SUGGESTION_2]
...
## Citations
If using this dataset, please cite:
[CITATION_INFO]

## Repository
Issues and questions: https://github.com/nikolaiwest/pyscrew

## Acknowledgments

These datasets were collected and prepared by:
- [RIF Institute for Research and Transfer e.V.](https://www.rif-ev.de/)
- [Technical University Dortmund](https://www.tu-dortmund.de/), [Institute for Production Systems](https://ips.mb.tu-dortmund.de/)
- Feel free to contact us directly for further questions: [Nikolai West (nikolai.west@tu-dortmund.de)](nikolai.west@tu-dortmund.de)

The preparation and provision of the research was supported by:

| Organization | Role | Logo |
|-------------|------|------|
| German Ministry of Education and Research (BMBF) | Funding | <img src="https://vdivde-it.de/system/files/styles/vdivde_logo_vdivde_desktop_1_5x/private/image/BMBF_englisch.jpg?itok=6FdVWG45" alt="BMBF logo" height="150"> |
| European Union's "NextGenerationEU" | Funding | <img src="https://www.bundesfinanzministerium.de/Content/DE/Bilder/Logos/nextgenerationeu.jpg?__blob=square&v=1" alt="NextGenerationEU logo" height="150"> |
| VDIVDE | Program Support | <img src="https://vdivde-it.de/themes/custom/vdivde/images/vdi-vde-it_og-image.png" alt="Projekttraeger VDIVDE logo" height="150"> |

This research is part of the funding program ["Data competencies for early career researchers"](https://www.bmbf.de/DE/Forschung/Wissenschaftssystem/Forschungsdaten/DatenkompetenzenInDerWissenschaft/datenkompetenzeninderwissenschaft_node.html). 

More information regarding the research project is available at [prodata-projekt.de](https://prodata-projekt.de/).

## License

**MIT License**


Permission is hereby granted, free of charge, to any person obtaining a copy of this dataset and associated documentation files, to deal in the dataset without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the dataset, and to permit persons to whom the dataset is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the dataset.

THE DATASET IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE DATASET OR THE USE OR OTHER DEALINGS IN THE DATASET.

*Copyright (c) 2025 Nikolai West @ RIF/IPS*