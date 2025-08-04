# 🚀 PythonAnywhere Deployment Guide

## Quick Start (5 minutes)

### Step 1: Create PythonAnywhere Account
1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Click "Create a Beginner account" (FREE)
3. Choose a username and password
4. Verify your email

### Step 2: Upload Your Files
1. **Go to Files tab** in your PythonAnywhere dashboard
2. **Create project folder:**
   ```bash
   mkdir importing_project
   cd importing_project
   ```
3. **Upload files** using the web interface:
   - `app.py`
   - `requirements_pythonanywhere.txt`
   - `templates/index.html`
   - `static/` folder (all files)
   - `uploads/` folder (create empty folder)

### Step 3: Install Dependencies
1. **Go to Consoles tab** → **Bash**
2. **Navigate to your project:**
   ```bash
   cd importing_project
   ```
3. **Install requirements:**
   ```bash
   pip install --user -r requirements_pythonanywhere.txt
   ```

### Step 4: Configure Web App
1. **Go to Web tab** → **Add a new web app**
2. **Choose settings:**
   - Manual configuration
   - Python 3.11
3. **Set source code:** `/home/yourusername/importing_project`
4. **Set WSGI file:** `/var/www/yourusername_pythonanywhere_com_wsgi.py`
5. **Edit WSGI file** (replace content with our `pythonanywhere_wsgi.py`)

### Step 5: Update WSGI File
1. **Click on the WSGI file link** in Web tab
2. **Replace all content** with:
   ```python
   import sys
   import os
   
   path = '/home/yourusername/importing_project'
   if path not in sys.path:
       sys.path.append(path)
   
   os.environ['FLASK_ENV'] = 'production'
   os.environ['FLASK_DEBUG'] = '0'
   
   from app import app as application
   ```
3. **Save the file**

### Step 6: Reload and Test
1. **Click "Reload"** in Web tab
2. **Visit your app:** `https://yourusername.pythonanywhere.com`
3. **Test all features** (upload Excel, calculate costs)

## Detailed Instructions

### File Structure on PythonAnywhere
```
/home/yourusername/importing_project/
├── app.py
├── requirements_pythonanywhere.txt
├── pythonanywhere_wsgi.py
├── templates/
│   └── index.html
├── static/
│   ├── icon-192.png
│   ├── icon-512.png
│   ├── icon.svg
│   ├── manifest.json
│   └── sw.js
└── uploads/
    └── (empty folder)
```

### Important Notes

#### 1. **Update Paths in WSGI File**
Replace `yourusername` with your actual PythonAnywhere username:
```python
path = '/home/YOUR_ACTUAL_USERNAME/importing_project'
```

#### 2. **File Permissions**
Make sure uploads folder is writable:
```bash
chmod 755 uploads/
```

#### 3. **Environment Variables**
If you need to set environment variables:
- Go to Web tab → Environment variables
- Add: `FLASK_ENV=production`

#### 4. **Static Files**
Static files are automatically served from `/static/` folder

### Troubleshooting

#### Common Issues:

**1. Import Error in WSGI**
- Check the path in WSGI file matches your username
- Verify all files are uploaded correctly
- Check error logs in Web tab

**2. Module Not Found**
- Install requirements: `pip install --user -r requirements_pythonanywhere.txt`
- Check Python version (use 3.11)

**3. File Upload Not Working**
- Create uploads folder: `mkdir uploads`
- Set permissions: `chmod 755 uploads/`

**4. App Not Loading**
- Check error logs in Web tab
- Verify WSGI file syntax
- Reload the web app

#### Error Logs
- **Go to Web tab** → **Error log** to see detailed errors
- **Go to Web tab** → **Server log** for general logs

### Performance Tips

1. **Use PythonAnywhere Pro** for better performance
2. **Enable HTTPS** (automatic on PythonAnywhere)
3. **Optimize images** in static folder
4. **Use CDN** for Bootstrap (already configured)

### Security

1. **HTTPS is automatic** on PythonAnywhere
2. **File uploads are restricted** to Excel files
3. **Input validation** is implemented
4. **No sensitive data** is stored

### Backup and Updates

#### To update your app:
1. **Upload new files** via Files tab
2. **Reload web app** in Web tab
3. **Test functionality**

#### To backup:
1. **Download files** via Files tab
2. **Export database** (if using one)
3. **Save configuration** settings

## Support

- **PythonAnywhere Help:** [help.pythonanywhere.com](https://help.pythonanywhere.com)
- **Flask Documentation:** [flask.palletsprojects.com](https://flask.palletsprojects.com)
- **Error Logs:** Check Web tab → Error log

## Next Steps

After deployment:
1. **Test all features** thoroughly
2. **Share the URL** with users
3. **Monitor usage** via PythonAnywhere dashboard
4. **Consider upgrading** to Pro account for better performance

Your app will be available at: `https://yourusername.pythonanywhere.com` 