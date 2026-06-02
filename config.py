import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

def get_env(key):
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing env var: {key}")
    return value
