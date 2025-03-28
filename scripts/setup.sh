# Make sure that you run this script from the root directory of the project by running the following command:
# $ source setup/setup.sh

# Ask the user to confirm that the script is running from the correct directory.
echo "Is the current working directory $(pwd) the root directory of the project? (y/n)"
read response
# If the user's response is not "y", then exit the script.
if [ "$response" != "y" ]; then
    echo "Please run the script from the root directory of the project."
    return
fi

# Try to unmount the data directory
if [ -d "data" ]; then
    echo "unmounting data directory..."
    unlink data
fi

# Mount the data directory to the correct location.
directories=("data")

for dir in "${directories[@]}"; do
    if [ -L "$dir" ]; then
        echo "$dir symlink already exists"
    else
        echo "generating symlink for $dir..."
        ln -s /pc/choozdsk01/DATA/AC-DC/TUTORIAL "$dir"
    fi
done

mkdir -p analysis
mkdir -p images
