#!/bin/bash

# Build script for Render.com with proper numpy/pandas installation order
echo "🚀 Starting Render.com build process..."

# Check Python version
echo "📋 Python version:"
python --version

# Install numpy first (required by pandas)
echo "📦 Installing numpy first..."
pip install numpy==1.23.5

# Install pandas (depends on numpy)
echo "📦 Installing pandas..."
pip install pandas==1.5.3

# Install other dependencies
echo "📦 Installing other dependencies..."
pip install Flask==2.3.3 openpyxl==3.1.2 xlrd==2.0.1 python-dotenv==1.0.0 Flask-WTF==1.1.1 Werkzeug==2.3.7 gunicorn==20.1.0 requests==2.28.2

echo "✅ Build completed!" 