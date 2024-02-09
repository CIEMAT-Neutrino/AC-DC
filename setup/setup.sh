# This script is used to setup the environment for the project.

# Make sure that you run this script from the root directory of the project by running the following command:
# $ source setup/setup.sh

# Print pwd to confirm that the script is running from the correct directory.
echo "The current working directory is: $(pwd)"
# Ask the user to confirm that the script is running from the correct directory.
echo "Is the current working directory the root directory of the project? (y/n)"
# Read the user's response.
read response
# If the user's response is not "y", then exit the script.
if [ "$response" != "y" ]; then
    echo "Please run the script from the root directory of the project."
    return
fi

# Create the necessary directories.
mkdir -p images
mkdir -p data

# Mount the data directory to the correct location.
directories=("data")

for dir in "${directories[@]}"; do
    if [ -L "$dir" ]; then
        echo "$dir symlink already exists"
    else
        echo "generating symlink for $dir..."
        sshfs ${USER}@gaeuidc1.ciemat.es:/pc/choozdsk01/palomare/ACDC/FBK_Preproduction "$dir"
    fi
done