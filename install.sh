#!/bin/bash

set -e

echo "Starting installation for Itch Automation App..."

echo "Installing prerequisities"
sudo apt-get update

AUTOMATION_LOCATION="$HOME/.itch_automation"
BIN_LOCATION="$HOME/.local/bin"
echo "Creating installation directory at $AUTOMATION_LOCATION and bin directory if not already created at $BIN_LOCATION..."
mkdir -p "$AUTOMATION_LOCATION"
mkdir -p "$BIN_LOCATION"
cd "$AUTOMATION_LOCATION"

curl -sSL -o "uploader.py" "https://raw.githubusercontent.com/SherryNinja10/itch-upload-automation/refs/heads/main/uploader.py"
curl -sSL -o "requirements.txt" "https://raw.githubusercontent.com/SherryNinja10/itch-upload-automation/refs/heads/main/requirements.txt"

export PIP_NO_INDEX=false

echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
deactivate

echo "Installing butler cli and adding it to the path..."
curl -L -o butler.zip https://broth.itch.zone/butler/linux-amd64/LATEST/archive/default
unzip -o butler.zip -d "$BIN_LOCATION"
chmod +x "$BIN_LOCATION/butler"
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc

echo "Creating alias and inputting into ~/.bashrc"
echo 'alias itch_uploader="source ~/.itch_automation/venv/bin/activate && python3 ~/.itch_automation/uploader.py && deactivate"' >> $HOME/.bashrc

source $HOME/.bashrc

echo "Install complete. To use the script run the following in a folder containing the godot projects you want to export and upload to itch: itch_uploader"
