import sys; sys.path.insert(0, '../'); from lib import *

for n, label, ch, ov in product([225],["SET1"],[2],[35,45,7]):
    os.system("python3 SiPM_DC.py --OV "+str(ov)+" --set "+label +" --ch "+str(ch)+" --N "+str(n)+" --debug True")
