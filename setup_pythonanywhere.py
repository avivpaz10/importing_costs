#!/usr/bin/env python3
"""
PythonAnywhere Setup Script
This script helps set up your import cost calculator on PythonAnywhere
"""

import os
import sys

def create_wsgi_file(username):
    """Create WSGI file with correct username"""
    wsgi_content = f'''import sys
import os

# Add your project directory to the sys.path
path = '/home/{username}/importing_project'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Import your Flask app
try:
    from app import app as application
except ImportError as e:
    print(f"Error importing app: {{e}}")
    # Fallback for debugging
    import traceback
    traceback.print_exc()
    raise

# For debugging (optional)
if __name__ == "__main__":
    application.run(debug=False, host='0.0.0.0', port=5000)
'''
    
    with open('pythonanywhere_wsgi.py', 'w', encoding='utf-8') as f:
        f.write(wsgi_content)
    
    print(f"✅ Created pythonanywhere_wsgi.py with username: {username}")

def create_uploads_folder():
    """Create uploads folder if it doesn't exist"""
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✅ Created uploads folder")
    else:
        print("✅ Uploads folder already exists")

def check_files():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'requirements_pythonanywhere.txt',
        'templates/index.html',
        'static/manifest.json',
        'static/sw.js'
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
    else:
        print("✅ All required files found")
        return True

def create_deployment_guide(username):
    """Create a personalized deployment guide"""
    guide_content = f'''# PythonAnywhere Deployment Guide for {username}

## Quick Setup Steps:

1. **Upload these files to PythonAnywhere:**
   - app.py
   - requirements_pythonanywhere.txt
   - pythonanywhere_wsgi.py
   - templates/index.html
   - static/ (entire folder)
   - uploads/ (empty folder)

2. **Install dependencies:**
   ```bash
   cd importing_project
   pip install --user -r requirements_pythonanywhere.txt
   ```

3. **Configure web app:**
   - Go to Web tab → Add a new web app
   - Choose: Manual configuration, Python 3.11
   - Source code: /home/{username}/importing_project
   - WSGI file: /var/www/{username}_pythonanywhere_com_wsgi.py

4. **Update WSGI file:**
   - Click on WSGI file link in Web tab
   - Replace content with pythonanywhere_wsgi.py content
   - Save and reload

5. **Test your app:**
   - Visit: https://{username}.pythonanywhere.com
   - Test Excel upload and cost calculation

## Your app URL: https://{username}.pythonanywhere.com
'''
    
    with open(f'DEPLOYMENT_GUIDE_{username}.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"✅ Created DEPLOYMENT_GUIDE_{username}.md")

def main():
    print("🚀 PythonAnywhere Setup Script")
    print("=" * 40)
    
    # Get username
    username = input("Enter your PythonAnywhere username: ").strip()
    if not username:
        print("❌ Username is required")
        return
    
    print(f"\nSetting up for user: {username}")
    print("-" * 30)
    
    # Check files
    if not check_files():
        print("\n❌ Please make sure all required files are present")
        return
    
    # Create uploads folder
    create_uploads_folder()
    
    # Create WSGI file
    create_wsgi_file(username)
    
    # Create deployment guide
    create_deployment_guide(username)
    
    print("\n🎉 Setup complete!")
    print(f"📁 Files ready for upload to PythonAnywhere")
    print(f"📖 Check DEPLOYMENT_GUIDE_{username}.md for instructions")
    print(f"🌐 Your app will be at: https://{username}.pythonanywhere.com")

if __name__ == "__main__":
    main() 