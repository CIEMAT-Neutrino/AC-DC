import sys
sys.path.insert(0, '../')
from lib import *

# Define the args to be called in the parser
parser = argparse.ArgumentParser(description="Program designed to read the txt data files from the oscilloscope.")
parser.add_argument('-n', type=list, default=["225"],
                    help='Sensor number')
parser.add_argument('-set', type=list, default=["SET1"],
                    help='Subset of the data')
parser.add_argument('-OV', type=list, default=[7],
                    help='Overvoltage') 
parser.add_argument('-ch', type=list, default=[2], 
                    help='Channel of the setup/board')
parser.add_argument('-debug', type=bool, default=True,
                    help='Debug mode, if True prints the debug information')
args = parser.parse_args()

for n, label, ch, ov in product(args.n, args.set, args.ch, args.OV):
    os.system(f"python3 run_DC_fit_analysis.py --n {n} --set {label} --OV {ov} --ch {ch} --polarity -1 --debug True")
