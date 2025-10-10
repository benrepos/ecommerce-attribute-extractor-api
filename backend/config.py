"""
Configuration module for the backend.

This module loads environment variables from a .env file and provides access to them.
"""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
