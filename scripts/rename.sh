# Small script to rename files in a directory. The current names are OV4--xxxxx.txt and the new names are C0--OV4--xxxxx.txt
# Usage: ./rename.sh number

# Create a variable number to be inputted by the user
NUMBER=$1
OV=$2
INPATH="/pc/choozdsk01/palomare/ACDC/COLD_FINGER/${NUMBER}/RT/SPE"
OUTPATH="/pc/choozdsk01/palomare/ACDC/COLD_FINGER/${NUMBER}/RT/SPE"

for file in $INPATH/OV${OV}--*.txt; do
    mv "$file" "$OUTPATH/C0--$(basename $file)"
    echo "Renaming ${file}"
done