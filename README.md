# 🚢 Import Cost Calculator

A comprehensive web application for calculating import costs, shipping expenses, and taxes for businesses importing goods. Features Excel file upload, automatic currency conversion, and detailed cost breakdowns.

## ✨ Features

- 📊 **Excel File Upload** - Upload and parse Excel files with product data
- 💰 **Cost Calculation** - Calculate shipping, taxes, and total costs
- 🌍 **Currency Conversion** - Real-time USD/ILS and CNY/ILS rates
- 📱 **PWA Support** - Install as mobile app on Android devices
- 🎨 **Modern UI** - Beautiful, responsive design with Bootstrap
- 📈 **Detailed Reports** - Export results to HTML/PDF
- 🔄 **Real-time Updates** - Live exchange rates and calculations

## 🚀 Quick Deploy

### Option 1: PythonAnywhere (Recommended for beginners)

1. **Run the setup script:**
   ```bash
   python setup_pythonanywhere.py
   ```

2. **Follow the generated guide** in `DEPLOYMENT_GUIDE_[username].md`

3. **Your app will be live** at `https://yourusername.pythonanywhere.com`

### Option 2: Railway (Advanced)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy to Railway:**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repo
   - Deploy automatically

## 📁 Project Structure

```
importing_project/
├── app.py                          # Main Flask application
├── requirements.txt                # Dependencies for Railway
├── requirements_pythonanywhere.txt # Dependencies for PythonAnywhere
├── pythonanywhere_wsgi.py         # WSGI configuration
├── setup_pythonanywhere.py        # Setup script
├── templates/
│   └── index.html                 # Main application interface
├── static/
│   ├── manifest.json              # PWA manifest
│   ├── sw.js                      # Service worker
│   ├── icon-192.png              # App icon (192px)
│   ├── icon-512.png              # App icon (512px)
│   └── icon.svg                  # App icon (SVG)
└── uploads/                       # File upload directory
```

## 🛠️ Local Development

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd importing_project
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   ```
   http://localhost:5000
   ```

## 📱 PWA Installation

### On Android:
1. Open Chrome browser
2. Navigate to your app URL
3. Tap "Add to Home Screen" when prompted
4. Use like a native app!

### On Desktop:
1. Open Chrome browser
2. Navigate to your app URL
3. Click the install icon in the address bar
4. Install the app

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV` - Set to 'production' for deployment
- `SECRET_KEY` - Flask secret key (auto-generated if not set)

### Exchange Rate APIs
The app uses multiple APIs for currency conversion:
- Primary: Exchange Rate API
- Fallback: Manual rates with user input

## 📊 Excel File Format

The app supports Excel files with the following columns:
- Product name/description
- Quantity
- Volume (CBM)
- Cost per unit (USD)

### Supported Formats:
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

## 🎯 Usage

1. **Upload Excel File** - Drag and drop or click to upload
2. **Configure Container Settings** - Set costs, volume, and rates
3. **Add Products** - Manually add products if needed
4. **Calculate Costs** - Click calculate to see detailed breakdown
5. **Export Results** - Save as HTML or print

## 🔒 Security Features

- ✅ File type validation (Excel only)
- ✅ Input sanitization
- ✅ HTTPS enforcement
- ✅ No sensitive data storage
- ✅ Secure file handling

## 🚀 Deployment Options

### PythonAnywhere (Free)
- ✅ Free hosting
- ✅ Easy setup
- ✅ HTTPS included
- ✅ Good for beginners

### Railway (Paid)
- ✅ Automatic deployments
- ✅ Better performance
- ✅ Custom domains
- ✅ Advanced features

### Heroku (Paid)
- ✅ Enterprise features
- ✅ Auto-scaling
- ✅ Advanced monitoring

## 🐛 Troubleshooting

### Common Issues:

**File Upload Not Working:**
- Check file format (.xls/.xlsx only)
- Verify file size (max 10MB)
- Ensure uploads folder exists

**Calculation Errors:**
- Verify all required fields are filled
- Check exchange rates are valid
- Ensure numeric values only

**PWA Not Installing:**
- Use Chrome browser
- Check HTTPS is enabled
- Clear browser cache

### Error Logs:
- **PythonAnywhere:** Check Web tab → Error log
- **Railway:** Check deployment logs
- **Local:** Check terminal output

## 📈 Performance Tips

1. **Optimize Images** - Compress static images
2. **Use CDN** - Bootstrap already uses CDN
3. **Enable Caching** - PWA includes service worker
4. **Minimize Dependencies** - Only essential packages included

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

- **Documentation:** Check the deployment guides
- **Issues:** Create GitHub issues
- **Email:** Contact for business inquiries

## 🎉 What You Get

- 🌐 **Web Application** - Works in any browser
- 📱 **Mobile App** - Install on Android home screen
- 🔒 **Secure** - HTTPS and input validation
- ⚡ **Fast** - Optimized for performance
- 🔄 **Auto Updates** - Gets latest version automatically
- 📊 **Full Features** - All functionality works on mobile

---

**Ready to deploy?** Choose your platform and follow the deployment guide! 🚀 