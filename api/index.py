"""Vercel entrypoint — mirrors the Ask-EINO pattern."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import os
os.chdir(ROOT)

try:
    from dashboard import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()

    @app.get("/{path:path}")
    def _err(path: str):
        return JSONResponse({"initError": str(e), "type": type(e).__name__}, status_code=500)
