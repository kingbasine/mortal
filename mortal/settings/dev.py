from .common import *

DEBUG = True

DATABASE = {
    "default": {
        "timezone": "Asia/Shanghai",
        "connections": {
            "mortal": {
                "engine": "tortoise.backends.mysql",
                "credentials": {
                    "host": "",
                    "port": "",
                    "user": "",
                    "password": "",
                    "database": "",
                    "maxsize": "",
                },
            }
        },
        "apps": {
            "mortal": {
                "models": ["mortal.models"],
                "default_connection": "mortal",
            }
        }
    }
}

# redis配置 db是redis的库：0,1,2
REDIS_SETTINGS = {
    "default": {
        "host": "",
        "port": "",
        "db": 0,
        "password": "",
        "minsize": 1,
        "maxsize": 5,
        "timeout": 3
    }
}
