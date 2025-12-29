#!/usr/bin/env bash
set -o errexit

chmod +x render-build.sh
pip install -r requirements.txt

echo "Downloading Chrome..."
wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

dpkg -x ./google-chrome-stable_current_amd64.deb ./chrome
rm ./google-chrome-stable_current_amd64.deb

echo "Chrome installed successfully"