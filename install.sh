#!/bin/bash

set -e

echo "Starting installation for Itch Automation App..."

echo "Installing prerequisities"
sudo apt-get update

AUTOMATION_LOCATION="~/.itch_automation"
BIN_LOCATION="~/.local/bin"
echo "Creating installation directory at $AUTOMATION_LOCATION and bin directory if not already created at $BIN_LOCATION..."
mkdir -p "$AUTOMATION_LOCATION"
cd "$AUTOMATION_LOCATION"

curl -sSL -o "https://raw.githubusercontent.com/SherryNinja10/itch-upload-automation/refs/heads/main/uploader.py"
curl -sSL -o "https://raw.githubusercontent.com/SherryNinja10/itch-upload-automation/refs/heads/main/requirements.txt"

echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "Installing butler cli and adding it to the path..."
curl -L -o butler.zip https://broth.itch.ovh/butler/linux-amd64/LATEST/archive/default
unzip butler.zip -d ~/.local/bin
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc

echo "Creating alias and inputting into ~/.bashrc"
echo 'alias itch_uploader="source ~/.itch_automation/venv/bin/activate && python3 ~/.itch_automation/uploader.py && deactivate"' >> ~/.bashrc

echo "Install complete. To use the script run the following in a folder containing the godot projects you want to export and upload to itch: itch_uploader"
