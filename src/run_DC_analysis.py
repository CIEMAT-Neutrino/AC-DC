import sys
sys.path.insert(0, '../')
from lib import *

rprint("--------------------")

parser = argparse.ArgumentParser(description="Program designed to read the txt data files from the oscilloscope.")    
parser.add_argument('--path', '-p', type=str, default=f'{root}/data',
                    help='Folder containing all the data')
parser.add_argument('--output', '-o', type=str, default=f'{root}/analysis',
                    help='Folder containing all the output data')
parser.add_argument('--n', type=str, default="225",
                    help='Sensor number')
parser.add_argument('--set', type=str, default="SET1",
                    help='Subset of the data')
parser.add_argument('--OV', type=int, default=7,
                    help='Overvoltage')
parser.add_argument('--channel', '-ch', type=int, default=2,
                    help='Channel of the setup/board')
parser.add_argument('--polarity', type=int, default=1,
                    help='Polarity of the signal, -1 for negative, 1 for positive')
parser.add_argument('--threshold', type=float, default=0.0,
                    help='Threshold for the peak finding')
parser.add_argument('--height', type=float, default=0.01,
                    help='Height for the peak finding')
parser.add_argument('--distance', type=int, default=40,
                    help='Min distance between peaks')
parser.add_argument('--width', type=int, default=20,
                    help='Width of the peak')
parser.add_argument('--debug', '-d', type=bool,default=True,
                    help='Debug mode, if True prints the debug information')
args = parser.parse_args()
debug = args.debug

if debug: rprint(args)
file_list = load_files(f'{args.path}/{args.n}/{args.set}/DC/C{args.channel}--OV{args.OV}**')
if file_list is None:
    rprint("No files found, exiting...")
    exit()

delta_times = []
peak_values = []
for f_path in track(file_list, description="Processing WVFs"): # type: ignore
    # if debug: rprint(f"Processing {f_path}...")
    times, _, peak_times, peak_amps, = process_file(f_path, polarity=args.polarity, width=args.width, threshold=args.threshold, height=args.height, distance=args.distance, debug=debug)
    times=(ak.Array(peak_times)+ak.Array(times))
    times=ak.flatten(times)
    times_aux =times[1:]-times[:-1]
    peak_amps=ak.flatten(ak.Array(peak_amps)) 
    peak_amps=peak_amps[1:]
    delta_times.append(times_aux)
    peak_values.append(peak_amps)

# Flatten the lists and convert to numpy arrays
delta_times = np.array(ak.flatten(ak.Array(delta_times)))
peak_values = np.array(ak.flatten(ak.Array(peak_values)))
rprint(f"Found {len(delta_times)} delta times")
rprint(f"Found {len(peak_values)} peak values")

# Save the data for later fits, avoid reprocessing
data={'DeltaT':delta_times,'Amplitude':peak_values}
df=pd.DataFrame(data=data)
df['Number'] = args.n
df['Set'] = args.set
df['OV'] = args.OV
df['Channel'] = args.channel
df = classify_df(df, ow=True, debug=debug)
df = fit_SiPM_response(df, filter_data=False, save=True, debug=debug)

data_path=f"{args.output}/{str(args.n)}/{args.set}/"
os.system("mkdir -p "+data_path)
file_name=f"{data_path}/{args.n}_{args.set}_DC_data_{str(args.OV)}_{str(args.channel)}.csv"
df.to_csv(file_name, index=False)
os.chmod(file_name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
rprint(f"Data saved in {file_name}")