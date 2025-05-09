#!/usr/bin/env python3
"""
Script to load environment variables from .env file.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment variables from {env_path}")
else:
    print(f"Warning: .env file not found at {env_path}")

# Check if OPENROUTER_API_KEY is set
if "OPENROUTER_API_KEY" in os.environ:
    print("OPENROUTER_API_KEY is set")
else:
    print("Warning: OPENROUTER_API_KEY is not set")
