# Screw Driving Dataset - S02_surface-friction

<!-- Dataset Information -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14769379.svg)](https://zenodo.org/uploads/14769379)
[![Dataset Size](https://img.shields.io/badge/Dataset_Size-12500_samples-blue)](https://github.com/nikolaiwest/pyscrew)

<!-- Version Information -->
[![Version](https://img.shields.io/badge/Version-v1.2.0-blue)](https://github.com/nikolaiwest/pyscrew)
[![Updated](https://img.shields.io/badge/Updated-2025/02/12-blue)](https://github.com/nikolaiwest/pyscrew)

<!-- Publication Information -->
[![Paper](https://img.shields.io/badge/DOI-10.24251%2FHICSS.2024.126-green)](https://hdl.handle.net/10125/106504)
[![ResearchGate](https://img.shields.io/badge/ResearchGate-00CCBB?logo=ResearchGate&logoColor=white)](https://www.researchgate.net/publication/388917487_Detection_of_surface-based_anomalies_for_self-tapping_screws_in_plastic_housings_using_supervised_machine_learning)

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
This dataset examines the impact of different surface conditions on screw driving operations in plastic material. It was generated using an automatic screwing station from EV motor control unit assembly.It captures the effects of various surface treatments and conditions on the fastening process. 
A total of seven different errors were recorded. The main focus of the experiment was seeing the effect that repeated screwing has on the upper work piece. Using an upper workpiece multiple times leaves residue in the contact area of the screw head and the upper workpiece, visually altering the surface structure. The goal was to deterime whether these effects alter the screwing behaviour. 

Collection Date: Jul. 2023 - Apr. 2024 *(some errors were recorded later to inspect more friction variations)*

## Quick Start

```python
from pyscrew import get_data

# Load and prepare the data (returns a dictionary)
data = get_data(scenario_name="s02_surface-friction")

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

| Value  | Name           | Amount | Description                                                             |
|--------|----------------|--------|-------------------------------------------------------------------------|
| 0      | Baseline       | 2500   | No additional manipulations, baseline data for reference                |
| 1      | Up to 50       | 2500   | Upper workpiece was used 25 times, showing surface weardown             |
| 2      | With water     | 1250   | Decreased friction due to water-contaminated workpiece surface          |
| 3      | With lubricant | 1250   | Decreased friction due to lubricant-contaminated workpiece surface      |
| 4      | Sanded 40      | 1250   | Increased friction due to coarse surface treatment by sanding (40 grit) |
| 5      | Sanded 400     | 1250   | Increased friction due to fine surface treatment by sanding (400 grit)  |
| 6      | With adhesive  | 1250   | Alien material by producing adhesive-contaminated surfaces              |
| 7      | Scratched      | 1250   | Alien material by a chip due to with mechanically damaged surfaces      |

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

The dataset is provided *"as raw as possible"* and underwent no additional preprocessing steps.
* The steps taken for **renaming** and **compressing** the data are available in this repo: see `pyscrew/tools/create_label_csv.py`

## Experimental Setup

### Equipment
- Automatic screwing station (EV motor control unit assembly)
- Delta PT 40x12 screws (thermoplastic-optimized)
- Target torque: 1.4 Nm (range: 1.2-1.6 Nm)
- Thermoplastic housing components
- Material for the error experiments (lubricant, sandpaper, adhesive)

### Test Protocol
- Each workpiece uniquely identified via DMC
- Two test locations per workpiece (left/right)
- Maximum 25 cycles per location
- 250 unique workpieces
- 12,500 total operations
- 8 unique error classes as decribed [above](#classification-labels-classes)

## Dataset Statistics

### Sample Distribution
- Sample Metrics:
  - Total operations: 12500
  - Unique workpieces: 250
  - Operations per workpiece: 50 (25 cycles x 2 sides)
- Quality Distribution:
  - Normal (OK): 9512 (76.10%)
  - Anomalous (NOK): 2988 (23.90%)

### Distribution by Class

| Value | Name           | Samples | #OK   | #NOK | %OK   | %NOK  |
|-------|---------------|---------|-------|------|-------|-------|
| 0     | Baseline      | 2500    | 2094  | 406  | 83.76 | 16.24 |
| 1     | Up to 50      | 2500    | 2273  | 227  | 90.92 | 9.08  |
| 2     | With water    | 1250    | 1101  | 149  | 88.08 | 11.92 |
| 3     | With lubricant| 1250    | 488   | 762  | 39.04 | 60.96 |
| 4     | Sanded 40     | 1250    | 770   | 480  | 61.60 | 38.40 |
| 5     | Sanded 400    | 1250    | 672   | 578  | 53.76 | 46.24 |
| 6     | With adhesive | 1250    | 1074  | 176  | 85.92 | 14.08 |
| 7     | Scratched     | 1250    | 1040  | 210  | 83.20 | 16.80 |

### Collection Timeline

**Initial Dataset (July 2023)**
- Jul 12-17: Baseline data collection (Class 0: 2500 samples)
- Jul 12-17: Multiple usage tests (Class 1: 2500 samples)
- Jul 18: Lubricant tests (Class 3: 1250 samples)
- Jul 19-20: Surface treatment experiments
  - Coarse sanding tests (Class 4: 1250 samples)
  - Fine sanding tests (Class 5: 1250 samples)

**Extended Collection (April 2024)**
- Apr 15-16: Adhesive contamination tests (Class 6: 1250 samples)
- Apr 22: Surface scratch tests (Class 7: 1250 samples)
- Apr 25: Water contamination tests (Class 2: 1250 samples)

*Note: The extended collection period in April 2024 focused on additional friction variations to complete the dataset with different surface contamination scenarios.*

### Data Quality
- Sampling frequency: 833.33 Hz
- Missing values: 4.03%
- Data completeness: 95.97%

### Key Characteristics
- Group of distinct errors related to surface properties
- Matches similar errors by type and number (e.g. 2&3, 4&5, 6&7)
- Initial anomaly rate: 12.6%
- Peak anomaly rate: 51.6% (in the final cycle 24)

## Usage Guidelines

### Data Access
Recommended approaches:
- Either via JSON library for operation data and Pandas/CSV readers for labels file
- Or via our custom `PyScrew` Python package (available in [this repository](https://github.com/nikolaiwest/pyscrew))

### Analysis Suggestions
- Torque-angle relationship evolution
- Multi-class classification for specific error types
- Clustering-based approaches to identify similar cause-effect-relationships
- Comparison of anomaly effects ("How severe/different are the 7 error classes?")

## Citations
If using this dataset, please cite:
- West, N., Trianni, A. & Deuse, J. (2024). Data-driven analysis of bolted joints in plastic housings with surface-based anomalies using supervised and unsupervised machine learning. CIE51 Proceedings. (DOI will follow after publication of the proceedings)

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