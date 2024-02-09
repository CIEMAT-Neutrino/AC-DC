# Follow the structure of the wFit_SiPM.C macro to create a python function that fits the SiPM response
import os
import json
import warnings
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
# suppress warnings 
warnings.filterwarnings('ignore') 

# TF1* fG1 = new TF1("fG1","[1]*[0]*log(10)*(10**x)*exp(-[0]*(10**x))");
def dark_current_SiPM(x, A, B):
    return A * np.log(10) * (10**x) * np.exp(-B * (10**x))
# TF1* fG2 = new TF1("fG2","[1]*[2]*(([2]-1)/[2])*(10**x)*log(10)*(1+([0]*(10**x))/[2])**(-[2])");
def bursts_SiPM(x, C, D, E):
    return D * ((E-1)/E) * (10**x) * np.log(10) * (1 + (C * (10**x)) / E)**(-E)    
# Combine the two functions
def SiPM_response(x, A, B, C, D, E):
    return dark_current_SiPM(x, A, B) + bursts_SiPM(x, C, D, E)

def fit_SiPM_response(df,save:bool=True,debug:bool=False):
    n = df['Number'].iloc[0]
    label = df['Label'].iloc[0]
    ov = df['OV'].iloc[0]
    ch = df['Channel'].iloc[0]
    # Append new df to existing df and add n,label,ov and ch as new columns with the same length as the new df
    df['Frequency'] = 1/df['DeltaT']
    df['LogDeltaT'] = np.log10(df['DeltaT'])

    # Make a histogram of the frequency using np.histogram
    with open('../data/analysis/SPE.json') as json_file:
        SPE_data = json.load(json_file)
    
    amp_lim = SPE_data[str(n)][label]["OV"][str(ov)]
    hist, bin_edges = np.histogram(df[df["Amplitude"] < amp_lim]["LogDeltaT"], bins=200)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Fit the SiPM_response function to the histogram
    try:
        popt, pcov = curve_fit(SiPM_response, bin_centers, hist, p0=[1e2,1,1e2,1e4,2], bounds=([0,0,0,0,0],[1e3,10,1e3,1e6,10]))
    except RuntimeError:
        print(f'Fit failed for {n} {label} OV{ov} Ch{ch}')
        return
    
    perr = np.sqrt(np.diag(pcov))

    # Plot the histogram and the fit
    fig, ax = plt.subplots()
    ax.plot(bin_centers, hist, label='Data', drawstyle='steps-mid')
    ax.plot(bin_centers, SiPM_response(bin_centers, *popt), label='Fit')
    # Add error bands
    # ax.fill_between(bin_centers, SiPM_response(bin_centers, *(popt + perr)), SiPM_response(bin_centers, *(popt - perr)), alpha=0.2)
    ax.plot(bin_centers, dark_current_SiPM(bin_centers, *popt[:2]), label='DarkCurrent',ls='--')
    ax.plot(bin_centers, bursts_SiPM(bin_centers, *popt[2:]), label='Bursts',ls='--')
    ax.set_title(f'SiPM response fit for {n} {label} OV{ov} Ch{ch}')
    ax.set_xlabel('log10(DeltaT)')
    ax.set_ylabel('Counts')
    ax.legend()

    if save:
        plt.savefig(f'../images/{n}/{label}/DC_data_fit_{ov}_{ch}.png', dpi=300)
        plt.close()
        with open(f'../data/{n}/{label}/DC_data_fit_{ov}_{ch}.csv', 'w') as file:
            file.write(f'Number,Set,OV,Channel,A,dA,DarkCurrent,dDarkCurrent,Bursts,dBursts,D,dD,E,dE\n')
            file.write(f'{n},{label},{ov},{ch},{popt[0]},{perr[0]},{popt[1]},{perr[1]},{popt[2]},{perr[2]},{popt[3]},{perr[3]},{popt[4]},{perr[4]}\n')
        file.close()

def gauss(x,a,x0,sigma):
    return a*np.exp(-0.5*np.power((x-x0)/sigma,2))

def gaussian_train(x, *params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        height = params[i]
        center = params[i+1]
        width  = params[i+2]
        y      +=  gauss(x, height, center, width)
    return y

def fit_gaussians(x, y, *p0):
    assert x.shape == y.shape, "Input arrays must have the same shape."
    # try:
    popt, pcov = curve_fit(gaussian_train, x,y, p0=p0[0])
    fit_y=gaussian_train(x,*popt)
    chi_squared = np.sum((y[abs(fit_y)>0.1] - fit_y[abs(fit_y)>0.1]) ** 2 / fit_y[abs(fit_y)>0.1]) / (y.size - len(popt))
    # plt.figure(dpi=200, figsize=(6, 3))
    # fig = plt.axes()
    # plt.plot(x, y, 'b-', label='data')
    # plt.plot(x, fit_y, 'r-', label='fit',linewidth=1)
    # plt.grid()
    return popt,fit_y, chi_squared
    # except:
    #     print("Fit failed.")
    
def Q_out(V_out,period):
    #   V_out in Volts
    #          osc resistance    x  t
    q=V_out  /      50          *   period
    return q