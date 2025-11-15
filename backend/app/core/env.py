# app/core/env.py

import os
from pathlib import Path
from dotenv import load_dotenv


def load_env():
    """
    Walk upward from this file until we find a directory containing `.env`.
    Loads the first match.
    """
    current_dir = Path(__file__).resolve().parent

    for parent in [current_dir] + list(current_dir.parents):
        env_file = parent / ".env"
        infra_env_file = parent / "infra" / ".env"

        if env_file.exists():
            load_dotenv(env_file)
            print(f"✔ Loaded .env from: {env_file}")
            return str(env_file)

        if infra_env_file.exists():
            load_dotenv(infra_env_file)
            print(f"✔ Loaded .env from: {infra_env_file}")
            return str(infra_env_file)

    raise FileNotFoundError(
        "❌ Could not find .env file anywhere above the backend directory."
    )


def require_env(name: str):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def validate_environment():
    required = [
        "OPENAI_API_KEY",
        "GOOGLE_PROJECT_ID",
        "GOOGLE_APPLICATION_CREDENTIALS",
    ]
    for key in required:
        require_env(key)

    print("✔ Environment validation successful from env.py")
