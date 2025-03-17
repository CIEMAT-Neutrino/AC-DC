import sys
sys.path.insert(0, '../')
from lib import *

rprint("--------------------")

parser = argparse.ArgumentParser(description="Program designed to read the txt data files from the oscilloscope.")    
parser.add_argument('--path', '-p', type=str, default=f'{root}/analysis',
                    help='Folder containing all the data')
parser.add_argument('--output', '-o', type=str, default=f'{root}/images',
                    help='Folder containing all the output data')
parser.add_argument('--n', type=str, default="225",
                    help='Sensor number')
parser.add_argument('--set', type=str, default="SET1",
                    help='Subset of the data')
parser.add_argument('--OV', type=int, default=7,
                    help='Overvoltage')
parser.add_argument('--channel', '-ch', type=int, default=2,
                    help='Channel of the setup/board')
parser.add_argument('--debug', '-d', type=bool,default=True,
                    help='Debug mode, if True prints the debug information')
args = parser.parse_args()

this_file = f'{args.path}/{args.n}/{args.set}/{args.n}_{args.set}_DC_data_{args.OV}_{args.channel}.csv'
try:
    df = pd.read_csv(this_file)
    df["Number"] = args.n
    df["Set"] = args.set
    df["OV"] = args.OV
    df["Channel"] = args.channel
    fit_SiPM_response(df, filter_data=False, save=True, debug=args.debug)

except FileNotFoundError:
    rprint(f'File not found: {this_file}')
    pass