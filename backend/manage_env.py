"""
manage_env.py: Utility to load environment variables from .env using python-dotenv.
Usage: Import and call load_env() at the start of your app.
"""
from pathlib import Path
from dotenv import load_dotenv
import os

def load_env():
    """Load environment variables from .env in project root."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)

# Optionally, expose a function to get env variables with default

def get_env(key, default=None):
    return os.getenv(key, default)
