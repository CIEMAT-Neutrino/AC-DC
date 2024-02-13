import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

from src.utils import get_project_root
root = get_project_root()

def make_cloud_plot(df,ch:int,ov:int,save:bool=True,debug:bool=False):
    fig = plt.figure()
    plt.plot(df["DeltaT"],df["Amplitude"],'.',markersize=1)
    plt.semilogx()
    plt.xlim(1e-6,20)
    plt.ylim(0,0.1)
    plt.ylabel('Amplitude [mV]')
    plt.xlabel('$\Delta T$ [s]')
    if save: plt.savefig(f"{root}/images/DC_Amp_vs_DeltaT_{ov}_{ch}.png",dpi=300)
    return fig

def make_hist_plot(df,ch:int,ov:int,save:bool=True,debug:bool=False):
    fig = plt.figure()
    bins=np.logspace(-6,1,100)
    plt.hist(df["DeltaT"],bins=bins,histtype='step',log=True);
    plt.semilogx()
    plt.ylabel('Amplitude [mV]')
    plt.xlabel('$\Delta T$ [s]')
    if save: plt.savefig(f"{root}/images/DC_DeltaT_hist_{ov}_{ch}.png",dpi=300)
    return fig