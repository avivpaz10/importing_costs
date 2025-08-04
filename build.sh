#!/bin/bash

# Build script for Render.com deployment
echo "🚀 Starting build process..."

# Check Python version
echo "📋 Python version:"
python --version

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Build completed!" 