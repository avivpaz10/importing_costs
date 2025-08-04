#!/usr/bin/env python3
"""
Python 3.9.16 Compatibility Verification Script
This script checks if your Flask app is compatible with Python 3.9.16
"""

import sys
import importlib

def check_python_version():
    """Check if we're running Python 3.9.x"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 9:
        print("✅ Python 3.9.x detected - compatible!")
        return True
    else:
        print(f"⚠️  Warning: Running Python {version.major}.{version.minor}.{version.micro}")
        print("   Expected Python 3.9.x for optimal compatibility")
        return False

def check_required_packages():
    """Check if all required packages can be imported"""
    required_packages = [
        'flask',
        'pandas', 
        'openpyxl',
        'xlrd',
        'python_dotenv',
        'flask_wtf',
        'werkzeug',
        'gunicorn',
        'requests',
        'numpy'
    ]
    
    print("\n📦 Checking required packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError as e:
            print(f"❌ {package} - Missing: {e}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {missing_packages}")
        return False
    else:
        print("\n✅ All required packages are available!")
        return True

def check_flask_app():
    """Check if Flask app can be imported"""
    print("\n🚀 Checking Flask app...")
    try:
        from app import app
        print("✅ Flask app imported successfully!")
        
        # Check if app has required routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        required_routes = ['/', '/upload', '/calculate', '/get-exchange-rate', '/get-currency-rates', '/upload-robust']
        
        print(f"📋 Found {len(routes)} routes")
        for route in required_routes:
            if route in routes:
                print(f"✅ {route} - OK")
            else:
                print(f"⚠️  {route} - Not found")
        
        return True
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        return False

def check_pandas_compatibility():
    """Check pandas compatibility"""
    print("\n📊 Checking pandas compatibility...")
    try:
        import pandas as pd
        print(f"✅ pandas version: {pd.__version__}")
        
        # Test basic pandas operations
        import numpy as np
        df = pd.DataFrame({'test': [1, 2, 3]})
        result = df['test'].sum()
        print(f"✅ pandas basic operations: OK (sum = {result})")
        
        return True
    except Exception as e:
        print(f"❌ pandas compatibility check failed: {e}")
        return False

def main():
    """Main compatibility check"""
    print("🔍 Python 3.9.16 Compatibility Check")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_required_packages(),
        check_flask_app(),
        check_pandas_compatibility()
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print("🎉 All compatibility checks passed!")
        print("✅ Your app is ready for Python 3.9.16 deployment!")
    else:
        print("⚠️  Some compatibility issues found.")
        print("   Please check the warnings above.")
    
    return all(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 