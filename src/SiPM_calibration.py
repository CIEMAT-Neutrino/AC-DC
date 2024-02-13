import sys; sys.path.insert(0, '../'); from lib import *
from src.utils import get_project_root

root = get_project_root()
rprint("--------------------")

parser = argparse.ArgumentParser(description="Purpose: Small program designed to read the SPE files and get the gain of each, adapted for Antonio Verdugo's data taking of FBK SiPMs with an oscilloscope. \n Designer: Rodrigo Alvarez Garrote")    
parser.add_argument('--OV', type=int, default=7,
                    help='Overvoltage')
parser.add_argument('--path', type=str, default=f'{root}/data/',
                    help='Folder containing all the data')
parser.add_argument('--N', type=int, default=225,
                    help='Set number')
parser.add_argument('--set', type=str, default="SET1",
                    help='subset of the data')
parser.add_argument('--ch', type=int, default=2,
                    help='channel of the board')
parser.add_argument('--debug', type=bool,default=False,
                    help='debug mode')
args = parser.parse_args()

debug =args.debug

le_path=args.path+str(args.N)+"/"+args.set+"/SPE/C"+str(args.ch)+"--OV"+str(args.OV)+"**"
file_list = load_files(le_path)

ADCs, period= SPE_get_ADCs_file_list(file_list)
charge= np.sum(ADCs[:,200:],axis=1)

# Select percentile of the charge
percentile = [1,99]
r = np.percentile(charge,percentile)
this_charge = charge[(charge>r[0]) & (charge<r[1])]

counts,bins,_ = plt.hist(this_charge ,bins=250,range=r,histtype='step',label="Calibration data");
peaks=find_peaks(counts,height=50,width=3,distance=6)

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
    
vars,fit_y,qs=fit_gaussians(bins[:-1][l_lim:r_lim],counts[l_lim:r_lim],params)
plt.plot(bins[:-1][l_lim:r_lim] +(bins[1]-bins[0])/2  ,fit_y,'--',color="red",label="Fit")
plt.legend()
plt.xlabel("Charge [ADCxticks]")
plt.ylabel("Counts")
x = bins[:-1][l_lim:r_lim] + (bins[1] - bins[0]) / 2

plt.ylim(0.5,counts[peaks[0]][0]*1.2)
plt.legend(frameon=True,fontsize=14)

plot_path=f"{root}/data/images/{str(args.N)}/{args.set}/"
os.system("mkdir -p "+plot_path)
plt.savefig(f"{plot_path}DC_data_calibration_{str(args.OV)}_{str(args.ch)}.png",dpi=300)
plt.semilogy()
plt.savefig(f"{plot_path}DC_data_calibration_logy_{str(args.OV)}_{str(args.ch)}.png",dpi=300)

gain_ADCs_x_ticks     = np.mean(vars[1::3][1:]-vars[1::3][:-1])
gain_ADCs_x_ticks_std = np.std (vars[1::3][1:]-vars[1::3][:-1])
error_relative=gain_ADCs_x_ticks/gain_ADCs_x_ticks_std


file_path=f"{root}/data/{str(args.N)}/{args.set}/"
os.system("mkdir -p "+file_path)
filename=f"{file_path}DC_data_calibration_{str(args.OV)}_{str(args.ch)}.csv"

df = pd.DataFrame({"Number":[], "Set":[], 'OV':[], "Channel":[], 'Gain': [], "Error":[], "Relative":[]})
new_row = {"Number":args.N,"Set":args.set,'OV':args.OV,"Channel":args.ch,'Gain': gain_ADCs_x_ticks, 'Error': gain_ADCs_x_ticks_std, 'Relative': error_relative}

df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
df.to_csv(filename, index=False)
os.chmod(filename, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
rprint(f"Data saved in {filename}")