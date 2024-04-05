import sys; sys.path.insert(0, '../'); from lib import *

for n, label, ch, ov in product(["375_0","375_1"],["CT","RT"],[0],[3,4,5]):
    # os.system(f"python3 SiPM_DC.py --n {n} --set {label} --OV {ov} --ch {ch} --polarity -1 --debug True")
    os.system(f"python3 SiPM_calibration.py --n {n} --set {label} --OV {ov} --ch {ch} --polarity -1 --debug True")