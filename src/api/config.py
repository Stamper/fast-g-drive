from pathlib import Path

from environs import Env

BASE_ROOT = Path(__file__).parent.parent
env = Env()
env.read_env(path=str(BASE_ROOT.parent / ".env"))

SECRET_KEY = env.str("SECRET_KEY")
API_BASE_URL = env.str("API_BASE_URL")
