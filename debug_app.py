import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

try:
    print("Attempting to import app...")
    from app.main import app
    print("Successfully imported app.")
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
