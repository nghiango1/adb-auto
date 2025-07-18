import os
from dotenv import load_dotenv

# Make sure env is correctly load before access any of the variable
load_dotenv()

# Constaint
VERBOSE = os.environ.get("VERBOSE", "true") == "true"
DEBUG = os.environ.get("DEBUG", "false") == "true"
SCREENSHOT_IMAGES = os.environ.get("SCREENSHOT_IMAGES", "/tmp/screen.png")
TOTAL_DIVIDE = int(os.environ.get("TOTAL_DIVIDE", "3"))
RELOAD_INTERVAL = max(int(os.environ.get("RELOAD_INTERVAL", "3")), 0.5)

# Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_USERNAME = os.environ.get("REDIS_USERNAME", "default")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "secret")
REDIS_SSL = os.environ.get("VERBOSE", "true") == "true"
REDIS_SSL_CERTFILE = os.environ.get("REDIS_SSL_CERTFILE", "./local/redis_user.crt")

REDIS_SSL_KEYFILE = os.environ.get(
    "REDIS_SSL_KEYFILE", "./local/redis_user_private.key"
)
REDIS_SSL_CA_CERTS = os.environ.get("REDIS_SSL_CA_CERTS", "./local/redis_ca.pem")
