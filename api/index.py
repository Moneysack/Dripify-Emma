"""Vercel entrypoint — imports the FastAPI app from dashboard.py."""
import sys
from pathlib import Path

# Make project root importable
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# Must set working directory so dashboard.html and .env resolve correctly
import os
os.chdir(ROOT)

# Patch: on Vercel there is no Playwright / no persistent scheduler.
# Importing dashboard triggers @app.on_event("startup") only during
# ASGI lifespan — Vercel serverless never runs it, so it's safe.
from dashboard import app  # noqa: F401  (Vercel picks up `app`)
