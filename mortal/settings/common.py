import os

SERVICE_NAME = "mortal"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REQUEST_TIMEOUT = 5

REQUEST_LIMIT_PER_HOST = 300

LIMIT = 0

KEEPALIVE_TIMEOUT = 15

DEFAULT_LOCK_TIME = 10

