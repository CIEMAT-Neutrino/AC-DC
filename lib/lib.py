import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
import scipy.signal as signal

from rich.progress import track
from scipy.ndimage import gaussian_filter1d

HEADER=3
N_SEGMENTs=50
PRETRIGGER=5e-6 #in s

def SPE_get_ADCs_file(file_path):
    ADCs=np.loadtxt(file_path, delimiter=',', skiprows=5)
    period=ADCs[1,0]-ADCs[0,0]
    ADCs=ADCs[:,1]
    return ADCs,period

def SPE_get_ADCs_file_list(file_list,polarity=1,PED_RANGE=250):
    ADCs_list=[]
    # for file_path in file_list:
    for file_path in track(file_list, description="Processing WVFs"):
        ADCs,period=SPE_get_ADCs_file(file_path)
        ADCs_list.append(ADCs)
    ADCs=np.array(ADCs_list)
    ADCs = (ADCs.T - np.mean(ADCs[:, :PED_RANGE], axis=1).T).T
    ADCs*=polarity
    return ADCs,period

def DC_get_times_file(file_path):
    decimal_numbers = []
    with open(file_path, 'r') as file:
        lines = file.readlines()[HEADER:N_SEGMENTs+HEADER]
        for line in lines:
            words = line.split(',')
            last_word = words[-1]
            decimal_numbers.append(float(last_word))

    windows_times = np.array(decimal_numbers)
    windows_times += PRETRIGGER;
    return np.array(windows_times)

def DC_get_ADCs_file(file_path):
    ADCs=np.loadtxt(file_path, delimiter=',', skiprows=54)
    period=ADCs[1,0]-ADCs[0,0]
    ADCs=ADCs[:,1]

    LEN_SEG=int(ADCs.shape[0]/N_SEGMENTs)
    ADCs=ADCs.reshape((N_SEGMENTs,LEN_SEG))
    return ADCs,period

def DC_read_file(file_path,polarity=1):
    times=DC_get_times_file(file_path)
    ADCs,period=DC_get_ADCs_file(file_path)
    ADCs=ADCs*polarity
    return times, ADCs,period

def smooth_and_find_peaks(ADCs,period, threshold=0.005, PED_RANGE=50):
    smoothed_ADCs = gaussian_filter1d(ADCs, sigma=4, mode='reflect', axis=1) 
    smoothed_ADCs = (smoothed_ADCs.T - np.mean(smoothed_ADCs[:, :PED_RANGE], axis=1).T).T
    peaks = []
    peak_values = []  # New list to store ADC values at each peak
    for row in smoothed_ADCs:
        peak_indices, _ = signal.find_peaks(row, width=50, height=threshold)
        peaks.append(peak_indices*period)
        peak_values.append(row[peak_indices])  # Store ADC values at each peak

    return peaks, peak_values, smoothed_ADCs

def DC_process_file(file_path):
    times, ADCs,period=DC_read_file(file_path)
    peaks,  peak_values, _ = smooth_and_find_peaks(ADCs,period=period)
    return times, peaks, peak_values