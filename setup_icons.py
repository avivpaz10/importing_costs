#!/usr/bin/env python3
"""
Setup script for Import Cost Calculator PWA
This script helps convert SVG icons to PNG and provides deployment guidance.
"""

import os
import subprocess
import sys

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import cairosvg
        return True
    except ImportError:
        print("❌ cairosvg not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "cairosvg"])
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install cairosvg. Please install manually:")
            print("   pip install cairosvg")
            return False

def convert_svg_to_png():
    """Convert SVG icon to PNG files."""
    try:
        import cairosvg
        
        # Convert to 192x192
        cairosvg.svg2png(
            url="static/icon.svg",
            write_to="static/icon-192.png",
            output_width=192,
            output_height=192
        )
        print("✅ Created icon-192.png")
        
        # Convert to 512x512
        cairosvg.svg2png(
            url="static/icon.svg",
            write_to="static/icon-512.png",
            output_width=512,
            output_height=512
        )
        print("✅ Created icon-512.png")
        
        return True
    except Exception as e:
        print(f"❌ Error converting icons: {e}")
        return False

def check_files():
    """Check if all required files exist."""
    required_files = [
        "app.py",
        "requirements.txt",
        "templates/index.html",
        "static/manifest.json",
        "static/sw.js",
        "static/icon.svg"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def main():
    print("🚀 Import Cost Calculator PWA Setup")
    print("=" * 40)
    
    # Check files
    if not check_files():
        print("\n❌ Please ensure all files are present before continuing.")
        return
    
    # Convert icons
    print("\n📱 Setting up app icons...")
    if check_dependencies():
        if convert_svg_to_png():
            print("✅ Icons created successfully!")
        else:
            print("❌ Failed to create icons")
            print("💡 You can manually create PNG icons from the SVG file")
    else:
        print("❌ Cannot convert icons automatically")
        print("💡 Please convert static/icon.svg to PNG files manually")
    
    # Deployment instructions
    print("\n🌐 Deployment Options:")
    print("=" * 40)
    print("1. Railway (Recommended):")
    print("   - Go to railway.app")
    print("   - Sign up with GitHub")
    print("   - Deploy from your repository")
    print("   - Get your app URL")
    print()
    print("2. PythonAnywhere (Free):")
    print("   - Go to pythonanywhere.com")
    print("   - Create free account")
    print("   - Upload files and configure")
    print()
    print("3. Local Testing:")
    print("   - Run: python app.py")
    print("   - Open: http://localhost:5000")
    print()
    print("📱 After deployment:")
    print("1. Open your app URL in Chrome on Android")
    print("2. Tap 'Add to Home Screen'")
    print("3. Use like a native app!")
    
    print("\n✅ Setup complete! Ready for deployment.")

if __name__ == "__main__":
    main() 