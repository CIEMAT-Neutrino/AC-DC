import sys
sys.path.insert(0, '../')
from lib import *

for n, label, ch, ov in product(["486"],["SET1"],[0],[3]):
    os.system(f"python3 run_DC_analysis.py --n {n} --set {label} --OV {ov} --ch {ch} --polarity -1 --debug True")
    # os.system(f"python3 SiPM_calibration.py --n {n} --set {label} --OV {ov} --ch {ch} --polarity -1 --debug True")