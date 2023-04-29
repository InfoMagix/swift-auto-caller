#!/bin/bash

#configures a new SD card that already has the raspberry pi o/s installed on it
# This assumes a 'lite' version of that o/s has been used otherwsie some packages may already be availabel (eg git)

# Update packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Git, pip, venv, and VLC
sudo apt-get install -y git python3-pip python3-venv vlc python3-vlc

# Clone the repository
git clone https://github.com/InfoMagix/swift-auto-caller.git

# Navigate to the swift-auto-caller directory
cd swift-auto-caller

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install Python packages
pip install schedule python-vlc Flask

# Make the run.sh script executable
chmod +x run.sh

# Modify rc.local to start the script at boot
sudo sed -i 's|^exit 0|cd /home/pi/swift-auto-caller \&\& ./run.sh \&\n\nexit 0|' /etc/rc.local

# Install the audio DAC
# Note that this is taken off the vendor's website and might change, 
# refer to https://shop.pimoroni.com/products/audio-dac-shim-line-out
 
git clone https://github.com/pimoroni/pirate-audio
cd pirate-audio/mopidy
sudo ./install.sh

echo "Installation completed. Please reboot your Raspberry Pi."
