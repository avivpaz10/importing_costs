#!/bin/bash

# Build script for Render.com deployment with Python 3.9.16
echo "🚀 Starting build process for Python 3.9.16..."

# Check Python version
echo "📋 Python version:"
python --version

# Verify Python 3.9.x
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$PYTHON_VERSION" == "3.9" ]]; then
    echo "✅ Python 3.9.x detected - compatible!"
else
    echo "⚠️  Warning: Expected Python 3.9.x, got $PYTHON_VERSION"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run compatibility check
echo "🔍 Running compatibility check..."
python verify_python39_compatibility.py

echo "✅ Build completed!" 