# Import Cost Calculator

A web application for calculating shipping costs for importing businesses. The app handles container costs, product volumes, import taxes, currency conversion (USD to ILS), and additional costs like local transportation and container unloading.

## Features

- Upload Excel files with product data (proforma invoice format)
- Dynamic product entry (up to 50 products)
- Automatic calculation of shipping costs based on product volume ratios
- Currency conversion (USD to ILS)
- Import tax calculations
- Additional costs (local transportation, container unloading)
- Smart Excel parsing that adapts to different file formats
- **Progressive Web App (PWA)** - Can be installed on Android devices

## Android App Conversion

This web application has been converted into a **Progressive Web App (PWA)** that can be installed on Android devices like a native app.

### How to Install on Android:

1. **Deploy the web app** to any hosting service (see deployment options below)
2. **Open the app URL** in Chrome on your Android device
3. **Install the app:**
   - Chrome will show an "Add to Home Screen" prompt
   - Or tap the menu (⋮) → "Add to Home Screen"
   - Or tap "Install App" button if shown
4. **Use like a native app:**
   - App icon appears on home screen
   - Opens in full-screen mode
   - Works offline (basic functionality)
   - Receives updates automatically

### PWA Features:

✅ **Installable** - Add to home screen like a native app  
✅ **Offline Support** - Basic functionality works without internet  
✅ **Full Screen** - No browser UI when opened from home screen  
✅ **Responsive** - Optimized for mobile devices  
✅ **Auto Updates** - Gets latest version automatically  

## Deployment Options

### Option 1: Railway (Recommended)

**Steps:**
1. Go to [Railway](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect it's a Python app and deploy it
6. Your app will be available at the provided URL

### Option 2: PythonAnywhere (Free Hosting)

**Steps:**
1. Go to [PythonAnywhere](https://www.pythonanywhere.com)
2. Create a free account
3. Go to "Web" tab → "Add a new web app"
4. Choose "Flask" and Python 3.11
5. Upload your files via the Files tab
6. Install requirements: `pip install -r requirements.txt`
7. Configure the WSGI file to point to your app
8. Your app will be available at: `yourusername.pythonanywhere.com`

### Option 3: Vercel

**Steps:**
1. Go to [Vercel](https://vercel.com)
2. Sign up with GitHub
3. Import your repository
4. Vercel will automatically deploy it
5. Your app will be available at the provided URL

## Local Development

If you want to run this locally for development:

1. **Install Python 3.11 or later**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```bash
   python app.py
   ```
5. **Open your browser to:** `http://localhost:5000`

## Usage

1. **Upload Excel File:**
   - Click "Choose File" and select your Excel file
   - The app will automatically parse product information
   - Review the extracted products and edit if needed

2. **Configure Costs:**
   - Enter container cost in USD
   - Set container volume in CBM
   - Configure import tax rate (as decimal, e.g., 0.17 for 17%)
   - Set USD to ILS exchange rate
   - Add local transportation and unloading costs (optional)

3. **Calculate:**
   - Click "Calculate Shipping Costs"
   - View detailed breakdown of costs per product
   - See totals including all additional costs

## File Format

The app expects Excel files with a specific proforma invoice format:
- Header row starting with "Item NO."
- Product information in the first column (multiline text)
- Quantity, price, and volume data in separate columns
- The app automatically detects and adapts to different column layouts

## PWA Technical Details

The app includes:
- **Web App Manifest** (`static/manifest.json`) - Defines app properties
- **Service Worker** (`static/sw.js`) - Handles caching and offline functionality
- **PWA Meta Tags** - Enable installation prompts
- **Responsive Design** - Optimized for mobile devices

## Support

For technical support or questions about deployment, please refer to the deployment platform's documentation or contact your IT administrator. 