import sys
import os

# Add your project directory to the sys.path
path = '/home/avivpaz10/importing_project'
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
    # Fallback for debugging
    import traceback
    traceback.print_exc()
    raise

# For debugging (optional)
if __name__ == "__main__":
    application.run(debug=False, host='0.0.0.0', port=5000)
