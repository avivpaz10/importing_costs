# 🚀 Quick Deploy to Railway (5 minutes)

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" button → "New repository"
3. Name it: `import-cost-calculator`
4. Make it **Public** (important for free Railway)
5. Click "Create repository"

## Step 2: Push to GitHub

Run these commands in your terminal:

```bash
git remote add origin https://github.com/YOUR_USERNAME/import-cost-calculator.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Click "Sign up with GitHub"
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Find and select your `import-cost-calculator` repository
6. Click "Deploy Now"
7. Wait 2-3 minutes for deployment

## Step 4: Get Your App URL

1. Once deployed, Railway will show your app URL
2. It will look like: `https://your-app-name.railway.app`
3. Click the URL to test your app

## Step 5: Install on Android

1. **Open Chrome** on your Android device
2. **Go to your app URL** (from step 4)
3. **Install the app:**
   - Chrome will show "Add to Home Screen" prompt
   - Or tap menu (⋮) → "Add to Home Screen"
   - Tap "Add" to install
4. **Use like a native app!**

## ✅ What You Get

- 🌐 **Web App**: Works in any browser
- 📱 **Android App**: Install on home screen
- 🔒 **HTTPS**: Secure connection
- ⚡ **Fast**: Optimized for mobile
- 🔄 **Auto Updates**: Gets latest version

## 🆘 Troubleshooting

**If Railway deployment fails:**
- Make sure repository is public
- Check that all files are committed to GitHub
- Verify `railway.json` is in the root folder

**If app doesn't work:**
- Check Railway logs in the dashboard
- Make sure `requirements.txt` has all dependencies
- Verify the app starts locally with `python app.py`

## 📞 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **GitHub Help**: [help.github.com](https://help.github.com)
- **PWA Guide**: [web.dev/install-criteria](https://web.dev/install-criteria)

---

**Your app will be live in 5 minutes!** 🎉 