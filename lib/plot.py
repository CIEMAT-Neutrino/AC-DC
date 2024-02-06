import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def make_cloud_plot(df,ch,ov,save=True,debug=False):
    fig = plt.figure()
    plt.plot(df["DeltaT"],df["Amplitude"],'.',markersize=1)
    plt.semilogx()
    plt.xlim(1e-6,20)
    plt.ylim(0,0.1)
    plt.ylabel('Amplitude [mV]')
    plt.xlabel('$\Delta T$ [s]')
    if save: plt.savefig("../images/DC_Amp_vs_DeltaT_"+str(ov)+"_"+str(ch)+".png",dpi=300)
    return fig

# Make equivalent function ussing plotly
def make_cloud_plotly(df,ch,ov,save=True,debug=False):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["DeltaT"],y=df["Amplitude"],mode='markers',marker=dict(size=1)))
    fig.update_xaxes(type="log")
    fig.update_yaxes(range=[0,0.1])
    fig.update_layout(xaxis_title='$\Delta T$ [s]',yaxis_title='Amplitude [mV]')
    if save: fig.write_image("../images/DC_Amp_vs_DeltaT_"+str(ov)+"_"+str(ch)+".png")
    return fig

# plt.figure()
# bins=np.logspace(-6,1,100)
# plt.hist(DELTA_TIMES,bins=bins,histtype='step',log=True);
# plt.semilogx()
# plt.ylabel('Amplitude [mV]')
# plt.xlabel('$\Delta T$ [s]')
# plt.savefig(plot_path+"DC_DeltaT_hist_"+str(args.OV)+"_"+str(args.ch)+".png",dpi=300)
# print("Saved plot in "+plot_path)