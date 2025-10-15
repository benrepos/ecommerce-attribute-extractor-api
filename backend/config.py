"""
Configuration module for the backend.

This module loads environment variables from a .env file and provides access to them.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Names of the keys we need
REQUIRED_KEYS = ["API_KEY", "OPENAI_API_KEY"]

# Path to the .env in the project root (one level above this file)
env_path = Path(__file__).parent.parent / ".env"

# Load .env if any required key is missing
if not all(os.getenv(key) for key in REQUIRED_KEYS):
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded local .env file from {env_path}")
    else:
        print(f".env file not found at {env_path}, relying on existing environment variables")
else:
    print("Using environment variables already set globally")

# Load keys into variables
API_KEY = os.getenv("API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Verify keys are loaded
# print(f"API_KEY loaded: {bool(API_KEY)}")
# print(f"OPENAI_API_KEY loaded: {bool(OPENAI_API_KEY)}")
