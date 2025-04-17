# Screw Driving Dataset - s06_variations-in-lower-workpiece-fabrication

<!-- Dataset Information -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12345678.svg)](https://zenodo.org/uploads/12345678)
[![Dataset Size](https://img.shields.io/badge/Dataset_Size-7482_samples-blue)](https://github.com/nikolaiwest/pyscrew)

<!-- Version Information -->
[![Version](https://img.shields.io/badge/Version-v1.2.0-blue)](https://github.com/nikolaiwest/pyscrew)
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
This dataset investigates how **variations in injection molding parameters** affect screw driving performance in plastic housing assemblies. We systematically modified *production parameters of the lower workpiece* including cooling time, mold temperature, glass fiber content, switching point, and injection velocity. These variations simulate real-world manufacturing fluctuations and material batch changes commonly encountered in production environments. The dataset includes `7,482` total observations across `44` distinct experimental conditions.

The purpose is to analyze how injection molding parameter variations impact screw driving metrics, providing insights for quality control measures in plastic component production and assembly processes, as well as the detectability of material and process variations through fastening data analysis.

Collection Date: Nov. 2024

## Quick Start

```python
from pyscrew import get_data

# Load and prepare the data (returns a dictionary)
data = get_data(scenario_name="s06_variations-in-lower-workpiece-fabrication")

# Access measurements and labels
x_values = data["torque values"] # Available: torque, angle, time, gradient, step, class
y_values = data["class values"]
```

## Dataset Structure

The dataset consists of three primary components:

1. `/json` directory: Contains 7,482 individual JSON files of unprocessed screw driving operations, each recording the complete measurement data of a single screwing process.
   - Each class directory contains data for a specific injection molding parameter variation
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

| NR    | Name                          | Amount | Description                                                             |
|-------|-------------------------------|--------|-------------------------------------------------------------------------|
| 0     | 001_reference_01              | 240    | Standard reference material and process parameters; represents the baseline for all comparisons with optimal mechanical properties and flow characteristics |
| 1     | 101_cooling_time_25           | 269    | Cooling time of 25 seconds; baseline cooling time setting providing optimal curing conditions for the workpiece and serving as the reference for the first test series |
| 2     | 102_cooling_time_26           | 237    | Increased cooling time to 26 seconds; minor extension of curing phase, simulating slight variations in cooling efficiency due to normal process fluctuations |
| 3     | 103_cooling_time_27           | 232    | Increased cooling time to 27 seconds; moderate extension of curing phase, simulating noticeable variations in cooling efficiency across production cycles |
| 4     | 104_cooling_time_28           | 236    | Increased cooling time to 28 seconds; significant extension of curing phase, simulating substantial variations in cooling efficiency throughout the process |
| 5     | 105_cooling_time_29           | 200    | Increased cooling time to 29 seconds; considerable extension of curing phase, simulating major variations in cooling efficiency impacting solidification dynamics |
| 6     | 106_cooling_time_30           | 156    | Increased cooling time to 30 seconds; extensive extension of curing phase, simulating extreme variations in cooling efficiency with pronounced impact on cycle time |
| 7     | 107_cooling_time_25           | 190    | Second reference condition with 25 seconds cooling time; repeat of standard setting recorded in second test series to verify reproducibility across testing periods |
| 8     | 201_mold_temperature_30       | 252    | Standard mold temperature of 30°C; baseline cooling medium temperature flowing through the injection mold cooling channels, representing optimal thermal conditions for part solidification |
| 9     | 202_mold_temperature_35       | 160    | Increased mold temperature to 35°C; moderately elevated cooling medium temperature, simulating minor fluctuation in the cooling circuit possibly caused by temperature control unit variation |
| 10    | 203_mold_temperature_45       | 330    | Increased mold temperature to 45°C; substantially elevated cooling medium temperature, simulating significant fluctuation in the cooling circuit possibly caused by deposits in cooling channels |
| 11    | 204_mold_temperature_55       | 248    | Increased mold temperature to 55°C; highly elevated cooling medium temperature, simulating severe fluctuation in the cooling circuit, significantly altering part cooling and crystallization behavior |
| 12    | 205_mold_temperature_65       | 166    | Increased mold temperature to 65°C; extremely elevated cooling medium temperature, simulating critical fluctuation in the cooling circuit, dramatically changing solidification dynamics and cycle time |
| 13    | 301_glass_fiber_content_30    | 326    | Standard reference material with 30% glass fiber content in the plastic granulate; represents the baseline specification for the upper workpiece material composition with optimal mechanical properties and flow characteristics |
| 14    | 302_glass_fiber_content_25    | 268    | Reduced glass fiber content to 25% by mixing base material with unreinforced granules of the same base polymer; simulates moderate material batch fluctuations with decreased reinforcement properties and altered flow behavior |
| 15    | 303_glass_fiber_content_20    | 274    | Reduced glass fiber content to 20% by mixing base material with unreinforced granules of the same base polymer; simulates severe material batch fluctuations with compromised mechanical properties and altered thermal behavior |
| 16    | 304_glass_fiber_content_15    | 254    | Reduced glass fiber content to 15% by mixing base material with unreinforced granules of the same base polymer; simulates major material batch fluctuations with substantially decreased reinforcement properties and pronounced changes in flow characteristics |
| 17    | 305_glass_fiber_content_10    | 104    | Reduced glass fiber content to 10% by mixing base material with unreinforced granules of the same base polymer; simulates extreme material batch fluctuations with minimally reinforced polymer exhibiting dramatically altered viscosity and mechanical properties |
| 18    | 401_switching_point_22_1      | 352    | First reference condition with 22 cm³ switching point; standard setting where system transitions from velocity-controlled injection to pressure-controlled packing; recorded in first test series for baseline comparison |
| 19    | 402_switching_point_20        | 205    | Decreased switching point to 20 cm³; minor reduction in melt volume at transition, simulating slight early closing of non-return valve, altering the filling and packing phases relationship |
| 20    | 403_switching_point_18        | 100    | Decreased switching point to 18 cm³; moderate reduction in melt volume at transition, simulating noticeable early closing of non-return valve, changing the filling-packing relationship |
| 21    | 404_switching_point_17        | 100    | Decreased switching point to 17 cm³; significant reduction in melt volume at transition, simulating substantial early closing of non-return valve, considerably altering packing phase initiation |
| 22    | 405_switching_point_16        | 154    | Decreased switching point to 16 cm³; major reduction in melt volume at transition, simulating considerable early closing of non-return valve, dramatically changing packing dynamics |
| 23    | 406_switching_point_15        | 98     | Decreased switching point to 15 cm³; extreme reduction in melt volume at transition, simulating major early closing of non-return valve, significantly impacting part quality and dimensions |
| 24    | 407_switching_point_14        | 108    | Decreased switching point to 14 cm³; severe reduction in melt volume at transition, representing critical deviation in process control with pronounced effect on cavity pressure development |
| 25    | 408_switching_point_13        | 96     | Decreased switching point to 13 cm³; minimal melt volume at transition, representing extreme deviation in process control with possible incomplete filling prior to packing phase initiation |
| 26    | 409_switching_point_22_2      | 100    | Second reference condition with 22 cm³ switching point; repeat of standard setting recorded in second test series to verify reproducibility across testing periods |
| 27    | 410_switching_point_24        | 98     | Increased switching point to 24 cm³; minor increase in melt volume at transition, simulating slight delay in non-return valve closing behavior, modifying filling-packing relationship |
| 28    | 411_switching_point_26        | 95     | Increased switching point to 26 cm³; moderate increase in melt volume at transition, simulating noticeable delay in non-return valve closing, substantially altering packing phase initiation |
| 29    | 412_switching_point_28        | 102    | Increased switching point to 28 cm³; significant increase in melt volume at transition, simulating substantial delay in non-return valve closing, considerably changing process dynamics |
| 30    | 413_switching_point_30        | 100    | Increased switching point to 30 cm³; major increase in melt volume at transition, simulating considerable delay in non-return valve closing, dramatically altering pressure profile |
| 31    | 414_switching_point_32        | 104    | Increased switching point to 32 cm³; extreme increase in melt volume at transition, simulating critical delay in non-return valve closing with potential risk of flash formation |
| 32    | 501_injection_velocity_030_1  | 350    | First reference condition with 30 cm³/s primary injection velocity; standard setting recorded in first test series for baseline comparison of flow behavior and filling patterns |
| 33    | 502_injection_velocity_050    | 100    | Increased primary injection velocity to 50 cm³/s; moderately accelerated melt flow during filling phase, simulating minor variation in velocity control of screw movement |
| 34    | 503_injection_velocity_070    | 98     | Increased primary injection velocity to 70 cm³/s; substantially accelerated melt flow during filling phase, simulating moderate variation in velocity control with altered shear conditions |
| 35    | 504_injection_velocity_090    | 110    | Increased primary injection velocity to 90 cm³/s; significantly accelerated melt flow during filling phase, simulating considerable variation in velocity control with pronounced shear effects |
| 36    | 505_injection_velocity_110    | 98     | Increased primary injection velocity to 110 cm³/s; highly accelerated melt flow during filling phase, simulating major variation in velocity control with potential fiber orientation changes |
| 37    | 506_injection_velocity_130    | 130    | Increased primary injection velocity to 130 cm³/s; dramatically accelerated melt flow during filling phase, simulating extreme variation in velocity control with altered pressure development |
| 38    | 507_injection_velocity_150    | 98     | Increased primary injection velocity to 150 cm³/s; extremely accelerated melt flow during filling phase, creating severe shear conditions and potentially affecting material properties |
| 39    | 508_injection_velocity_170    | 102    | Increased primary injection velocity to 170 cm³/s; maximum accelerated melt flow during filling phase, creating critical shear conditions with high potential for molded-in stress |
| 40    | 509_injection_velocity_030_2  | 100    | Second reference condition with 30 cm³/s primary injection velocity; repeat of standard setting recorded in second test series to verify reproducibility across testing periods |
| 41    | 510_injection_velocity_025    | 138    | Decreased primary injection velocity to 25 cm³/s; slightly slowed melt flow during filling phase, simulating minor reduction in screw movement control with reduced shear conditions |
| 42    | 511_injection_velocity_020    | 106    | Decreased primary injection velocity to 20 cm³/s; moderately slowed melt flow during filling phase, simulating significant reduction in screw movement control with minimal shear |
| 43    | 512_injection_velocity_015    | 98     | Decreased primary injection velocity to 15 cm³/s; dramatically slowed melt flow during filling phase, simulating extreme reduction in screw movement control with potential for premature freezing |

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
- Material preparation equipment for mixing different glass fiber contents

### Test Protocol
- Each workpiece uniquely identified via DMC
- 3,743 unique workpieces
- 7,482 total operations
- 44 distinct experimental conditions organized into 5 parameter groups:
  - Group 1: Reference condition (class 001)
  - Group 2: Cooling time variations (classes 101-107)
  - Group 3: Mold temperature variations (classes 201-205)
  - Group 4: Glass fiber content variations (classes 301-305)
  - Group 5: Switching point variations (classes 401-414)
  - Group 6: Injection velocity variations (classes 501-512)

## Dataset Statistics

### Sample Distribution
- Sample Metrics:
  - Total operations: 7482
  - Unique workpieces: 3743
  - Operations per workpiece: 2.0
- Quality Distribution:
  - Normal (OK): 7274 (97.22%)
  - Anomalous (NOK): 208 (2.78%)

### Distribution by Class

| NR    | Name                          | Samples | #OK  | #NOK | %OK   | %NOK  |
|-------|-------------------------------|---------|------|------|-------|-------|
| 0     | 001_reference_01              | 240     | 238  | 2    | 99.17 | 0.83  |
| 1     | 101_cooling_time_25           | 269     | 264  | 5    | 98.14 | 1.86  |
| 2     | 102_cooling_time_26           | 237     | 237  | 0    | 100.0 | 0.0   |
| 3     | 103_cooling_time_27           | 232     | 232  | 0    | 100.0 | 0.0   |
| 4     | 104_cooling_time_28           | 236     | 236  | 0    | 100.0 | 0.0   |
| 5     | 105_cooling_time_29           | 200     | 200  | 0    | 100.0 | 0.0   |
| 6     | 106_cooling_time_30           | 156     | 156  | 0    | 100.0 | 0.0   |
| 7     | 107_cooling_time_25           | 190     | 189  | 1    | 99.47 | 0.53  |
| 8     | 201_mold_temperature_30       | 252     | 251  | 1    | 99.6  | 0.4   |
| 9     | 202_mold_temperature_35       | 160     | 160  | 0    | 100.0 | 0.0   |
| 10    | 203_mold_temperature_45       | 330     | 330  | 0    | 100.0 | 0.0   |
| 11    | 204_mold_temperature_55       | 248     | 248  | 0    | 100.0 | 0.0   |
| 12    | 205_mold_temperature_65       | 166     | 166  | 0    | 100.0 | 0.0   |
| 13    | 301_glass_fiber_content_30    | 326     | 325  | 1    | 99.69 | 0.31  |
| 14    | 302_glass_fiber_content_25    | 268     | 268  | 0    | 100.0 | 0.0   |
| 15    | 303_glass_fiber_content_20    | 274     | 244  | 30   | 89.05 | 10.95 |
| 16    | 304_glass_fiber_content_15    | 254     | 168  | 86   | 66.14 | 33.86 |
| 17    | 305_glass_fiber_content_10    | 104     | 59   | 45   | 56.73 | 43.27 |
| 18    | 401_switching_point_22_1      | 352     | 348  | 4    | 98.86 | 1.14  |
| 19    | 402_switching_point_20        | 205     | 202  | 3    | 98.54 | 1.46  |
| 20    | 403_switching_point_18        | 100     | 99   | 1    | 99.0  | 1.0   |
| 21    | 404_switching_point_17        | 100     | 99   | 1    | 99.0  | 1.0   |
| 22    | 405_switching_point_16        | 154     | 152  | 2    | 98.7  | 1.3   |
| 23    | 406_switching_point_15        | 98      | 98   | 0    | 100.0 | 0.0   |
| 24    | 407_switching_point_14        | 108     | 108  | 0    | 100.0 | 0.0   |
| 25    | 408_switching_point_13        | 96      | 95   | 1    | 98.96 | 1.04  |
| 26    | 409_switching_point_22_2      | 100     | 100  | 0    | 100.0 | 0.0   |
| 27    | 410_switching_point_24        | 98      | 98   | 0    | 100.0 | 0.0   |
| 28    | 411_switching_point_26        | 95      | 90   | 5    | 94.74 | 5.26  |
| 29    | 412_switching_point_28        | 102     | 101  | 1    | 99.02 | 0.98  |
| 30    | 413_switching_point_30        | 100     | 96   | 4    | 96.0  | 4.0   |
| 31    | 414_switching_point_32        | 104     | 101  | 3    | 97.12 | 2.88  |
| 32    | 501_injection_velocity_030_1  | 350     | 346  | 4    | 98.86 | 1.14  |
| 33    | 502_injection_velocity_050    | 100     | 99   | 1    | 99.0  | 1.0   |
| 34    | 503_injection_velocity_070    | 98      | 97   | 1    | 98.98 | 1.02  |
| 35    | 504_injection_velocity_090    | 110     | 110  | 0    | 100.0 | 0.0   |
| 36    | 505_injection_velocity_110    | 98      | 98   | 0    | 100.0 | 0.0   |
| 37    | 506_injection_velocity_130    | 130     | 130  | 0    | 100.0 | 0.0   |
| 38    | 507_injection_velocity_150    | 98      | 98   | 0    | 100.0 | 0.0   |
| 39    | 508_injection_velocity_170    | 102     | 102  | 0    | 100.0 | 0.0   |
| 40    | 509_injection_velocity_030_2  | 100     | 100  | 0    | 100.0 | 0.0   |
| 41    | 510_injection_velocity_025    | 138     | 135  | 3    | 97.83 | 2.17  |
| 42    | 511_injection_velocity_020    | 106     | 105  | 1    | 99.06 | 0.94  |
| 43    | 512_injection_velocity_015    | 98      | 96   | 2    | 97.96 | 2.04  |

### Collection Timeline

This dataset was collected over a three-week period in November 2024, with careful organization of parameter variations to minimize environmental influences.

**November 2024**
- Nov 7: Collection of reference conditions (class 001) and initial cooling time variations (classes 101-103)
- Nov 8: Collection of remaining cooling time variations (classes 103-107)
- Nov 11: Collection of initial mold temperature variations (classes 201-203)
- Nov 18: Collection of remaining mold temperature variations (classes 203-205) and initial glass fiber content variations (classes 301-302)
- Nov 19: Collection of remaining glass fiber content variations (classes 302-305)
- Nov 20: Collection of initial switching point variations (classes 401-407)
- Nov 21: Collection of remaining switching point variations (classes 407-414) and initial injection velocity variations (class 501)
- Nov 22: Collection of injection velocity variations (classes 501-509)
- Nov 25: Collection of remaining injection velocity variations (classes 509-512)

### Data Quality
- Sampling frequency: 833.33 Hz
- Missing values: 2.64%
- Data completeness: 97.36%

### Key Characteristics
- Systematic variation of 5 distinct injection molding parameters
- Gradient variations within each parameter group to study progressive effects
- Strong correlation between reduced glass fiber content and increased failure rates
- Initial anomaly rate: 0%
- Peak anomaly rate: 2.78%
- Multiple reference conditions (e.g., 101/107, 401/409, 501/509) to verify reproducibility
- Significant impact of reduced glass fiber content on screw driving quality (up to 43.27% NOK rate)
- Most parameters showing minimal impact on screw driving quality until extreme values

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
- Comparison of glass fiber content thresholds for acceptable fastening performance
- Identification of critical threshold values for various process parameters
- Comparative analysis with upper workpiece fabrication variations (s05 dataset)

## Citations
If using this dataset, please cite:
- --> add Zenodo Citation here

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