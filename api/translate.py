"""Vercel endpoint: re-export the FastAPI app from repo-root app.py.

Vercel maps /api/<name> to api/<name>.py as a serverless function and
passes the original request path, so FastAPI routes it normally.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: F401,E402
