# Follow the structure of the wFit_SiPM.C macro to create a python function that fits the SiPM response
import os
import stat
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from itertools import product
from rich import print as rprint
from scipy.optimize import curve_fit
# suppress warnings 
warnings.filterwarnings('ignore')

from src.utils import get_project_root
root = get_project_root()


# TF1* fG1 = new TF1("fG1","[1]*[0]*log(10)*(10**x)*exp(-[0]*(10**x))");
def dark_current_SiPM(x, A, B):
    return A * np.log(10) * (10**x) * np.exp(-B * (10**x))

# TF1* fG2 = new TF1("fG2","[1]*[2]*(([2]-1)/[2])*(10**x)*log(10)*(1+([0]*(10**x))/[2])**(-[2])");
def bursts_SiPM(x, C, D, E):
    return C * ((E-1)/E) * (10**x) * np.log(10) * (1 + (D * (10**x)) / E)**(-E)    

# Combine the two functions
def SiPM_response(x, A, B, C, D, E):
    return dark_current_SiPM(x, A, B) + bursts_SiPM(x, C, D, E)


def fit_SiPM_response(df:pd.DataFrame,filter_data:bool=False,save:bool=False,debug:bool=False) -> pd.DataFrame:
    numbers = df['Number'].unique()
    labels = df['Set'].unique()
    ovs = df['OV'].unique()
    chs = df['Channel'].unique()

    df['Frequency'] = 0
    df['LogDeltaT'] = 0
    for n, label, ov, ch in product(numbers, labels, ovs, chs): # type: ignore
        data = df[(df['Number'] == n) & (df['Set'] == label) & (df['OV'] == ov) & (df['Channel'] == ch)]
        # Append new df to existing df and add n,label,ov and ch as new columns with the same length as the new df
        data['Frequency'] = 1/data['DeltaT']
        data['LogDeltaT'] = np.log10(data['DeltaT'])
        # Update df with Frequency and LogDeltaT
        df.loc[(df['Number'] == n) & (df['Set'] == label) & (df['OV'] == ov) & (df['Channel'] == ch), 'Frequency'] = data['Frequency']
        df.loc[(df['Number'] == n) & (df['Set'] == label) & (df['OV'] == ov) & (df['Channel'] == ch), 'LogDeltaT'] = data['LogDeltaT']
        # Make a histogram of the frequency using np.histogram
        amp_lim = data["Amplitude"].max()
        if filter_data:
            with open('{root}/analysis/SPE.json') as json_file:
                SPE_data = json.load(json_file)
            amp_lim = SPE_data[str(n)][label]["OV"][str(ov)]

        hist, bin_edges = np.histogram(data[data["Amplitude"] < amp_lim]["LogDeltaT"], bins=200)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        try:
            popt, pcov = curve_fit(SiPM_response, bin_centers, hist, p0=[1e2,1,1e2,1e2,2], bounds=([0,1e-2,0,5e1,0],[1e6,5e1,1e6,1e9,10]))
        except RuntimeError:
            rprint(f'Fit failed for {n} {label} OV{ov} Ch{ch}')
            return df
        perr = np.sqrt(np.diag(pcov))

        # Plot the histogram and the fit
        fig, ax = plt.subplots()
        ax.plot(bin_centers, hist, label='Data', drawstyle='steps-mid')
        ax.plot(bin_centers, SiPM_response(bin_centers, *popt), label='Fit')
        ax.plot(bin_centers, dark_current_SiPM(bin_centers, *popt[:2]), label=f'DarkCurrent: {popt[1]:.2e} [Hz]',ls='--')
        ax.plot(bin_centers, bursts_SiPM(bin_centers, *popt[2:]), label=f'Bursts: {popt[3]:.2e}',ls='--')
        ax.set_title(f'SiPM response fit for {n} {label} OV{ov} Ch{ch}')
        ax.set_xlabel('log10(DeltaT)')
        ax.set_ylabel('Counts')
        ax.legend()

        if save:
            image_path = f'{root}/images/{n}/{label}/'
            analysis_path = f'{root}/analysis/{n}/{label}/'
            os.system(f'mkdir -p {image_path}')
            os.system(f'mkdir -p {analysis_path}')
            plt.savefig(f'{image_path}/{n}_{label}_DC_data_fit_{ov}_{ch}.png', dpi=300)
            plt.close()
            with open(f'{root}/analysis/{n}/{label}/{n}_{label}_DC_data_fit_{ov}_{ch}.csv', 'w') as file:
                file.write(f'Number,Set,OV,Channel,A,dA,DarkCurrent,dDarkCurrent,B,dB,Bursts,dBursts,E,dE\n')
                file.write(f'{n},{label},{ov},{ch},{popt[0]},{perr[0]},{popt[1]},{perr[1]},{popt[2]},{perr[2]},{popt[3]},{perr[3]},{popt[4]},{perr[4]}\n')
            file.close()
            os.chmod(f'{root}/analysis/{n}/{label}/{n}_{label}_DC_data_fit_{ov}_{ch}.csv', stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        
    
    if debug: rprint(f'Updated df with Frequency and LogDeltaT')
    return df


def gauss(x,a,x0,sigma):
    return a*np.exp(-0.5*np.power((x-x0)/sigma,2))


def gaussian_train(x, *params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        height = params[i]
        center = params[i+1]
        width  = params[i+2]
        y += gauss(x, height, center, width)
    return y


def fit_gaussians(x, y, *p0):
    assert x.shape == y.shape, "Input arrays must have the same shape."
    popt, pcov = curve_fit(gaussian_train, x,y, p0=p0[0])
    perr = np.sqrt(np.diag(pcov))
    fit_y=gaussian_train(x,*popt)
    chi_squared = np.sum((y[abs(fit_y)>0.1] - fit_y[abs(fit_y)>0.1]) ** 2 / fit_y[abs(fit_y)>0.1]) / (y.size - len(popt))
    return popt, perr, fit_y, chi_squared
    
    
def Q_out(V_out,period):
    # Volts / osc resistance * time
    q=V_out/50*period
    return q