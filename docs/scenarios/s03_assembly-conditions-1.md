# Screw Driving Dataset - s03_variations-in-assembly-conditions-1

<!-- Dataset Information -->
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14729547.svg)](https://zenodo.org/uploads/14729547)
[![Dataset Size](https://img.shields.io/badge/Dataset_Size-1700_samples-blue)](https://github.com/nikolaiwest/pyscrew)

<!-- Version Information -->
[![Version](https://img.shields.io/badge/Version-v1.2-blue)](https://github.com/nikolaiwest/pyscrew)
[![Updated](https://img.shields.io/badge/Updated-2025/05/13-blue)](https://github.com/nikolaiwest/pyscrew)

<!-- Publication Information -->
[![Paper](https://img.shields.io/badge/DOI-10.24251%2FHICSS.2024.126-green)](https://hdl.handle.net/10125/106504)
[![ResearchGate](https://img.shields.io/badge/ResearchGate-00CCBB?logo=ResearchGate&logoColor=white)](https://www.researchgate.net/publication/379822823_A_Comparative_Study_of_Machine_Learning_Approaches_for_Anomaly_Detection_in_Industrial_Screw_Driving_Data)

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
This dataset examines how different **screw and component faults** affect screw driving performance. We tested *various fault conditions* including washer modifications, thread deformations, interface interferences, structural modifications, and alignment issues to create realistic fault scenarios encountered in manufacturing environments. The dataset includes `1,700` total observations across `26` distinct experimental conditions.

The purpose is to analyze how different fault conditions impact screw driving metrics, providing insights for quality control measures and fault detection capabilities under varying screw driving failure scenarios.

Collection Date: Feb. 2023 - May 2024

## Quick Start

```python
from pyscrew import get_data

# Load and prepare the data (returns a dictionary)
data = get_data(scenario_name="s03_variations-in-assembly-conditions-1")

# Access measurements and labels
x_values = data["torque values"] # Available: torque, angle, time, gradient, step, class
y_values = data["class values"]
```

## Dataset Structure

The dataset consists of three primary components:

1. `/json` directory: Contains 1,700 individual JSON files of unprocessed screw driving operations, each recording the complete measurement data of a single screwing process.
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

| NR    | Name                              | Amount | Description                                                             |
|-------|-----------------------------------|--------|-------------------------------------------------------------------------|
| 0     | 001_control-group-1               | 100    | No manipulations, standard reference data for comparison with other experiment groups; recorded for s03 in March 2023 |
| 1     | 002_control-group-2               | 100    | No manipulations, standard reference data for comparison with other experiment groups; recorded for s03 in February 2024 |
| 2     | 003_control-group-from-s01        | 200    | No manipulations like 001; the observations were taken from s01-001 control group, using first cycles only to maintain comparability with other experiments |
| 3     | 004_control-group-from-s02        | 100    | No manipulations like 001; the observations were taken from s02-001 control group, using first cycles only to maintain comparability with other experiments |
| 4     | 101_m4-washer-in-upper-piece      | 50     | Reduced screw insertion depth using a custom-cut polyamide washer with 4mm inner diameter; the washer was placed inside the upper part during fastening and secured together with the screw, creating controlled thread interference |
| 5     | 102_m3-washer-in-upper-piece      | 50     | Reduced screw insertion depth using a standard M3 polyamide washer; the washer was placed inside the upper part during fastening and secured together with the screw, creating controlled thread interference |
| 6     | 103_m3-half-washer-in-upper-part  | 50     | Reduced screw insertion depth and asymmetric load distribution using half of an M3 polyamide washer; the half-washer was placed inside the upper part during fastening and secured together with the screw, creating non-uniform thread engagement |
| 7     | 201_adhesive-thread               | 50     | Modified thread behavior by applying a metal adhesive to the screw tip, creating partial binding and increased resistance during fastening due to secondary material interference |
| 8     | 202_deformed-thread-1             | 100    | Damaged thread by mechanically deforming multiple thread sections, causing irregular engagement and variations in torque requirements; reforded for s03 in March 2023 |
| 9     | 203_deformed-thread-2             | 50     | Damaged thread by mechanically like 202; observations collected under similar experimental conditions but recorded three months later, in June 2023 |
| 10    | 301_material-in-the-screw-head    | 50     | Compromised tool engagement by applying melted adhesive to the Delta PT screw head, causing driver slippage during automated fastening and inconsistent torque transfer |
| 11    | 302_material-in-the-lower-part    | 50     | Inserted plastic adhesive into the lower workpiece's screw-in hole, creating higher mechanical opposition as the screw enters and rotates during tightening |
| 12    | 401_drilling-out-the-workpiece    | 50     | Reduced thread engagement by enlarging the pilot holes in the lower part with a fine drill, decreasing available material for thread formation and weakening the connection |
| 13    | 402_shortening-the-screw-1        | 50     | Caused rotation angle tolerance deviations by removing approximately two thread turns and the screw tip using a saw, reducing total length of thread engagement and tip |
| 14    | 403_shortening-the-screw-2        | 50     | Caused rotation angle tolerance deviations like 402; observations collected under similar experimental conditions but recorded three months later, in September 2023 |
| 15    | 404_tearing-off-the-screw-1       | 50     | Simulated catastrophic screw failure by partially sawing through the screw shaft just below the screw head, causing complete fastener failure during assembly, recorded in June 2023 |
| 16    | 405_tearing-off-the-screw-2       | 50     | Simulated catastrophic screw failure like 404; observations collected under similar experimental conditions but recorded three months later, in September 2023 |
| 17    | 501_offset-of-the-screw-hole      | 50     | Created horizontal misalignment by using a polyamide washer to offset the screwdriver relative to the joining part; effectively reducing the through-hole so the screw contacts the washer before reaching the lower part |
| 18    | 502_offset-of-the-work-piece      | 50     | Generated angular misalignment between screw axis and insertion tube by placing foreign material between component and tool carrier (on just one side), resulting in angled fastening and non-perpendicular insertion |
| 19    | 601_surface-used                  | 100    | Upper workpiece was used 25 times, showing surface weardown; runs were taken from s02-101 using only the first screw cycles with no thread/surface degradation |
| 20    | 602_surface-moisture              | 50     | Decreased friction due to water-contaminated workpiece surface; runs were taken from s02-201 using only the first screw cycles with no thread/surface degradation |
| 21    | 603_surface-lubricant             | 50     | Decreased friction due to lubricant-contaminated workpiece surface; runs were taken from s02-202 using only the first screw cycles with no thread/surface degradation |
| 22    | 604_surface-adhesive              | 50     | Alien material by producing adhesive-contaminated surfaces; runs were taken from s02-401 using only the first screw cycles with no thread/surface degradation |
| 23    | 605_surface-sanded-40             | 50     | Increased friction due to coarse surface treatment by sanding (40 grit); runs were taken from s02-301 using only the first screw cycles with no thread/surface degradation |
| 24    | 606_surface-sanded-400            | 50     | Increased friction due to fine surface treatment by sanding (400 grit); runs were taken from s02-302 using only the first screw cycles with no thread/surface degradation |
| 25    | 607_surface-scratched             | 50     | Alien material by a chip due to with mechanically damaged surfaces; runs were taken from s02-402 using only the first screw cycles with no thread/surface degradation |

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
- Various materials for error simulations (washers, adhesives, drills, etc.)

### Test Protocol
- Each workpiece uniquely identified via DMC
- 869 unique workpieces
- 1,700 total operations
- 26 unique experimental conditions as described [above](#classification-labels-classes)

## Dataset Statistics

### Sample Distribution
- Sample Metrics:
  - Total operations: 1700
  - Unique workpieces: 869
  - Operations per workpiece: 1.96
- Quality Distribution:
  - Normal (OK): 1067 (62.76%)
  - Anomalous (NOK): 633 (37.24%)

### Distribution by Class

| NR    | Name                              | Samples | #OK  | #NOK | %OK   | %NOK  |
|-------|-----------------------------------|---------|------|------|-------|-------|
| 0     | 001_control-group-1               | 100     | 100  | 0    | 100.0 | 0.0   |
| 1     | 002_control-group-2               | 100     | 96   | 4    | 96.0  | 4.0   |
| 2     | 003_control-group-from-s01        | 200     | 200  | 0    | 100.0 | 0.0   |
| 3     | 004_control-group-from-s02        | 100     | 100  | 0    | 100.0 | 0.0   |
| 4     | 101_m4-washer-in-upper-piece      | 50      | 6    | 44   | 12.0  | 88.0  |
| 5     | 102_m3-washer-in-upper-piece      | 50      | 0    | 50   | 0.0   | 100.0 |
| 6     | 103_m3-half-washer-in-upper-part  | 50      | 1    | 49   | 2.0   | 98.0  |
| 7     | 201_adhesive-thread               | 50      | 43   | 7    | 86.0  | 14.0  |
| 8     | 202_deformed-thread-1             | 100     | 94   | 6    | 94.0  | 6.0   |
| 9     | 203_deformed-thread-2             | 50      | 5    | 45   | 10.0  | 90.0  |
| 10    | 301_material-in-the-screw-head    | 50      | 22   | 28   | 44.0  | 56.0  |
| 11    | 302_material-in-the-lower-part    | 50      | 37   | 13   | 74.0  | 26.0  |
| 12    | 401_drilling-out-the-workpiece    | 50      | 0    | 50   | 0.0   | 100.0 |
| 13    | 402_shortening-the-screw-1        | 50      | 1    | 49   | 2.0   | 98.0  |
| 14    | 403_shortening-the-screw-2        | 50      | 2    | 48   | 4.0   | 96.0  |
| 15    | 404_tearing-off-the-screw-1       | 50      | 0    | 50   | 0.0   | 100.0 |
| 16    | 405_tearing-off-the-screw-2       | 50      | 0    | 50   | 0.0   | 100.0 |
| 17    | 501_offset-of-the-screw-hole      | 50      | 1    | 49   | 2.0   | 98.0  |
| 18    | 502_offset-of-the-work-piece      | 50      | 49   | 1    | 98.0  | 2.0   |
| 19    | 601_surface-used                  | 100     | 99   | 1    | 99.0  | 1.0   |
| 20    | 602_surface-moisture              | 50      | 50   | 0    | 100.0 | 0.0   |
| 21    | 603_surface-lubricant             | 50      | 2    | 48   | 4.0   | 96.0  |
| 22    | 604_surface-adhesive              | 50      | 45   | 5    | 90.0  | 10.0  |
| 23    | 605_surface-sanded-40             | 50      | 43   | 7    | 86.0  | 14.0  |
| 24    | 606_surface-sanded-400            | 50      | 44   | 6    | 88.0  | 12.0  |
| 25    | 607_surface-scratched             | 50      | 27   | 23   | 54.0  | 46.0  |

### Collection Timeline

This dataset was collected across multiple phases to systematically explore different error types and to allow comparison of similar errors across time.

**February 2023 - June 2023**
- Initial collection of control groups and several error conditions

**July 2023 - September 2023**
- Collection of washer modifications, thread deformations, and various surface condition experiments

**February 2024 - May 2024**
- Collection of additional control group data and completion of remaining experimental conditions

### Data Quality
- Sampling frequency: 833.33 Hz
- Missing values: 3.65%
- Data completeness: 96.35%

### Key Characteristics
- Wide variety of error types (26 distinct experimental conditions)
- Some error conditions recorded at different time periods for comparison
- Contains both original experiments and selections from other scenarios (s01, s02)
- Initial anomaly rate: 0%
- Peak anomaly rate: 37.24%

## Usage Guidelines

### Data Access
Recommended approaches:
- Either via JSON library for operation data and Pandas/CSV readers for labels file
- Or via our custom `PyScrew` Python package (available in [this repository](https://github.com/nikolaiwest/pyscrew))

### Analysis Suggestions
- Error type categorization and classification
- Comparative analysis between similar error types recorded at different times
- Cross-scenario analysis using data from multiple scenarios (s01, s02, s03)
- Fault severity ranking based on impact on screw driving performance
- Machine learning approaches for anomaly detection in diverse error conditions

## Citations
If using this dataset, please cite:
- West, N., & Deuse, J. (2025). Industrial screw driving dataset collection: Time series data for process monitoring and anomaly detection [Data set]. https://doi.org/10.5281/zenodo.14729547
*We are currently not planning to publish a paper focussing s03, so please simply cite the zenodo dataset when using the data.*

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

  > West, N., & Deuse, J. (2025). Industrial screw driving dataset collection: Time series data for process monitoring and anomaly detection [Data set]. https://doi.org/10.5281/zenodo.14729547

* For non-academic work, please include the following attribution:

  > Screw Driving Dataset - s03_variations-in-assembly-conditions-1 by Nikolai West @ RIF/IPS; 
  Source: [github.com/nikolaiwest/pyscrew](https://github.com/nikolaiwest/pyscrew);
  DOI: [10.5281/zenodo.14729547](https://doi.org/10.5281/zenodo.14729547)

*Copyright (c) 2025 Nikolai West @ RIF/IPS*