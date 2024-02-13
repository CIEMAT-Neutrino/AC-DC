# AC-DC
After-pulses &amp; Cross-talk from Dark Current

## Introduction
This is a repository to evaluate the xtalk and afterpulses of photosensors from dark current data. For now the supported format is segmented wvfs stored to txt files (see ref. data for more information).
The structure of the data is as follows:
```
data/number/label/Cx--OVy--zzzzz.txt
```
where:
- number is the number of the sensor
- label is the set number (SET1, SET2 for SiPMs mounted on boards -> 6 channels)
- x is the channel number
- y is the overvoltage
- zzzzz is the number of the file

The repository is divided in 3 main parts:
- data: where the data is stored. See setup folder and scripts for more information on how to mount the data.
- scripts: where the main analysis scripts are stored. There is a script (production.py) that is used to produce the data for the analysis.
- notebooks: where the main analysis notebooks are stored. Notebooks read the output of the production.py script and produce the standard plots for the analysis.

Additionally, during the analysis process, folders analysis and images are created inside the data folder. The analysis folder contains the output of the analysis and the images folder contains the plots produced during the analysis.

## Installation

## Workflow