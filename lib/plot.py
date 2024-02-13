import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

from itertools import product
from src.utils import get_project_root
root = get_project_root()

def make_cloud_plot(df,save:bool=True,debug:bool=False):
    numbers = df['Number'].unique()
    labels = df['Set'].unique()
    ovs = df['OV'].unique()
    chs = df['Channel'].unique()
    for n, label, ov, ch in product(numbers, labels, ovs, chs):
        data = df[(df['Number'] == n) & (df['Set'] == label) & (df['OV'] == ov) & (df['Channel'] == ch)]
        fig = plt.figure()
        plt.plot(data["DeltaT"],data["Amplitude"],'.',markersize=1)
        plt.semilogx()
        plt.xlim(1e-6,20)
        plt.ylim(0,0.1)
        plt.ylabel('Amplitude [mV]')
        plt.xlabel('$\Delta T$ [s]')
        if save: plt.savefig(f"{root}/images/{n}/{label}/{n}_{label}_DC_Amp_vs_DeltaT_{ov}_{ch}.png",dpi=300)
    
    return fig

def make_hist_plot(df,save:bool=True,debug:bool=False):
    numbers = df['Number'].unique()
    labels = df['Set'].unique()
    ovs = df['OV'].unique()
    chs = df['Channel'].unique()
    for n, label, ov, ch in product(numbers, labels, ovs, chs):
        data = df[(df['Number'] == n) & (df['Set'] == label) & (df['OV'] == ov) & (df['Channel'] == ch)]
        fig = plt.figure()
        bins=np.logspace(-6,1,100)
        plt.hist(data["DeltaT"],bins=bins,histtype='step',log=True);
        plt.semilogx()
        plt.ylabel('Amplitude [mV]')
        plt.xlabel('$\Delta T$ [s]')
        if save: plt.savefig(f"{root}/images/{n}/{label}/{n}_{label}_DC_DeltaT_hist_{ov}_{ch}.png",dpi=300)
    
    return fig