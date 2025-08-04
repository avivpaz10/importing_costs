#!/bin/bash

# PythonAnywhere Deployment Script
# Run this script on PythonAnywhere to update your app

echo "🚀 Starting deployment..."

# Navigate to project directory
cd ~/importing_project

# Pull latest changes from Git
echo "📥 Pulling latest changes from Git..."
git pull origin main

# Try to install dependencies with the main requirements file
echo "📦 Installing dependencies..."
if pip3 install --user -r requirements_pythonanywhere.txt; then
    echo "✅ Dependencies installed successfully!"
else
    echo "⚠️  Main requirements failed, trying conservative version..."
    if pip3 install --user -r requirements_pythonanywhere_conservative.txt; then
        echo "✅ Conservative dependencies installed successfully!"
    else
        echo "⚠️  Conservative requirements failed, trying pandas with binary wheels..."
        pip3 install --user --force-reinstall --only-binary=all pandas==1.5.3
        pip3 install --user Flask==2.3.3 openpyxl==3.1.2 xlrd==2.0.1 python-dotenv==1.0.0 Flask-WTF==1.1.1 Werkzeug==2.3.7 requests==2.28.2
        echo "✅ Dependencies installed with binary wheels!"
    fi
fi

# Create uploads directory if it doesn't exist
echo "📁 Creating uploads directory..."
mkdir -p uploads

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 uploads

echo "✅ Deployment completed!"
echo "🔄 Don't forget to reload your web app in the PythonAnywhere dashboard!"
echo "🌐 Your app should be available at: https://avivpaz10.pythonanywhere.com" 