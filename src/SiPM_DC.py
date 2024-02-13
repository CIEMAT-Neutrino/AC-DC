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
parser.add_argument('--debug', type=bool,default=True,
                    help='debug mode')
args = parser.parse_args()

debug =args.debug

le_path=args.path+str(args.N)+"/"+args.set+"/DC/C"+str(args.ch)+"--OV"+str(args.OV)+"**"
file_list = load_files(le_path)

DELTA_TIMES = []
PEAK_VALUES = []
for f_path in track(file_list, description="Processing WVFs"):
    if debug: rprint(f"Processing {f_path}...")
    times, peak_times, peak_values, = DC_process_file(f_path);
    times=(ak.Array(peak_times)+ak.Array(times))
    times=ak.flatten(times)
    times_aux =times[1:]-times[:-1]
    peak_values=ak.flatten(ak.Array(peak_values)) 
    peak_values=peak_values[1:]
    DELTA_TIMES.append(times_aux)
    PEAK_VALUES.append(peak_values)

# Flatten
DELTA_TIMES = np.array(ak.flatten(ak.Array(DELTA_TIMES)))
PEAK_VALUES = np.array(ak.flatten(ak.Array(PEAK_VALUES)))

# Save the data for later fits, avoid reprocessing
data={'DeltaT':DELTA_TIMES,'Amplitude':PEAK_VALUES}
df=pd.DataFrame(data=data)
df['Number'] = args.N
df['Set'] = args.set
df['OV'] = args.OV
df['Channel'] = args.ch
df = classify_df(df, ow=True, debug=debug)
fit_SiPM_response(df, filter_data=False, save=True, debug=debug)
data_path=f"{root}/data/{str(args.N)}/{args.set}/"
os.system("mkdir -p "+data_path)
file_name=f"{data_path}DC_data_{str(args.OV)}_{str(args.ch)}.csv"
df.to_csv(file_name,index=False)
os.chmod(file_name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
rprint(f"Data saved in {file_name}")