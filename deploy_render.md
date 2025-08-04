# Render.com Deployment Instructions

## Step 1: Push to GitHub
Make sure your code is pushed to GitHub:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push
```

## Step 2: Deploy on Render.com

1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" and select "Web Service"
3. Connect your GitHub account if not already connected
4. Select your repository: `importing_project`
5. Configure the service:
   - **Name**: `importing-costs` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free (or choose paid if needed)

6. Click "Create Web Service"

## Step 3: Environment Variables (Optional)
If you need to set any environment variables:
1. Go to your service dashboard
2. Click "Environment" tab
3. Add any required environment variables

## Step 4: Access Your App
Once deployed, Render will provide you with a URL like:
`https://your-app-name.onrender.com`

## Troubleshooting
- Check the logs in the Render dashboard if deployment fails
- Ensure all dependencies are in `requirements.txt`
- Make sure the `app.py` file is in the root directory 