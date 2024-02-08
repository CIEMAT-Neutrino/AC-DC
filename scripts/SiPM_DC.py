print("--------------------")
import sys; sys.path.insert(0, '../'); from lib import *

parser = argparse.ArgumentParser(description="Purpose: Small program designed to read the SPE files and get the gain of each, adapted for Antonio Verdugo's data taking of FBK SiPMs with an oscilloscope. \n Designer: Rodrigo Alvarez Garrote")    
parser.add_argument('--OV', type=int, default=7,
                    help='Overvoltage')
parser.add_argument('--path', type=str, default="/pc/choozdsk01/palomare/ACDC/FBK_Preproduction/",
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

le_path=args.path+str(args.N)+"/"+args.set+"/DC/C"+str(args.ch)+"--OV"+str(args.OV)+"**"

file_list = glob.glob(le_path)
print('Reading files in :'+le_path+'...')
print('Found {} files'.format(len(file_list)))
if len(file_list)==0:
    print("No files found, exiting...")
    exit()
print('First 3 files names:')
print(file_list[:3])

file1_path = file_list[0]
HEADER=3
N_SEGMENTs=50
PRETRIGGER=5e-6 #in s

if debug:
    times, ADCs,period=DC_read_file(file1_path)
    peaks,  peak_values, smoothed_ADCs = smooth_and_find_peaks(ADCs,period=period)
    plt.hist(np.max(smoothed_ADCs,axis=1),bins=100);

    plt.figure()
    for i in range(10):
        plt.plot(np.arange(len(smoothed_ADCs[i]))*period,smoothed_ADCs[i])
        plt.plot(peaks[i], peak_values[i], "x")

DELTA_TIMES = []
PEAK_VALUES = []
for f_path in file_list:
    print(f"Processing {f_path}...")
    times, peak_times, peak_values, = DC_process_file(f_path);
    times=(ak.Array(peak_times)+ak.Array(times))
    times=ak.flatten(times)
    times_aux =times[1:]-times[:-1]
    peak_values=ak.flatten(ak.Array(peak_values)) 
    peak_values=peak_values[1:]
    DELTA_TIMES.append(times_aux)
    PEAK_VALUES.append(peak_values)

#finally flatten
DELTA_TIMES = np.array(ak.flatten(ak.Array(DELTA_TIMES)))
PEAK_VALUES = np.array(ak.flatten(ak.Array(PEAK_VALUES)))

#save the data for later fits, avoid reprocessing
data={'DeltaT':DELTA_TIMES,'Amplitude':PEAK_VALUES}
df=pd.DataFrame(data=data)
data_path="../data/"+str(args.N)+"/"+args.set+"/"
print("Saving data in "+data_path)
os.system("mkdir -p "+data_path)
file_name=data_path+"DC_data_"+str(args.OV)+"_"+str(args.ch)+".csv"
df.to_csv(file_name,index=False)
os.chmod(file_name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
print("Done!")