#!/bin/bash
set -e

echo "============================================="
echo " MiroFish OS - WSL2 Hardware Tuning Script"
echo "============================================="

echo "[*] Updating package list..."
sudo apt-update || echo "Requires sudo privileges."

echo "[*] Installing native dependencies for audio and browser engines..."
sudo apt-get install -y ffmpeg libsm6 libxext6 || echo "Failed to install ffmpeg. Please install manually."

echo "[*] Installing Python dependencies..."
pip install -r ../requirements.txt

echo "[*] Installing Playwright system dependencies..."
playwright install --with-deps chromium

echo "[*] Optimizing WSL2 memory limits (sysctl)..."
# In a real setup, we would append to /etc/wsl.conf or .wslconfig on the Windows side.
echo "Note: To strictly enforce the 16GB RAM limit, ensure your .wslconfig in Windows has 'memory=16GB'."

echo "[*] Setup Complete. Ready to boot MiroFish OS."
