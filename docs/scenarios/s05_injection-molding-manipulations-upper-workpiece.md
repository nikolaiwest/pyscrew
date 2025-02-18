# Screw Driving Dataset - s05_injection-modling-manipulations-upper-workpiece

<!-- Dataset Information -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dataset Size](https://img.shields.io/badge/Dataset_Size-2400_samples-blue)](https://github.com/nikolaiwest/pyscrew)

<!-- Version Information -->
[![Version](https://img.shields.io/badge/Version-v1.1.5-blue)](https://github.com/nikolaiwest/pyscrew)
[![Updated](https://img.shields.io/badge/Updated-2025/02/18-blue)](https://github.com/nikolaiwest/pyscrew)

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
This dataset examines the impact of injection molding process parameters on screw driving performance in plastic components. It systematically investigates five key process parameters: mold temperature, glass fiber content, recyclate content, switching point, and injection velocity.

The dataset was generated using a controlled experimental setup that systematically varied these parameters to understand their influence on screw connection quality.

This research is crucial for understanding how manufacturing process parameters affect assembly quality, enabling more robust process control and quality assurance in plastic component assembly.

Collection Date: December 2024

## Quick Start

```python
from pyscrew import get_data

# Load and prepare the data (returns a dictionary)
data = get_data(scenario_name="s05_injection-molding-manipulations-upper-workpiece")

# Access measurements and labels
x_values = data["torque values"] # Available: torque, angle, time, gradient, step, class
y_values = data["class values"]
```

## Dataset Structure

The dataset consists of three primary components:

1. `/json` directory: Contains 2,400 individual JSON files of unprocessed screw driving operations
2. `labels.csv`: A metadata file containing key information for each operation
3. `README.md`: This documentation file

### Labels File Structure

The `labels.csv` contains seven columns:

| Column             | Type    | Description                                                      |
|--------------------|---------|------------------------------------------------------------------|
| run_id             | int     | Unique cycle number as recorded by the screw station             |
| file_name          | string  | Name of corresponding JSON file with the measurements            |
| class_value        | integer | Specifies the respective class (0-43)                            |
| result_value       | string  | Operation outcome (OK/NOK) as determined by the station          |
| workpiece_id       | string  | Unique workpiece identifier (14-digit) as data matrix code       |
| workpiece_usage    | integer | Previous operations count                                         |
| workpiece_location | integer | Screw position (0: left, 1: right)                               |

### Classification Labels (Classes)

The dataset includes 44 distinct classes across 5 main parameter groups:

1. Mold Temperature (Classes 0-5):
   - Temperature range: 30°C - 55°C
   - Simulates cooling circuit fluctuations

2. Glass Fiber Content (Classes 6-12):
   - Content range: 18% - 30%
   - Simulates material batch variations

3. Recyclate Content (Classes 13-23):
   - Content range: 0% - 100%
   - Simulates recycled material impact

4. Switching Point (Classes 24-33):
   - Range: 11cm³ - 19cm³
   - Simulates non-return valve behavior

5. Injection Velocity (Classes 34-43):
   - Range: 20cm³/s - 100cm³/s
   - Simulates screw movement control

### JSON File Structure
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

### Test Protocol
- Each workpiece uniquely identified via DMC
- Two test locations per workpiece (left/right)
- Parameter variations according to defined class specifications

## Dataset Statistics

### Sample Distribution
- Sample Metrics:
  - Total operations: 2,400
  - Unique workpieces: 1,200
  - Operations per workpiece: 2
- Quality Distribution:
  - Normal (OK): 2,397 (99.88%)
  - Anomalous (NOK): 3 (0.12%)

### Distribution by Class

| Value  | Name      | Samples | #OK  | #NOK | %OK   | %NOK  |
|--------|-----------|---------|------|------|-------|-------|
| 0      | Baseline  | 5000    | 4089 |  911 | 81.78 | 18.22 |


### Collection Timeline
Data collection occurred in December 2024:
- Dec 5: Glass fiber content variations
- Dec 6: Recyclate content variations
- Dec 9: Mixed parameter studies
- Dec 11: Temperature and velocity studies

### Data Quality
- Sampling frequency: 833.33 Hz
- Missing values: 2.58%
- Data completeness: 97.42%

### Key Characteristics
- Comprehensive parameter study
- Very low anomaly rate (0.12%)
- High data completeness (97.42%)
- Systematic parameter variations
- Dual test locations per workpiece

## Usage Guidelines

### Data Access
Recommended approaches:
- Either via JSON library for operation data and Pandas/CSV readers for labels file
- Or via our custom `PyScrew` Python package (available in [this repository](https://github.com/nikolaiwest/pyscrew))

### Analysis Suggestions
- Parameter influence analysis
- Cross-parameter interaction studies
- Quality prediction modeling
- Process window optimization

## Citations
A publication for this dataset is currently in process. This information will be updated once a DOI is available. 

## Repository
Issues and questions: https://github.com/nikolaiwest/pyscrew

## Acknowledgments

These datasets were collected and prepared by:
- [RIF Institute for Research and Transfer e.V.](https://www.rif-ev.de/)
- [University of Kassel](https://www.uni-kassel.de/maschinenbau/en/), [Institute of Materials Engineering (IfW)](https://www.uni-kassel.de/maschinenbau/en/institute/institute-of-materials-engineering/departments/plastics-engineering)
- [Technical University Dortmund](https://www.tu-dortmund.de/), [Institute for Production Systems(IPS)](https://ips.mb.tu-dortmund.de/)
- Feel free to contact us directly for further questions: [Nikolai West (nikolai.west@tu-dortmund.de)](nikolai.west@tu-dortmund.de)

The preparation and provision of the research was supported by:

| Organization | Role | Logo |
|-------------|------|------|
| German Ministry of Education and Research (BMBF) | Funding | <img src="https://vdivde-it.de/system/files/styles/vdivde_logo_vdivde_desktop_1_5x/private/image/BMBF_englisch.jpg?itok=6FdVWG45" alt="BMBF logo" height="150"> |
| European Union's "NextGenerationEU" | Funding | <img src="https://www.bundesfinanzministerium.de/Content/DE/Bilder/Logos/nextgenerationeu.jpg?__blob=square&v=1" alt="NextGenerationEU logo" height="150"> |
| VDIVDE | Program Support | <img src="https://vdivde-it.de/themes/custom/vdivde/images/vdi-vde-it_og-image.png" alt="Projekttraeger VDIVDE logo" height="150"> |

This research is part of the funding program ["Data competencies for early career researchers"](https://www.bmbf.de/DE/Forschung/Wissenschaftssystem/Forschungsdaten/DatenkompetenzenInDerWissenschaft/datenkompetenzeninderwissenschaft_node.html). 

More information regarding the research project is available our [project homepage](https://prodata-projekt.de/).


## License

**MIT License**

Permission is hereby granted, free of charge, to any person obtaining a copy of this dataset and associated documentation files, to deal in the dataset without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the dataset, and to permit persons to whom the dataset is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the dataset.

THE DATASET IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE DATASET OR THE USE OR OTHER DEALINGS IN THE DATASET.

*Copyright (c) 2025 Nikolai West @ RIF/IfW/IPS*