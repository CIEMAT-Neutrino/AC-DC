from re import A
import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
import scipy.signal as signal

from rich import print as rprint
from rich.progress import track
from scipy.ndimage import gaussian_filter1d


def merge_processed_files(file_list, data:str="DC", polarity=-1, width=3, threshold=0.001, header:int=3, segments:int=50, debug:bool=False):
    ADCs = []
    for file_path in track(file_list, description="Processing WVFs"):
        _, this_ADCs, _, _ = process_file(file_path, data=data, polarity=polarity,width=width,threshold=threshold, header=header, segments=segments, debug=debug)
        ADCs.append(this_ADCs[0])
    
    return np.asarray(ADCs)


def process_file(file_path:str, data:str="DC", polarity:int=-1, width:int=3, threshold:float=0.001,  header:int=3, segments:int=50, debug:bool = False):
    event_times, ADCs, period = read_file(file_path, data=data, header=header, segments=segments, debug=debug)
    ADCs = np.asarray(ADCs)
    ADCs=ADCs*polarity
    ped_lim = get_ped_lim(ADCs, buffer=50)
    ADCs = (ADCs.T - np.mean(ADCs[:, :ped_lim], axis=1).T).T
    peaks,  peak_values = find_peaks(ADCs, period=period,  width=width, threshold=threshold, debug=debug)
    
    return event_times, ADCs, peaks, peak_values


def get_ped_lim(ADCs, buffer:int=50, debug:bool = False):
    peak = np.argmax(ADCs[:,:],axis=1)
    values,counts = np.unique(peak, return_counts=True)
    ped_lim = values[np.argmax(counts)]-buffer
    if ped_lim <= buffer: ped_lim = buffer
    
    return ped_lim


def get_times(file_path, header:int=3, segments:int=50, debug:bool=False):
    decimal_numbers = []
    with open(file_path, 'r') as file:
        lines = file.readlines()[header:segments+header]
        for line in lines:
            words = line.split(',')
            last_word = words[-1]
            decimal_numbers.append(float(last_word))

    windows_times = np.array(decimal_numbers)
    
    return np.array(windows_times)


def get_DC_ADCs(file_path, header:int=3, segments:int=50, debug:bool=False):
    ADCs=np.loadtxt(file_path, delimiter=',', skiprows=54)
    period=ADCs[1,0]-ADCs[0,0]
    ADCs=ADCs[:,1]

    seg_len=int(ADCs.shape[0]/segments)
    ADCs=ADCs.reshape((segments,seg_len))
    
    return ADCs,period


def get_SPE_ADCs(file_path, header:int=5, segments:int=0, debug:bool=False):
    ADCs=np.loadtxt(file_path, delimiter=',', skiprows=header)
    period=ADCs[1,0]-ADCs[0,0]
    ADCs=ADCs[:,1]
    
    return [ADCs],period


def read_file(file_path, data:str="DC", header:int=3, segments:int=50, debug:bool=False):
    event_times=get_times(file_path, header=header, segments=segments, debug=debug)
    if data=="DC":
        ADCs,period=get_DC_ADCs(file_path, header=header, segments=segments, debug=debug)
    if data=="SPE":
        ADCs,period=get_SPE_ADCs(file_path, header=header, segments=segments, debug=debug)
    # if debug: rprint(f"Read {ADCs.shape[0]} segments of {ADCs.shape[1]} samples each")

    return event_times, ADCs, period


def find_peaks(ADCs, period, width=3, height:float=0.001, threshold:float=0.001, debug:bool=False):
    peaks = []
    peak_values = []  # New list to store ADC values at each peak
    for row in ADCs:
        peak_indices, _ = signal.find_peaks(row, width=width, height=height, threshold=threshold)
        peaks.append(peak_indices*period)
        peak_values.append(row[peak_indices])  # Store ADC values at each peak

    return peaks, peak_values


def smooth_ADCs(ADCs, debug:bool=False):
    # TODO: Implement a better smoothing algorithm, so that the peak amplitude is not affected!
    smoothed_ADCs = gaussian_filter1d(ADCs, sigma=4, mode='reflect', axis=1) 
    
    return smoothed_ADCs