# Screw Driving Dataset - s05_variations-in-upper-workpiece-fabrication

<!-- Dataset Information -->
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14729547.svg)](https://zenodo.org/uploads/14729547)
[![Dataset Size](https://img.shields.io/badge/Dataset_Size-2400_samples-blue)](https://github.com/nikolaiwest/pyscrew)

<!-- Version Information -->
[![Version](https://img.shields.io/badge/Version-v1.2-blue)](https://github.com/nikolaiwest/pyscrew)
[![Updated](https://img.shields.io/badge/Updated-2025/04/17-blue)](https://github.com/nikolaiwest/pyscrew)

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
This dataset examines how **variations in injection molding parameters** affect screw driving performance in plastic housing assemblies. We systematically modified *production parameters of the upper workpiece* including glass fiber content, recyclate content, switching point, injection velocity, and mold temperature. These variations simulate real-world manufacturing fluctuations and material batch changes commonly encountered in production environments. The dataset includes `2,400` total observations across `42` distinct experimental conditions.

The purpose is to analyze how injection molding parameter variations impact screw driving metrics, providing insights for quality control measures in plastic component production and assembly processes, as well as the detectability of material and process variations through fastening data analysis.

Collection Date: Dec. 2024

## Quick Start

```python
from pyscrew import get_data

# Load and prepare the data (returns a dictionary)
data = get_data(scenario_name="s05_variations-in-upper-workpiece-fabrication")

# Access measurements and labels
x_values = data["torque values"] # Available: torque, angle, time, gradient, step, class
y_values = data["class values"]
```

## Dataset Structure

The dataset consists of three primary components:

1. `/json` directory: Contains 2,400 individual JSON files of unprocessed screw driving operations, each recording the complete measurement data of a single screwing process.
   - Each class directory contains data for a specific injection molding parameter variation
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

| NR    | Name                          | Amount | Description                                                             |
|-------|-------------------------------|--------|-------------------------------------------------------------------------|
| 0     | 101_glass-fiber-content-30    | 80     | Standard reference material with 30% glass fiber content in the plastic granulate; represents the baseline specification for the upper workpiece material composition with optimal mechanical properties and flow characteristics |
| 1     | 102_glass-fiber-content-28    | 80     | Reduced glass fiber content to 28% by mixing base material with unreinforced granules of the same base polymer; simulates minor material batch fluctuations with decreased reinforcement properties |
| 2     | 103_glass-fiber-content-26    | 80     | Reduced glass fiber content to 26% by mixing base material with unreinforced granules of the same base polymer; simulates moderate material batch fluctuations with noticeably decreased reinforcement properties and altered flow behavior |
| 3     | 104_glass-fiber-content-24    | 80     | Reduced glass fiber content to 24% by mixing base material with unreinforced granules of the same base polymer; simulates significant material batch fluctuations with substantially decreased reinforcement properties and modified viscosity |
| 4     | 105_glass-fiber-content-22    | 80     | Reduced glass fiber content to 22% by mixing base material with unreinforced granules of the same base polymer; simulates major material batch fluctuations with considerably decreased reinforcement properties and pronounced changes in flow characteristics |
| 5     | 106_glass-fiber-content-20    | 80     | Reduced glass fiber content to 20% by mixing base material with unreinforced granules of the same base polymer; simulates severe material batch fluctuations with compromised mechanical properties and altered thermal behavior |
| 6     | 107_glass-fiber-content-18    | 80     | Reduced glass fiber content to 18% by mixing base material with unreinforced granules of the same base polymer; simulates extreme material batch fluctuations with substantially reinforcement properties |
| 7     | 201_recyclate-content-000     | 80     | Standard reference material with 0% recyclate content; represents the baseline specification using only virgin material with optimal and consistent mechanical properties |
| 8     | 202_recyclate-content-010     | 80     | Addition of 10% regrind material to simulate minimal recycled material use; regrind produced from laboratory-milled workpieces of the same plastic, introducing minor variations in material properties and fiber length distribution |
| 9     | 203_recyclate-content-020     | 80     | Addition of 20% regrind material to simulate moderate recycled material use; regrind produced from laboratory-milled workpieces of the same plastic, introducing noticeable variations in viscosity and mechanical properties |
| 10    | 204_recyclate-content-030     | 80     | Addition of 30% regrind material to simulate significant recycled material use; regrind produced from laboratory-milled workpieces of the same plastic, introducing substantial variations in fiber length distribution and flow characteristics |
| 11    | 205_recyclate-content-040     | 80     | Addition of 40% regrind material to simulate high recycled material use; regrind produced from laboratory-milled workpieces of the same plastic, introducing considerable variations in material homogeneity and mechanical performance |
| 12    | 206_recyclate-content-050     | 80     | Addition of 50% regrind material to simulate very high recycled material use; regrind produced from laboratory-milled workpieces of the same plastic, creating equal parts virgin and recycled material with significantly altered viscosity profiles |
| 13    | 207_recyclate-content-060     | 80     | Addition of 60% regrind material to simulate predominantly recycled material use; regrind produced from laboratory-milled workpieces of the same plastic, creating a majority recyclate mixture with pronounced changes in fiber orientation and length |
| 14    | 208_recyclate-content-070     | 80     | Addition of 70% regrind material to simulate heavily recycled material use; regrind produced from laboratory-milled workpieces of the same plastic, introducing major variations in flow behavior and molecular weight distribution |
| 15    | 209_recyclate-content-080     | 80     | Addition of 80% regrind material to simulate extensively recycled material use; regrind produced from laboratory-milled workpieces of the same plastic, with only 20% virgin material remaining, substantially affecting material consistency |
| 16    | 210_recyclate-content-090     | 80     | Addition of 90% regrind material to simulate nearly complete recycled material use; regrind produced from laboratory-milled workpieces of the same plastic, with minimal virgin material addition, resulting in significantly degraded fiber reinforcement |
| 17    | 211_recyclate-content-100     | 80     | Complete 100% regrind material to simulate full recyclate use; regrind produced from laboratory-milled workpieces of the same plastic, using no virgin material, representing extreme case with max variation in fiber length distribution and orientation |
| 18    | 301_switching-point-15-1      | 40     | First reference condition with 15 cm³ switching point; standard setting where system transitions from velocity-controlled injection to pressure-controlled packing; recorded in first test series for baseline comparison |
| 19    | 302_switching-point-16        | 40     | Increased switching point to 16 cm³; minor change in transition from velocity-controlled injection to pressure-controlled packing, simulating slight variance in non-return valve closing behavior |
| 20    | 303_switching-point-17        | 40     | Increased switching point to 17 cm³; moderate change in transition from velocity-controlled injection to pressure-controlled packing, simulating noticeable variance in non-return valve closing behavior |
| 21    | 304_switching-point-18        | 40     | Increased switching point to 18 cm³; significant change in transition from velocity-controlled injection to pressure-controlled packing, simulating substantial variance in non-return valve closing behavior |
| 22    | 305_switching-point-19        | 40     | Increased switching point to 19 cm³; major change in transition from velocity-controlled injection to pressure-controlled packing, simulating considerable variance in non-return valve closing behavior |
| 23    | 306_switching-point-15-2      | 40     | Second reference condition with 15 cm³ switching point; repeat of standard setting recorded in second test series to verify reproducibility across testing periods |
| 24    | 307_switching-point-14        | 40     | Decreased switching point to 14 cm³; minor reduction in melt volume at transition, simulating slight early closing of non-return valve, altering the filling and packing phases relationship |
| 25    | 308_switching-point-13        | 40     | Decreased switching point to 13 cm³; moderate reduction in melt volume at transition, simulating noticeable early closing of non-return valve, substantially changing the filling-packing relationship |
| 26    | 309_switching-point-12        | 40     | Decreased switching point to 12 cm³; significant reduction in melt volume at transition, simulating substantial early closing of non-return valve, considerably altering packing phase initiation |
| 27    | 310_switching-point-11        | 40     | Decreased switching point to 11 cm³; extreme reduction in melt volume at transition, simulating major early closing of non-return valve, dramatically changing the process dynamics during molding |
| 28    | 401_injection-velocity-60-1   | 40     | First reference condition with 60 cm³/s primary injection velocity (secondary velocity at 90 cm³/s); standard setting recorded in first test series for baseline comparison of flow behavior |
| 29    | 402_injection-velocity-70     | 40     | Increased primary injection velocity to 70 cm³/s (secondary velocity at 100 cm³/s); accelerated melt flow during filling phase, simulating minor variation in velocity control of screw movement |
| 30    | 403_injection-velocity-80     | 40     | Increased primary injection velocity to 80 cm³/s (secondary velocity at 110 cm³/s); substantially accelerated melt flow during filling phase, simulating moderate variation in velocity control |
| 31    | 404_injection-velocity-90     | 40     | Increased primary injection velocity to 90 cm³/s (secondary velocity at 120 cm³/s); significantly accelerated melt flow during filling phase, simulating considerable variation in velocity control |
| 32    | 405_injection-velocity-100    | 40     | Increased primary injection velocity to 100 cm³/s (secondary velocity at 130 cm³/s); dramatically accelerated melt flow during filling phase, simulating major variation in velocity control |
| 33    | 406_injection-velocity-60-2   | 40     | Second reference condition with 60 cm³/s primary injection velocity (secondary velocity at 90 cm³/s); repeat of standard setting recorded in second test series to verify reproducibility |
| 34    | 407_injection-velocity-50     | 40     | Decreased primary injection velocity to 50 cm³/s (secondary velocity at 80 cm³/s); slowed melt flow during filling phase, simulating minor reduction in screw movement control |
| 35    | 408_injection-velocity-40     | 40     | Decreased primary injection velocity to 40 cm³/s (secondary velocity at 70 cm³/s); substantially slowed melt flow during filling phase, simulating moderate reduction in screw movement control |
| 36    | 409_injection-velocity-30     | 40     | Decreased primary injection velocity to 30 cm³/s (secondary velocity at 60 cm³/s); significantly slowed melt flow during filling phase, simulating considerable reduction in screw movement control |
| 37    | 410_injection-velocity-20     | 40     | Decreased primary injection velocity to 20 cm³/s (secondary velocity at 50 cm³/s); dramatically slowed melt flow during filling phase, simulating extreme reduction in screw movement control |
| 38    | 501_mold-temperature-30       | 40     | Standard mold temperature of 30°C; baseline cooling medium temperature flowing through the injection mold cooling channels, representing optimal thermal conditions for part solidification |
| 39    | 502_mold-temperature-35       | 40     | Increased mold temperature to 35°C; moderately elevated cooling medium temperature, simulating minor fluctuation in the cooling circuit possibly caused by temperature control unit variation |
| 40    | 503_mold-temperature-40       | 40     | Increased mold temperature to 40°C; substantially elevated cooling medium temperature, simulating significant fluctuation in the cooling circuit possibly caused by deposits in cooling channels |
| 41    | 504_mold-temperature-45       | 40     | Increased mold temperature to 45°C; dramatically elevated cooling medium temperature, simulating extreme fluctuation in the cooling circuit, considerably altering part solidification dynamics |

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
- Injection molding machine with variable parameter control
- Material preparation equipment for mixing different glass fiber and recyclate contents

### Test Protocol
- Each workpiece uniquely identified via DMC
- 1,200 unique workpieces
- 2,400 total operations
- 42 distinct experimental conditions organized into 5 parameter groups:
  - Group 1: Glass fiber content variations (classes 101-107)
  - Group 2: Recyclate content variations (classes 201-211)
  - Group 3: Switching point variations (classes 301-310)
  - Group 4: Injection velocity variations (classes 401-410)
  - Group 5: Mold temperature variations (classes 501-504)

## Dataset Statistics

### Sample Distribution
- Sample Metrics:
  - Total operations: 2400
  - Unique workpieces: 1200
  - Operations per workpiece: 2.0
- Quality Distribution:
  - Normal (OK): 2397 (99.88%)
  - Anomalous (NOK): 3 (0.12%)

### Distribution by Class

| NR    | Name                          | Samples | #OK  | #NOK | %OK   | %NOK  |
|-------|-------------------------------|---------|------|------|-------|-------|
| 0     | 101_glass-fiber-content-30    | 80      | 80   | 0    | 100.0 | 0.0   |
| 1     | 102_glass-fiber-content-28    | 80      | 80   | 0    | 100.0 | 0.0   |
| 2     | 103_glass-fiber-content-26    | 80      | 80   | 0    | 100.0 | 0.0   |
| 3     | 104_glass-fiber-content-24    | 80      | 80   | 0    | 100.0 | 0.0   |
| 4     | 105_glass-fiber-content-22    | 80      | 80   | 0    | 100.0 | 0.0   |
| 5     | 106_glass-fiber-content-20    | 80      | 80   | 0    | 100.0 | 0.0   |
| 6     | 107_glass-fiber-content-18    | 80      | 79   | 1    | 98.75 | 1.25  |
| 7     | 201_recyclate-content-000     | 80      | 79   | 1    | 98.75 | 1.25  |
| 8     | 202_recyclate-content-010     | 80      | 80   | 0    | 100.0 | 0.0   |
| 9     | 203_recyclate-content-020     | 80      | 80   | 0    | 100.0 | 0.0   |
| 10    | 204_recyclate-content-030     | 80      | 80   | 0    | 100.0 | 0.0   |
| 11    | 205_recyclate-content-040     | 80      | 80   | 0    | 100.0 | 0.0   |
| 12    | 206_recyclate-content-050     | 80      | 79   | 1    | 98.75 | 1.25  |
| 13    | 207_recyclate-content-060     | 80      | 80   | 0    | 100.0 | 0.0   |
| 14    | 208_recyclate-content-070     | 80      | 80   | 0    | 100.0 | 0.0   |
| 15    | 209_recyclate-content-080     | 80      | 80   | 0    | 100.0 | 0.0   |
| 16    | 210_recyclate-content-090     | 80      | 80   | 0    | 100.0 | 0.0   |
| 17    | 211_recyclate-content-100     | 80      | 80   | 0    | 100.0 | 0.0   |
| 18    | 301_switching-point-15-1      | 40      | 40   | 0    | 100.0 | 0.0   |
| 19    | 302_switching-point-16        | 40      | 40   | 0    | 100.0 | 0.0   |
| 20    | 303_switching-point-17        | 40      | 40   | 0    | 100.0 | 0.0   |
| 21    | 304_switching-point-18        | 40      | 40   | 0    | 100.0 | 0.0   |
| 22    | 305_switching-point-19        | 40      | 40   | 0    | 100.0 | 0.0   |
| 23    | 306_switching-point-15-2      | 40      | 40   | 0    | 100.0 | 0.0   |
| 24    | 307_switching-point-14        | 40      | 40   | 0    | 100.0 | 0.0   |
| 25    | 308_switching-point-13        | 40      | 40   | 0    | 100.0 | 0.0   |
| 26    | 309_switching-point-12        | 40      | 40   | 0    | 100.0 | 0.0   |
| 27    | 310_switching-point-11        | 40      | 40   | 0    | 100.0 | 0.0   |
| 28    | 401_injection-velocity-60-1   | 40      | 40   | 0    | 100.0 | 0.0   |
| 29    | 402_injection-velocity-70     | 40      | 40   | 0    | 100.0 | 0.0   |
| 30    | 403_injection-velocity-80     | 40      | 40   | 0    | 100.0 | 0.0   |
| 31    | 404_injection-velocity-90     | 40      | 40   | 0    | 100.0 | 0.0   |
| 32    | 405_injection-velocity-100    | 40      | 40   | 0    | 100.0 | 0.0   |
| 33    | 406_injection-velocity-60-2   | 40      | 40   | 0    | 100.0 | 0.0   |
| 34    | 407_injection-velocity-50     | 40      | 40   | 0    | 100.0 | 0.0   |
| 35    | 408_injection-velocity-40     | 40      | 40   | 0    | 100.0 | 0.0   |
| 36    | 409_injection-velocity-30     | 40      | 40   | 0    | 100.0 | 0.0   |
| 37    | 410_injection-velocity-20     | 40      | 40   | 0    | 100.0 | 0.0   |
| 38    | 501_mold-temperature-30       | 40      | 40   | 0    | 100.0 | 0.0   |
| 39    | 502_mold-temperature-35       | 40      | 40   | 0    | 100.0 | 0.0   |
| 40    | 503_mold-temperature-40       | 40      | 40   | 0    | 100.0 | 0.0   |
| 41    | 504_mold-temperature-45       | 40      | 40   | 0    | 100.0 | 0.0   |

### Collection Timeline

This dataset was collected over a one-week period in December 2024, with careful organization of parameter variations to minimize environmental influences.

**December 2024**
- Dec 5: Collection of glass fiber content variations (classes 101-107)
- Dec 6: Collection of initial recyclate content variations (classes 201-206)
- Dec 9: Collection of remaining recyclate content variations (classes 207-211) and initial switching point variations (classes 301-303)
- Dec 11: Collection of remaining switching point variations (classes 304-310), all injection velocity variations (classes 401-410), and all mold temperature variations (classes 501-504)

### Data Quality
- Sampling frequency: 833.33 Hz
- Missing values: 2.64%
- Data completeness: 97.36%

### Key Characteristics
- Systematic variation of 5 distinct injection molding parameters
- Gradient variations within each parameter group to study progressive effects
- Very high OK rate (99.88%) indicating parameter variations had minimal impact on process success
- Initial anomaly rate: 0%
- Peak anomaly rate: 0.12%
- Duplicate reference conditions (e.g., 301/306, 401/406) to verify reproducibility

## Usage Guidelines

### Data Access
Recommended approaches:
- Either via JSON library for operation data and Pandas/CSV readers for labels file
- Or via our custom `PyScrew` Python package (available in [this repository](https://github.com/nikolaiwest/pyscrew))

### Analysis Suggestions
- Parameter sensitivity analysis (which molding parameters most affect screw driving)
- Correlation between material composition and torque-angle behavior
- Predictive modeling for screw driving behavior based on material parameters
- Material property detection via screw driving signal analysis
- Regression analysis for quality prediction based on process parameters
- Comparison of glass fiber vs. recyclate content effects on fastening performance
- Identification of critical threshold values for various process parameters

## Citations
If using this dataset, please cite:
- West, N., & Deuse, J. (2025). Industrial screw driving dataset collection: Time series data for process monitoring and anomaly detection [Data set]. https://doi.org/10.5281/zenodo.14729547

*We are currently working on a separate paper for this dataset and will update the citation once it releases.*

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

  > Screw Driving Dataset - s05_variations-in-upper-workpiece-fabrication by Nikolai West @ RIF/IPS;
  Source: [github.com/nikolaiwest/pyscrew](https://github.com/nikolaiwest/pyscrew);
  DOI: [10.5281/zenodo.14729547](https://doi.org/10.5281/zenodo.14729547)

*Copyright (c) 2025 Nikolai West @ RIF/IPS*