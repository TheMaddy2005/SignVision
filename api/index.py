"""Vercel entrypoint: expose the FastAPI app from the repo-root app.py.

Vercel runs files under api/ as serverless functions; this shim puts the
repo root on sys.path and re-exports the ASGI app defined in app.py.
Local runs still use `uvicorn app:app` from the repo root.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: F401,E402
