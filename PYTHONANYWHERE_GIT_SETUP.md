# PythonAnywhere + Git Setup Guide

## Prerequisites
- PythonAnywhere account (free tier available)
- Your Flask app code in a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Local Repository

### 1.1 Commit and Push Your Changes
```bash
# Add all files to Git
git add .

# Commit your changes
git commit -m "Add PythonAnywhere configuration files"

# Push to your remote repository
git push origin main
```

### 1.2 Verify Your Repository
Make sure your repository contains these essential files:
- `app.py` - Your Flask application
- `requirements_pythonanywhere.txt` - Python dependencies
- `pythonanywhere_wsgi.py` - WSGI configuration
- `templates/` folder - HTML templates
- `static/` folder - Static files (CSS, JS, images)

## Step 2: Set Up PythonAnywhere

### 2.1 Create PythonAnywhere Account
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for a free account
3. Choose a username (e.g., `avivpaz10`)

### 2.2 Access Your PythonAnywhere Dashboard
1. Log in to your PythonAnywhere account
2. You'll see your dashboard with various sections

## Step 3: Clone Your Git Repository

### 3.1 Open a Bash Console
1. In your PythonAnywhere dashboard, click on "Consoles" tab
2. Click "New Console" → "Bash"
3. This opens a terminal where you can run Git commands

### 3.2 Clone Your Repository
```bash
# Navigate to your home directory
cd ~

# Clone your repository (replace with your actual repository URL)
git clone https://github.com/yourusername/importing_project.git

# Navigate into your project directory
cd importing_project

# Verify the files are there
ls -la
```

### 3.3 Alternative: If you don't have a remote repository
If your code is only local, you can:
1. Create a GitHub repository
2. Push your local code to GitHub
3. Then clone it on PythonAnywhere

## Step 4: Set Up Your Web App

### 4.1 Create a New Web App
1. In your PythonAnywhere dashboard, go to "Web" tab
2. Click "Add a new web app"
3. Choose your domain (e.g., `avivpaz10.pythonanywhere.com`)
4. Select "Flask" as the framework
5. Choose Python version (3.9 recommended for compatibility)

### 4.2 Configure the WSGI File
1. After creating the web app, click on the WSGI configuration file link
2. Replace the default content with your custom WSGI file:

```python
import sys
import os

# Add your project directory to the sys.path
path = '/home/avivpaz10/importing_project'  # Replace with your username
if path not in sys.path:
    sys.path.append(path)

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Import your Flask app
try:
    from app import app as application
except ImportError as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
    raise

# For debugging (optional)
if __name__ == "__main__":
    application.run(debug=False, host='0.0.0.0', port=5000)
```

### 4.3 Install Dependencies
1. Go to "Consoles" tab
2. Open a new Bash console
3. Navigate to your project directory:
```bash
cd ~/importing_project
```

4. Install the requirements:
```bash
pip3 install --user -r requirements_pythonanywhere.txt
```

**If you get pandas compilation errors, try the conservative version:**
```bash
pip3 install --user -r requirements_pythonanywhere_conservative.txt
```

### 4.4 Create Uploads Directory
```bash
# Create the uploads directory if it doesn't exist
mkdir -p uploads
```

## Step 5: Configure Your Web App

### 5.1 Set Working Directory
1. Go back to "Web" tab
2. Click on your web app
3. In the "Code" section, set:
   - **Source code**: `/home/avivpaz10/importing_project`
   - **Working directory**: `/home/avivpaz10/importing_project`

### 5.2 Set Environment Variables (if needed)
1. In the "Web" tab, scroll down to "Environment variables"
2. Add any environment variables your app needs:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your_secret_key_here`

## Step 6: Test Your Application

### 6.1 Reload Your Web App
1. In the "Web" tab, click the "Reload" button
2. Wait for the reload to complete

### 6.2 Visit Your Site
1. Click on your web app URL (e.g., `avivpaz10.pythonanywhere.com`)
2. Your Flask app should now be running!

## Step 7: Set Up Automatic Deployment with Git

### 7.1 Create a Deployment Script
Create a file called `deploy.sh` in your project:

```bash
#!/bin/bash
cd ~/importing_project
git pull origin main
pip3 install --user -r requirements_pythonanywhere.txt
echo "Deployment completed!"
```

### 7.2 Make it Executable
```bash
chmod +x deploy.sh
```

### 7.3 Manual Deployment Process
Whenever you want to update your app:

1. **On your local machine:**
   ```bash
   git add .
   git commit -m "Update description"
   git push origin main
   ```

2. **On PythonAnywhere:**
   ```bash
   cd ~/importing_project
   git pull origin main
   pip3 install --user -r requirements_pythonanywhere.txt
   ```

3. **Reload the web app:**
   - Go to "Web" tab
   - Click "Reload"

## Troubleshooting

### Common Issues:

1. **Pandas Compilation Errors:**
   - **Error**: `error: request for member 'real' in something not a structure or union`
   - **Cause**: Python 3.13 compatibility issues with older pandas versions
   - **Solution**: Use the conservative requirements file:
     ```bash
     pip3 install --user -r requirements_pythonanywhere_conservative.txt
     ```
   - **Alternative**: Try installing pandas with binary wheels:
     ```bash
     pip3 install --user --only-binary=all pandas==1.5.3
     ```

2. **Import Errors:**
   - Check that your WSGI file path is correct
   - Verify all dependencies are installed
   - Check the error logs in the "Web" tab

3. **File Upload Issues:**
   - Make sure the `uploads` directory exists and has write permissions
   - Check file size limits (free tier has restrictions)

4. **Static Files Not Loading:**
   - Verify your `static/` folder is in the correct location
   - Check that Flask is serving static files correctly

5. **Database Issues:**
   - PythonAnywhere free tier includes SQLite
   - For other databases, you might need a paid account

### Useful Commands:
```bash
# Check Python version
python3 --version

# Check installed packages
pip3 list

# View error logs
tail -f ~/.local/share/pythonanywhere/logs/yourusername.pythonanywhere.com.error.log

# Check disk usage
df -h

# Force reinstall pandas with binary wheels
pip3 install --user --force-reinstall --only-binary=all pandas==1.5.3
```

## Next Steps

1. **Custom Domain:** Upgrade to a paid plan for custom domains
2. **Database:** Set up a proper database for production
3. **SSL:** Enable HTTPS (available on paid plans)
4. **Monitoring:** Set up error monitoring and logging

## Important Notes

- **Free Tier Limitations:**
  - 512MB storage
  - 1 web app
  - CPU time limits
  - No custom domains
  - No HTTPS on free tier

- **File Upload Limits:**
  - Free tier: 100MB max file size
  - Paid tier: 1GB max file size

- **Always Reload:**
  - After making changes, always reload your web app
  - Changes to Python files require a reload
  - Static files (CSS, JS) are served directly

- **Python Version Compatibility:**
  - PythonAnywhere uses Python 3.13 by default
  - Some packages may not be compatible
  - Use conservative package versions if needed

This setup gives you a professional deployment of your Flask app with easy Git-based updates! 