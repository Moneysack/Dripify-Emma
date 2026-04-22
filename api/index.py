"""
Vercel Python entrypoint.
Vercel looks for a variable named `app` (ASGI) in this file.
"""
import sys
from pathlib import Path

# Add project root to path so all imports resolve
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import os
os.chdir(ROOT)

# Import the FastAPI app — all routes defined in dashboard.py
from dashboard import app  # noqa: F401
