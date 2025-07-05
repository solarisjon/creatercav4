#!/usr/bin/env bash

# Deployment script for MCP-based Root Cause Analysis Tool on Ubuntu in /var/www

set -e

# 1. Install system dependencies
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# 2. Clone or update the repository
if [ ! -d /var/www/creatercav4 ]; then
    sudo git clone https://github.com/solarisjon/creatercav4.git /var/www/creatercav4
    sudo chown -R $USER:$USER /var/www/creatercav4
else
    cd /var/www/creatercav4
    git pull
fi

cd /var/www/creatercav4

# 3. Set up Python virtual environment
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# 4. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Copy and configure config.ini if needed
if [ ! -f config.ini ]; then
    cp config.ini.example config.ini
    echo "Please edit /var/www/creatercav4/config.ini with your API keys and settings."
fi

# 6. Create required directories
mkdir -p uploads output logs

# 7. (Optional) Set permissions for uploads/output/logs
chmod 770 uploads output logs

# 8. Start the application (use tmux or systemd for production)
echo "To run the app in the foreground:"
echo "cd /var/www/creatercav4 && source .venv/bin/activate && python3 main.py"
echo "Or set up a systemd service for production use."
