#!/bin/bash

# Fix Pandas Compilation Issue on PythonAnywhere
# This script will help resolve the pandas compilation error

echo "🔧 Fixing pandas compilation issue..."

# Navigate to project directory
cd ~/importing_project

echo "📋 Current Python version:"
python3 --version

echo "📋 Current pip version:"
pip3 --version

echo "🧹 Cleaning up any existing pandas installation..."
pip3 uninstall -y pandas numpy

echo "📦 Installing numpy first (required for pandas)..."
pip3 install --user numpy==1.24.3

echo "📦 Installing pandas with binary wheels..."
pip3 install --user --only-binary=all pandas==1.4.4

echo "📦 Installing other dependencies..."
pip3 install --user Flask==2.2.5 openpyxl==3.0.10 xlrd==2.0.1 python-dotenv==0.21.1 Flask-WTF==1.0.1 Werkzeug==2.2.3 requests==2.28.2

echo "✅ Installation completed!"
echo "📋 Installed packages:"
pip3 list | grep -E "(pandas|Flask|numpy)"

echo "🔄 Don't forget to reload your web app!" 