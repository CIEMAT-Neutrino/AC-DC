import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

def make_cloud_plot(df,ch:int,ov:int,save:bool=True,debug:bool=False):
    fig = plt.figure()
    plt.plot(df["DeltaT"],df["Amplitude"],'.',markersize=1)
    plt.semilogx()
    plt.xlim(1e-6,20)
    plt.ylim(0,0.1)
    plt.ylabel('Amplitude [mV]')
    plt.xlabel('$\Delta T$ [s]')
    if save: plt.savefig("../images/DC_Amp_vs_DeltaT_"+str(ov)+"_"+str(ch)+".png",dpi=300)
    return fig

def make_hist_plot(df,ch:int,ov:int,save:bool=True,debug:bool=False):
    fig = plt.figure()
    bins=np.logspace(-6,1,100)
    plt.hist(df["DeltaT"],bins=bins,histtype='step',log=True);
    plt.semilogx()
    plt.ylabel('Amplitude [mV]')
    plt.xlabel('$\Delta T$ [s]')
    if save: plt.savefig("../images/DC_DeltaT_hist_"+str(ov)+"_"+str(ch)+".png",dpi=300)
    return fig