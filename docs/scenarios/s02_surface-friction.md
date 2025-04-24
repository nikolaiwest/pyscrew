# Screw Driving Dataset - s02_variations-in-surface-friction

<!-- Dataset Information -->
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14729547.svg)](https://zenodo.org/uploads/14729547)
[![Dataset Size](https://img.shields.io/badge/Dataset_Size-12500_samples-blue)](https://github.com/nikolaiwest/pyscrew)

<!-- Version Information -->
[![Version](https://img.shields.io/badge/Version-v1.2-blue)](https://github.com/nikolaiwest/pyscrew)
[![Updated](https://img.shields.io/badge/Updated-2025/04/17-blue)](https://github.com/nikolaiwest/pyscrew)

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
This dataset examines how different **surface conditions** affect screw driving performance. We tested various *surface modifications* including wear, lubrication, surface treatments, and contamination to create realistic scenarios encountered in manufacturing environments. The dataset includes `12,500` total observations across `8` distinct surface conditions.

The purpose is to analyze how different surface conditions impact screw driving metrics, providing insights for quality control measures and optimal manufacturing parameters under varying surface friction scenarios.

Collection Date: Jul. 2023 - Apr. 2024 *(some errors were recorded later to inspect more friction variations)*

## Quick Start

```python
from pyscrew import get_data

# Load and prepare the data (returns a dictionary)
data = get_data(scenario_name="s02_variations-in-surface-friction")

# Access measurements and labels
x_values = data["torque values"] # Available: torque, angle, time, gradient, step, class
y_values = data["class values"]
```

## Dataset Structure

The dataset consists of three primary components:

1. `/json` directory: Contains 12,500 individual JSON files of unprocessed screw driving operations, each recording the complete measurement data of a single screwing process.
2. `labels.csv`: A metadata file that collects key information from each operation (e.g. for classification). More Details are displayed in the table below.
3. `README.md`: This readme-file providing stand-alone context for the dataset.

### Labels File Structure

The `labels.csv` contains nine columns:

| Column               | Type    | Description                                                      |
|----------------------|---------|------------------------------------------------------------------|
| run_id               | int     | Unique cycle number as recorded by the screw station             |
| file_name            | string  | Name of corresponding JSON file with the measurements            |
| class_value          | string  | Specifies the [respective class](#classification-labels-classes) |
| workpiece_id         | string  | Unique workpiece identifier (14-digit) as data matrix code       |
| workpiece_date       | datetime| Timestamp of when the workpiece was processed                    |
| workpiece_usage      | integer | Previous operations count (0-24): number of screw runs           |
| workpiece_result     | string  | Operation outcome (OK/NOK) as determined by the station          |
| workpiece_location   | string  | Screw position (left/right)                                      |
| scenario_condition   | string  | Experimental condition applied to the sample (normal or fautly)  |
| scenario_exception   | integer | Exception flag for special conditions (0: none)                  |

### Classification Labels (Classes)

| NR    | Name                     | Amount | Description                                                             |
|-------|--------------------------|--------|-------------------------------------------------------------------------|
| 0     | 001_control-group        | 2500   | No additional manipulations, baseline data for reference                |
| 1     | 101_used-upper-workpiece | 2500   | Upper workpiece was used 25 times, showing surface weardown             |
| 2     | 201_lubricant-water      | 1250   | Decreased friction due to water-contaminated workpiece surface          |
| 3     | 202_lubricant-oil-based  | 1250   | Decreased friction due to lubricant-contaminated workpiece surface      |
| 4     | 301_sanding-coarse       | 1250   | Increased friction due to coarse surface treatment by sanding (40 grit) |
| 5     | 302_sanding-fine         | 1250   | Increased friction due to fine surface treatment by sanding (400 grit)  |
| 6     | 401_plastic-adhesive     | 1250   | Alien material by producing adhesive-contaminated surfaces              |
| 7     | 402_surface-chipped      | 1250   | Alien material by a chip due to with mechanically damaged surfaces      |

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
- 8 unique error classes as described [above](#classification-labels-classes)

## Dataset Statistics

### Sample Distribution
- Sample Metrics:
  - Total operations: 12500
  - Unique workpieces: 250
  - Operations per workpiece: 50.0
- Quality Distribution:
  - Normal (OK): 9512 (76.10%)
  - Anomalous (NOK): 2988 (23.90%)

### Distribution by Class

| NR    | Name                     | Samples | #OK   | #NOK  | %OK   | %NOK   |
|-------|--------------------------|---------|-------|-------|-------|--------|
| 0     | 001_control-group        | 2500    | 2094  | 406   | 83.76 | 16.24  |
| 1     | 101_used-upper-workpiece | 2500    | 2273  | 227   | 90.92 | 9.08   |
| 2     | 201_lubricant-water      | 1250    | 1101  | 149   | 88.08 | 11.92  |
| 3     | 202_lubricant-oil-based  | 1250    | 488   | 762   | 39.04 | 60.96  |
| 4     | 301_sanding-coarse       | 1250    | 770   | 480   | 61.60 | 38.40  |
| 5     | 302_sanding-fine         | 1250    | 672   | 578   | 53.76 | 46.24  |
| 6     | 401_plastic-adhesive     | 1250    | 1074  | 176   | 85.92 | 14.08  |
| 7     | 402_surface-chipped      | 1250    | 1040  | 210   | 83.20 | 16.80  |

### Collection Timeline

**July 2023**
- Initial data collection including baseline samples, multiple usage tests, lubricant tests, and surface treatment experiments

**April 2024**
- Extended collection focusing on additional friction variations (adhesive contamination, surface scratch tests, water contamination)

### Data Quality
- Sampling frequency: 833.33 Hz
- Missing values: 4.03%
- Data completeness: 95.97%

### Key Characteristics
- Group of distinct errors related to surface properties
- Matches similar errors by type and number (e.g. classes 201/202, 301/302, 401/402)
- Initial anomaly rate: 0%
- Peak anomaly rate: 23.90%

## Usage Guidelines

### Data Access
Recommended approaches:
- Either via JSON library for operation data and Pandas/CSV readers for labels file
- Or via our custom `PyScrew` Python package (available in [this repository](https://github.com/nikolaiwest/pyscrew))

### Analysis Suggestions
- Torque-angle relationship evolution
- Multi-class classification for specific error types
- Clustering-based approaches to identify similar cause-effect-relationships
- Comparison of anomaly effects ("How severe/different are the 8 error classes?")

## Citations
If using this dataset, please cite:
- West, N., Trianni, A. & Deuse, J. (2024). Detection of surface-based anomalies for self-tapping screws in plastic housings using supervised machine learning. CIE51 Proceedings. (DOI will follow after publication of the proceedings)

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

**Creative Commons Attribution 4.0 International (CC BY 4.0)**

*This dataset is licensed under a Creative Commons Attribution 4.0 International License.*

You are free to:
* **Share** — copy and redistribute the material in any medium or format
* **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
* **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

The full text of this license is available at: https://creativecommons.org/licenses/by/4.0/legalcode

**Citation Requirement**: 

* When using this dataset in academic or research work, please cite:

  > West, N., & Deuse, J. (2024). A Comparative Study of Machine Learning Approaches for Anomaly Detection in Industrial Screw Driving Data. Proceedings of the 57th Hawaii International Conference on System Sciences (HICSS), 1050-1059. https://hdl.handle.net/10125/106504

* For non-academic work, please include the following attribution:

  > Screw Driving Dataset - s02_variations-in-surface-friction by Nikolai West @ RIF/IPS; 
  Source: [github.com/nikolaiwest/pyscrew](https://github.com/nikolaiwest/pyscrew);
  DOI: [10.5281/zenodo.14729547](https://doi.org/10.5281/zenodo.14729547)

*Copyright (c) 2025 Nikolai West @ RIF/IPS*