#!/bin/bash

# PythonAnywhere Initial Setup Script
# Run this script once on PythonAnywhere to set up your environment

echo "🔧 Setting up PythonAnywhere environment..."

# Navigate to home directory
cd ~

# Clone the repository (replace with your actual repository URL)
echo "📥 Cloning repository..."
git clone https://github.com/yourusername/importing_project.git

# Navigate to project directory
cd importing_project

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user -r requirements_pythonanywhere.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p static
mkdir -p templates

# Set permissions
echo "🔐 Setting permissions..."
chmod 755 uploads
chmod 755 static
chmod 755 templates

# Make deployment script executable
chmod +x deploy.sh

echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Create a new web app (Flask)"
echo "3. Set source code to: /home/avivpaz10/importing_project"
echo "4. Set working directory to: /home/avivpaz10/importing_project"
echo "5. Update the WSGI file with the content from pythonanywhere_wsgi.py"
echo "6. Reload your web app"
echo ""
echo "🌐 Your app will be available at: https://avivpaz10.pythonanywhere.com" 