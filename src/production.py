import sys; sys.path.insert(0, '../'); from lib import *

for n, label, ch, ov in product([289,290,377,378,486,487,488,490],["SET1"],[0],[4]):
    os.system("python3 SiPM_DC.py --OV "+str(ov)+" --set "+label +" --ch "+str(ch)+" --N "+str(n)+" --debug True")
    # os.system("python3 SiPM_calibration.py --OV "+str(ov)+" --set "+label +" --ch "+str(ch)+" --N "+str(n)+" --debug True")