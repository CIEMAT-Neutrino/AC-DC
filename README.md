# AC-DC

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

After-pulses &amp; Cross-talk from Dark Current

## Introduction

This is a repository to evaluate the xtalk and afterpulses of photosensors from dark current data. For now the supported format is segmented wvfs stored to txt files (see ref. data for more information).
The structure of the data is as follows:

```bash
data/number/label/Cx--OVy--zzzzz.txt
```

where:

- number is the number of the sensor
- label is the set number (SET1, SET2 for SiPMs mounted on boards -> 6 channels)
- x is the channel number
- y is the overvoltage
- zzzzz is the number of the file

The repository is divided in 3 main parts:

- lib: where the main functions are stored.
- scripts: where the setup and axuliary bash scripts are stored to preparate the data for the analysis.
- src: where the main analysis scripts are stored. There is are two scripts (run_DC_analysis.py and run_SPE_analysis.py) that are used to run the analysis. This folder also contains notebooks, which read the output of the analysis scripts and produce the standard plots for the results.

## Installation

To install the repository, clone the repository and install the requirements:

```bash
git clone https://github.com/CIEMAT-Neutrino/AC-DC.git
cd AC-DC
## RECOMMENDED: create a virtual environment
mkdir .venv && cd .venv
/cvmfs/sft.cern.ch/lcg/releases/Python/3.7.3-f4f57/x86_64-centos7-gcc7-opt/bin/python3 -m venv .
source bin/activate
pip install --upgrade pip
## Install the requirements
pip install -r requirements.txt
```

## Workflow

The first step is to setup the local environment. This is done by running the setup.sh script. This script will create the necessary folders and will link the data to the data folder. The data folder is the main folder where the data is stored. The setup.sh script will also create the necessary folders for the analysis.

```bash
bash scripts/setup.sh
```

This script will create the following folders:

- data: where the data is stored. See setup folder and scripts for more information on how to mount the data.
- analysis: where the output of the analysis is stored.
- images: where the plots produced during the analysis are stored.

Additionally, during the analysis process, folders analysis and images are created. The analysis folder contains the output of the analysis and the images folder contains the plots produced during the analysis.

### Data Visualization

To visualize the data, enter the ```src``` folder and run the ```event_display.ipynb``` notebook. This notebook will read the data and produce the event display with the peak finder. Make sure to take a first look at the data before running the analysis.

### Dark Current Analysis

To run the dark current analysis, run the ```run_DC_analysis.py``` script. This script will read the data and produce the dark current plots. The output of the analysis is stored in the analysis folder.

```bash
python src/run_DC_analysis.py -h
python src/run_DC_analysis.py --args*
```

If you feel confident with the parameters, you can run the production script to process all the data. This script will run the analysis for all the data stored in the data folder.

```bash
bash scripts/run_DC_producer.sh
```
