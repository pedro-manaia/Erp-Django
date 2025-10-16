import os
from pathlib import Path
import environ
from waitress import serve

BASE_DIR = Path(__file__).resolve().parent
env = environ.Env()
# Load .env from project root
dotenv_file = BASE_DIR / ".env"
if dotenv_file.exists():
    environ.Env.read_env(dotenv_file)
# Read SERVER_PORT (fallback 3100)
port = int(os.environ.get("SERVER_PORT") or env("SERVER_PORT", default=3100))
# Import WSGI app
from erp.wsgi import application
print(f"Starting Waitress on 0.0.0.0:{port} (from .env SERVER_PORT)")
serve(application, host="0.0.0.0", port=port)
