# Screw Driving Dataset - s04_variations-in-assembly-conditions-2

<!-- Dataset Information -->
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14729547.svg)](https://zenodo.org/uploads/14729547)
[![Dataset Size](https://img.shields.io/badge/Dataset_Size-5000_samples-blue)](https://github.com/nikolaiwest/pyscrew)

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
This dataset examines how different **screw and component faults** affect screw driving performance. We tested various *fault conditions* including thread modifications, surface conditions, component modifications, material variations, and process parameter changes to create realistic fault scenarios encountered in manufacturing environments. The dataset includes 5000 total observations across `25` distinct experimental conditions, recorded over a compressed two-week period. 

Unlike previous scenarios, each error class directory contains both normal (OK) and abnormal (NOK) observations collected in alternating sequence (usually `5` OK followed by `5` NOK) to minimize environmental condition influences. This methodological improvement enables direct comparison between *normal* and *faulty* conditions within the same experimental context.

The purpose is to analyze how different fault conditions impact screw driving metrics, providing insights for quality control measures and fault detection capabilities under varying screw driving failure scenarios. The experimental design with five distinct groups of `24` errors and interleaved normal/abnormal samples enables more robust analysis of error patterns by reducing temporal bias compared to `s03`. The knowledge gained from `s03` directly informed these methodological improvements, resulting in a dataset with higher consistency and reduced confounding variables.

Collection Date: Sept. 2024

## Quick Start

```python
from pyscrew import get_data

# Load and prepare the data (returns a dictionary)
data = get_data(scenario_name="s04_variations-in-assembly-conditions-2")

# Access measurements and labels
x_values = data["torque values"] # Available: torque, angle, time, gradient, step, class
y_values = data["class values"]
```

## Dataset Structure

The dataset consists of three primary components:

1. `/json` directory: Contains 5,000 individual JSON files of unprocessed screw driving operations, each recording the complete measurement data of a single screwing process.
   - Unlike previous scenarios, each error class directory (e.g., `504_decreased-torque/`) contains both normal (OK) and abnormal (NOK) observations
   - This methodological improvement enables direct comparison of normal and faulty conditions within the same experimental setup
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
| 0     | 001_control-group             | 200    | No manipulations, standard reference data for comparison with other experiment groups; recorded for s04 using standard parameters (torque 1.4 Nm, process window 1.2-1.6 Nm) and original components according to specification |
| 1     | 101_deformed-thread           | 200    | Damaged thread by mechanically deforming the lower section (approx. 2nd-3rd thread turn); characterized by strong compression of the thread profile; creating increased resistance during fastening due to irregular thread engagement |
| 2     | 102_filed-screw-tip           | 200    | Removed thread at the screw tip on one side through mechanical processing; first 2-3mm of one screw side no longer have thread structure; causing difficult screw insertion and irregular thread formation |
| 3     | 103_glued-screw-tip           | 200    | Modified thread behavior by applying metal adhesive to the first 3-4mm of the screw tip; created an even layer approx. 0.1mm thick; partially filling the thread profile and creating increased resistance during fastening |
| 4     | 104_coated-screw              | 200    | Altered surface properties by using a screw with different coating; modified friction coefficient between screw and component material; affecting torque-angle relationship during the fastening process |
| 5     | 105_worn-out-screw            | 200    | Degraded screw quality by using screws with significant wear marks from multiple use cycles; thread flanks show abrasion patterns and partially removed coating; simulating reused fasteners in production environments |
| 6     | 201_damaged-contact-surface   | 200    | Compromised seating surface by creating two symmetrical damages in the upper part contact area; damages made with 8mm drill to approx. 0.5mm depth; impairing the flat contact surface needed for proper screw head seating |
| 7     | 202_broken-contact-surface    | 200    | Reduced structural integrity by creating continuous crack in the upper part contact surface; damage extends from screw hole across entire contact area; severely compromising mechanical stability of the connection |
| 8     | 203_metal-ring-upper-part     | 200    | Modified pressure distribution by integrating metallic O-ring in the screw head contact area; ring dimensions 8.5mm outer diameter, 5.5mm inner diameter, 1.5mm width; creating altered force distribution and changed torque transmission characteristics |
| 9     | 204_rubber-ring-upper-part    | 200    | Altered seating dynamics by inserting rubber O-ring (6mm outer diameter) in the contact surface; elastic material changes compressibility characteristics during tightening; affecting torque transmission and preload development |
| 10    | 205_different-material        | 200    | Changed component properties by using upper part made from non-standard plastic material; material exhibits different elastic modulus and strength characteristics; affecting thread formation and torque-angle relationship |
| 11    | 301_plastic-pin-screw-hole    | 200    | Obstructed thread engagement by placing plastic pin in the screw-in area of the lower part; pin made of material similar to the component; reducing effective screw-in depth and preventing proper fastener seating |
| 12    | 302_enlarged-screw-hole       | 200    | Reduced thread formation by mechanically enlarging lower part screw hole using 4mm drill; expanded diameter matches screw outer dimensions; preventing proper thread formation and reducing holding strength |
| 13    | 303_less-glass-fiber          | 200    | Weakened component structure by using lower part with reduced glass fiber content (10% vs. specified 30%); altered material composition leads to lower strength and increased deformability; particularly affecting thread formation and stability |
| 14    | 304_glued-screw-hole          | 200    | Modified thread interface by applying plastic adhesive to the inner surface of the screw hole; adhesive forms thin layer narrowing diameter by approx. 0.1-0.2mm; increasing insertion resistance and altering thread engagement |
| 15    | 305_gap-between-parts         | 200    | Prevented proper component mating by introducing 1.1mm metal wire between upper and lower parts; created consistent gap preventing complete component joining; significantly affecting preload development and connection stability |
| 16    | 401_surface-lubricant         | 200    | Decreased friction by contaminating head contact surface with multi-purpose oil (WD40); lubricant reduces coefficient of friction between screw head and contact surface; altering torque transmission characteristics during final tightening phase |
| 17    | 402_surface-moisture          | 200    | Modified surface conditions by applying water particles (approx. 0.5ml as two drops) to contact area; moisture temporarily reduces friction between screw head and component surface; creating inconsistent torque transmission |
| 18    | 403_plastic-chip              | 200    | Disrupted thread formation by placing elongated plastic chip (approx. 3cm length) in screw hole; chip wraps around screw during insertion; affecting both insertion behavior and thread formation quality |
| 19    | 404_increased-temperature     | 200    | Altered material properties through thermal conditioning of components for ten minutes in oven; elevated temperature changes plastic stiffness and flow characteristics; affecting thread formation and torque-angle relationship |
| 20    | 405_decreased-temperature     | 200    | Modified component properties by cooling parts in insulated box with ice (10kg), protected by foil packaging; lowered temperature increases material brittleness; changing deformation behavior and thread formation characteristics |
| 21    | 501_increased-ang-velocity    | 200    | Accelerated installation process by increasing angular velocity 10% across all phases; modified dynamics create "hard" screwing case; changing heat generation and affecting thread formation dynamics |
| 22    | 502_decreased-ang-velocity    | 200    | Slowed installation process by reducing angular velocity 10% in all process phases; decreased speed creates "softer" screwing case with extended process time; altering thread formation characteristics and thermal conditions |
| 23    | 503_increased-torque          | 200    | Heightened connection preload by increasing target tightening torque 0.1 Nm to 1.5 Nm; adjusted process window to 1.3-1.7 Nm; creating higher mechanical load and different stress distribution in connection |
| 24    | 504_decreased-torque          | 200    | Reduced connection preload by decreasing target tightening torque 0.1 Nm to 1.3 Nm; adjusted process window to 1.1-1.5 Nm; producing lower clamping force and affecting overall connection stability |

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
- Various materials for error simulations (adhesives, metal/rubber rings, temperature control equipment, etc.)

### Test Protocol
- Each workpiece uniquely identified via DMC
- 2,500 unique workpieces
- 5,000 total operations
- 25 distinct experimental conditions (1 control + 24 error classes)
- Alternating sequence of normal and faulty operations (5 OK followed by 5 NOK) within each error class
- Each error class directory contains both normal and abnormal operations related to that specific experimental condition
- Compressed data collection period (2 weeks) to maintain consistent environmental conditions
- Organized into 5 error groups:
  - Group 1: Screw quality deviations (classes 101-105)
  - Group 2: Contact surface modifications (classes 201-205)
  - Group 3: Component/thread modifications (classes 301-305)
  - Group 4: Environmental/interface conditions (classes 401-405)
  - Group 5: Process parameter variations (classes 501-504)

## Dataset Statistics

### Sample Distribution
- Sample Metrics:
  - Total operations: 5000
  - Unique workpieces: 2500
  - Operations per workpiece: 2.0
- Quality Distribution:
  - Normal (OK): 4307 (86.14%)
  - Anomalous (NOK): 693 (13.86%)

### Distribution by Class

| NR    | Name                          | Samples | #OK  | #NOK | %OK   | %NOK  |
|-------|-------------------------------|---------|------|------|-------|-------|
| 0     | 001_control-group             | 200     | 199  | 1    | 99.50 | 0.50  |
| 1     | 101_deformed-thread           | 200     | 187  | 13   | 93.50 | 6.50  |
| 2     | 102_filed-screw-tip           | 200     | 189  | 11   | 94.50 | 5.50  |
| 3     | 103_glued-screw-tip           | 200     | 186  | 14   | 93.00 | 7.00  |
| 4     | 104_coated-screw              | 200     | 166  | 34   | 83.00 | 17.00 |
| 5     | 105_worn-out-screw            | 200     | 163  | 37   | 81.50 | 18.50 |
| 6     | 201_damaged-contact-surface   | 200     | 196  | 4    | 98.00 | 2.00  |
| 7     | 202_broken-contact-surface    | 200     | 164  | 36   | 82.00 | 18.00 |
| 8     | 203_metal-ring-upper-part     | 200     | 123  | 77   | 61.50 | 38.50 |
| 9     | 204_rubber-ring-upper-part    | 200     | 110  | 90   | 55.00 | 45.00 |
| 10    | 205_different-material        | 200     | 194  | 6    | 97.00 | 3.00  |
| 11    | 301_plastic-pin-screw-hole    | 200     | 169  | 31   | 84.50 | 15.50 |
| 12    | 302_enlarged-screw-hole       | 200     | 99   | 101  | 49.50 | 50.50 |
| 13    | 303_less-glass-fiber          | 200     | 148  | 52   | 74.00 | 26.00 |
| 14    | 304_glued-screw-hole          | 200     | 198  | 2    | 99.00 | 1.00  |
| 15    | 305_gap-between-parts         | 200     | 199  | 1    | 99.50 | 0.50  |
| 16    | 401_surface-lubricant         | 200     | 89   | 111  | 44.50 | 55.50 |
| 17    | 402_surface-moisture          | 200     | 188  | 12   | 94.00 | 6.00  |
| 18    | 403_plastic-chip              | 200     | 193  | 7    | 96.50 | 3.50  |
| 19    | 404_increased-temperature     | 200     | 164  | 36   | 82.00 | 18.00 |
| 20    | 405_decreased-temperature     | 200     | 199  | 1    | 99.50 | 0.50  |
| 21    | 501_increased-ang-velocity    | 200     | 200  | 0    | 100.00| 0.00  |
| 22    | 502_decreased-ang-velocity    | 200     | 196  | 4    | 98.00 | 2.00  |
| 23    | 503_increased-torque          | 200     | 190  | 10   | 95.00 | 5.00  |
| 24    | 504_decreased-torque          | 200     | 198  | 2    | 99.00 | 1.00  |

**Note:** *Each class (001 to 504) contains `100` normal and `100` faulty/anormal observations. Information on the class label can be found in the respective `CSV` file.* 

### Collection Timeline

This dataset was collected over a concentrated four-day period to minimize environmental variations and temporal biases, with a methodologically rigorous experimental design.

**September 2024**
- Entire dataset was collected in a compressed timeframe (September 3-9, 2024)
- Control samples were recorded in alternating sequence with error data (5 OK followed by 5 NOK)
- Daily collection focused on specific error groups to maintain experimental consistency:
  - Sept 3: Primarily screw quality deviations (Group 1)
  - Sept 4: Focus on contact surface and environmental modifications (Groups 2 and 4)
  - Sept 5: Component/thread modifications and temperature conditions (Group 3 and part of Group 4)
  - Sept 6: Process parameter variations and remaining classes (Group 5 and remaining samples)
  - Sept 9: Completion of any remaining samples (n=20)

### Data Quality
- Sampling frequency: 833.33 Hz
- Missing values: 2.80%
- Data completeness: 97.20%

### Key Characteristics
- Each error class contains both normal (OK) and abnormal (NOK) operations
- Methodologically rigorous design with 5 distinct error groups
- Alternating normal-abnormal sampling pattern (5 OK, 5 NOK) within each error class
- Compressed collection timeframe to minimize environmental variations
- Consistent sample size (200) for each experimental condition
- Initial anomaly rate: 0%
- Peak anomaly rate: 13.86%

## Usage Guidelines

### Data Access
Recommended approaches:
- Either via JSON library for operation data and Pandas/CSV readers for labels file
- Or via our custom `PyScrew` Python package (available in [this repository](https://github.com/nikolaiwest/pyscrew))

### Analysis Suggestions
- Paired analysis of normal and abnormal operations within the same error class
- Comparative analysis of the five distinct error groups
- ML-based classification for distinguishing error types
- Detection performance comparison with unstructured error scenarios (e.g., s03)
- Time-series analysis of torque-angle relationships across different error types
- Effect of process parameter variations on screw driving performance
- Material property impact study (temperature, composition, surface conditions)
- Intra-class variability study (comparing OK vs NOK observations in the same error condition)

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

  > Screw Driving Dataset - s04_variations-in-assembly-conditions-2 by Nikolai West @ RIF/IPS;
  Source: [github.com/nikolaiwest/pyscrew](https://github.com/nikolaiwest/pyscrew);
  DOI: [10.5281/zenodo.14729547](https://doi.org/10.5281/zenodo.14729547)

*Copyright (c) 2025 Nikolai West @ RIF/IPS*