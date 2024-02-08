# Follow the structure of the wFit_SiPM.C macro to create a python function that fits the SiPM response
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# TF1* fG1 = new TF1("fG1","[1]*[0]*log(10)*(10**x)*exp(-[0]*(10**x))");
def fG1_SiPM_response(x, A, B):
    return A * np.log(10) * (10**x) * np.exp(-B * (10**x))
# TF1* fG2 = new TF1("fG2","[1]*[0]*(([2]-1)/[2])*(10**x)*log(10)*(1+([0]*(10**x))/[2])**(-[2])");
def fG2_SiPM_response(x, C, D, E):
    return C * D * ((E-1)/E) * (10**x) * np.log(10) * (1 + (D * (10**x)) / E)**(-E)    
# Combine the two functions
def SiPM_response(x, A, B, C, D, E):
    return fG1_SiPM_response(x, A, B) + fG2_SiPM_response(x, C, D, E)

def fit_SiPM_response(df,save:bool=True,debug:bool=False):
    n = df['Number'].iloc[0]
    label = df['Label'].iloc[0]
    ov = df['OV'].iloc[0]
    ch = df['Channel'].iloc[0]
    # Append new df to existing df and add n,label,ov and ch as new columns with the same length as the new df
    df['Frequency'] = 1/df['DeltaT']
    df['LogDeltaT'] = np.log10(df['DeltaT'])

    # Make a histogram of the frequency using np.histogram
    hist, bin_edges = np.histogram(df["LogDeltaT"], bins=200)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Fit the SiPM_response function to the histogram
    popt, pcov = curve_fit(SiPM_response, bin_centers, hist, p0=[1,1,1,1,1])
    perr = np.sqrt(np.diag(pcov))

    # Plot the histogram and the fit
    fig, ax = plt.subplots()
    ax.plot(bin_centers, hist, label='Data', drawstyle='steps-mid')
    ax.plot(bin_centers, SiPM_response(bin_centers, *popt), label='Fit')
    # Add error bands
    ax.fill_between(bin_centers, SiPM_response(bin_centers, *(popt + perr)), SiPM_response(bin_centers, *(popt - perr)), alpha=0.2)
    ax.plot(bin_centers, fG1_SiPM_response(bin_centers, *popt[:2]), label='Busrts',ls='--')
    ax.plot(bin_centers, fG2_SiPM_response(bin_centers, *popt[2:]), label='XTalk',ls='--')
    ax.set_xlabel('log10(DeltaT)')
    ax.set_ylabel('Counts')
    ax.legend()

    if save:
        try:
            os.mkdir(f'../images/{n}')
            os.mkdir(f'../data/{n}/{label}/')
            os.mkdir(f'../images/{n}/{label}')
        except FileExistsError:
            pass
        plt.savefig(f'../images/{n}/{label}/DC_data_fit_{ch}_{ov}.png', dpi=300)
        plt.close()
        with open(f'../data/{n}/{label}/DC_data_fit_{ch}_{ov}.csv', 'w') as file:
            file.write(f'N,Label,OV,Ch,XTalk,dXTalk,B,dB,Bursts,dBursts,D,dD,E,dE\n')
            file.write(f'{n},{label},{ov},{ch},{1/popt[0]},{perr[0]/popt[0]**2},{popt[1]},{perr[1]},{1/popt[2]},{perr[2]/popt[2]**2},{popt[3]},{perr[3]},{popt[4]},{perr[4]}\n')