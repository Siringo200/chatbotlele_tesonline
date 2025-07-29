import sys
import os

# Add the current directory to Python's path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    # Use an import string instead of the direct app object
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
