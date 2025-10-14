"""
Configuration module for the backend.

This module loads environment variables from a .env file and provides access to them.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file locally (ignored in Cloud Run)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
