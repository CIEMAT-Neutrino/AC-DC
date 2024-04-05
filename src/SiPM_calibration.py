import sys

from numpy import mean; sys.path.insert(0, '../'); from lib import *
from src.utils import get_project_root

root = get_project_root()
rprint("--------------------")

parser = argparse.ArgumentParser(description="Program designed to read the txt data files from the oscilloscope.")    
parser.add_argument('--path', type=str, default=f'{root}/data/',
                    help='Folder containing all the data')
parser.add_argument('--n', type=str, default="375_0",
                    help='Sensor number')
parser.add_argument('--set', type=str, default="CT",
                    help='Subset of the data')
parser.add_argument('--OV', type=int, default=5,
                    help='Overvoltage')
parser.add_argument('--ch', type=int, default=0,
                    help='Channel of the setup/board')
parser.add_argument('--polarity', type=int, default=-1,
                    help='Polarity of the signal, -1 for negative, 1 for positive')
parser.add_argument('--threshold', type=float, default=0.001,
                    help='Threshold for the peak finding')
parser.add_argument('--width', type=int, default=3,
                    help='Width of the peak')
parser.add_argument('--debug', type=bool,default=True,
                    help='Debug mode, if True prints the debug information')
args = parser.parse_args()
debug = args.debug
plot_path=f"{root}/data/images/{args.n}/{args.set}/"
os.system("mkdir -p "+plot_path)

if debug: rprint(args)
file_list = load_files(f'{args.path}{args.n}/{args.set}/SPE/C{args.ch}--OV{args.OV}**')
if file_list is None:
    rprint("No files found, exiting...")
    exit()

ADCs = merge_processed_files(file_list, data="SPE", width=args.width, threshold=args.threshold, polarity=args.polarity, header=5, segments=0, debug=debug)
charge = np.sum(ADCs[:,50:150],axis=1)

# Select percentile of the charge
percentile = [1,99]
r = np.percentile(charge,percentile)
this_charge = charge[(charge>r[0]) & (charge<r[1])]

counts,bins,_ = plt.hist(this_charge ,bins=250,range=r,histtype='step',label="Calibration data");
plt.xlabel("Charge [ADCxticks]")
plt.ylabel("Counts")
plt.legend()
plt.savefig(f"{plot_path}{args.n}_{args.set}DC_data_calibration_raw_{args.OV}_{args.ch}.png",dpi=300)
peaks = signal.find_peaks(counts, height=50, width=3, distance=6)

plt.plot(bins[peaks[0]], counts[peaks[0]], "x")
r_lim=peaks[0][-1]+ int (((peaks[0][-1]-peaks[0][-2]))/2)
l_lim=peaks[0][0]- int (((peaks[0][1]-peaks[0][0]))/2)-2
if l_lim<0:
    l_lim=0
std=(bins[peaks[0]][1]-bins[peaks[0]][0])/4

params = np.zeros(len(peaks[0])*3)
params[0::3] = peaks[1]["peak_heights"]
params[1::3] = bins[peaks[0]]
params[2::3] = std
    
popt, perr, fit_y, qs = fit_gaussians(bins[:-1][l_lim:r_lim],counts[l_lim:r_lim],params)
plt.plot(bins[:-1][l_lim:r_lim] +(bins[1]-bins[0])/2  ,fit_y,'--',color="red",label="Fit")
plt.legend()
x = bins[:-1][l_lim:r_lim] + (bins[1] - bins[0]) / 2

plt.ylim(0.5,counts[peaks[0]][0]*1.2)
plt.legend(frameon=True,fontsize=14)

plt.savefig(f"{plot_path}{args.n}_{args.set}_SPE_data_calibration_{args.OV}_{args.ch}.png",dpi=300)
plt.semilogy()
plt.savefig(f"{plot_path}{args.n}_{args.set}_SPE_data_calibration_logy_{args.OV}_{args.ch}.png",dpi=300)

file_path=f"{root}/data/analysis/{args.n}/{args.set}/"
os.system("mkdir -p "+file_path)
filename=f"{file_path}{args.n}_{args.set}_SPE_data_calibration_{args.OV}_{args.ch}.csv"
df = pd.DataFrame({'Peak': [], 'Mu': [], "dMu":[], 'Sigma': [], "dSigma":[], 'Gain': [], "dGain":[]})

mu = popt[1::3]; dmu = perr[1::3]
gain = popt[1::3][1:]-popt[1::3][:-1]; dgain = perr[1::3][1:]-perr[1::3][:-1]
width = popt[2::3]; dwidth = perr[2::3]
for i in (range(len(mu))):
    try:
        new_row = {'Peak': i, 'Mu': mu[i], 'dMu': dmu[i], 'Sigma': width[i], 'dSigma': dwidth[i], 'Gain': gain[i], 'dGain': dgain[i]}
    except:
        new_row = {'Peak': i, 'Mu': mu[i], 'dMu': dmu[i], 'Sigma': width[i], 'dSigma': dwidth[i], 'Gain': -99, 'dGain': -99}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
df.to_csv(filename, index=False)
os.chmod(filename, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
rprint(f"Data saved in {filename}")

mean_mu = np.mean(mu)
std_mu = np.std (mu) 
mean_gain = np.mean(gain)
std_gain = np.std (gain)
mean_width = np.mean(width)
std_width = np.std (width)

filename=f"{file_path}{args.n}_{args.set}_SPE_data_calibration_summary_{args.OV}_{args.ch}.csv"
df = pd.DataFrame({"Number":[], "Set":[], 'OV':[], "Channel":[], 'Gain': [], "dGain":[], "Relative":[]})
new_row = {"Number":args.n,"Set":args.set,'OV':args.OV,"Channel":args.ch,'Gain': mean_gain, 'Error': std_gain, 'Relative': mean_gain/std_gain}

df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
df.to_csv(filename, index=False)
os.chmod(filename, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
rprint(f"Data saved in {filename}")