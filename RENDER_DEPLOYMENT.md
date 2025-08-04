# Render.com Deployment Guide (Python 3.9)

## Overview
This guide will help you deploy your Flask import cost calculator to Render.com using Python 3.9, which is more stable and compatible with pandas.

## Prerequisites
- Render.com account (free tier available)
- Your code in a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Repository

### 1.1 Commit and Push Your Changes
```bash
# Add all files to Git
git add .

# Commit your changes
git commit -m "Configure for Render.com with Python 3.9"

# Push to your remote repository
git push origin main
```

### 1.2 Verify Required Files
Make sure your repository contains:
- `app.py` - Your Flask application
- `requirements.txt` - Python dependencies (compatible with Python 3.9)
- `runtime.txt` - Specifies Python 3.9.16
- `.python-version` - Specifies Python 3.9.16
- `render.yaml` - Render.com configuration
- `Procfile` - Process configuration
- `templates/` folder - HTML templates
- `static/` folder - Static files

## Step 2: Deploy to Render.com

### 2.1 Create Render.com Account
1. Go to [render.com](https://render.com)
2. Sign up for a free account
3. Connect your GitHub/GitLab account

### 2.2 Create New Web Service
1. In your Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your repository
4. Choose the repository containing your Flask app

### 2.3 Configure the Service
Use these settings:

**Basic Settings:**
- **Name**: `importing-project` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (if your app is in the root)

**Build & Deploy Settings:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Environment Variables:**
- `PYTHON_VERSION`: `3.9.16`
- `FLASK_ENV`: `production`
- `SECRET_KEY`: (Render will generate this automatically)

### 2.4 Deploy
1. Click "Create Web Service"
2. Render will automatically start building and deploying your app
3. Wait for the build to complete (usually 2-5 minutes)

## Step 3: Verify Deployment

### 3.1 Check Build Logs
1. In your Render dashboard, click on your web service
2. Go to the "Logs" tab
3. Check for any build errors

### 3.2 Test Your Application
1. Once deployed, click on your app's URL
2. Test all functionality:
   - Excel file upload
   - Cost calculations
   - Currency conversion
   - Save/print features

## Step 4: Update Your Application

### 4.1 Automatic Deployments
Render automatically redeploys when you push to your main branch:

```bash
# Make your changes locally
git add .
git commit -m "Your update description"
git push origin main

# Render will automatically deploy the changes
```

### 4.2 Manual Deployments
If needed, you can manually trigger a deployment:
1. Go to your Render dashboard
2. Click on your web service
3. Click "Manual Deploy" → "Deploy latest commit"

## Troubleshooting

### Common Issues:

1. **Build Failures:**
   - Check the build logs in Render dashboard
   - Verify all dependencies are in `requirements.txt`
   - Ensure Python version compatibility

2. **Import Errors:**
   - Check that all required packages are in `requirements.txt`
   - Verify file paths in your Flask app
   - Check the runtime logs

3. **File Upload Issues:**
   - Render has file size limits (free tier: 100MB)
   - Ensure your upload directory is writable
   - Check file permissions

4. **Static Files Not Loading:**
   - Verify your `static/` folder structure
   - Check Flask static file configuration
   - Ensure file paths are correct

### Useful Commands for Debugging:
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Test Flask app locally
python app.py
```

## Configuration Files Explained

### `runtime.txt`
```
python-3.9.16
```
Specifies Python version for Render.com

### `.python-version`
```
3.9.16
```
Specifies Python version for local development

### `requirements.txt`
```
Flask==2.3.3
pandas==2.0.3
openpyxl==3.1.2
xlrd==2.0.1
python-dotenv==1.0.0
Flask-WTF==1.1.1
Werkzeug==2.3.7
gunicorn==20.1.0
requests==2.28.2
```
Python dependencies compatible with Python 3.9

### `render.yaml`
```yaml
services:
  - type: web
    name: importing-project
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: FLASK_ENV
        value: production
```
Render.com configuration

## Important Notes

- **Free Tier Limitations:**
  - 750 hours/month (enough for always-on service)
  - 512MB RAM
  - Shared CPU
  - 100MB file upload limit

- **Performance:**
  - First request might be slow (cold start)
  - Subsequent requests are faster
  - Consider upgrading to paid plan for better performance

- **Security:**
  - HTTPS is enabled by default
  - Environment variables are encrypted
  - Automatic security updates

## Next Steps

1. **Monitor Performance:** Use Render's built-in monitoring
2. **Set Up Custom Domain:** Available on paid plans
3. **Database Integration:** Add PostgreSQL or Redis if needed
4. **CI/CD:** Set up automated testing and deployment

Your Flask app should now be successfully deployed on Render.com with Python 3.9! 