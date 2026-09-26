import os

from slowapi import Limiter
from slowapi.util import get_remote_address

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8010")

limiter = Limiter(key_func=get_remote_address)