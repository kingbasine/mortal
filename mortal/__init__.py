import os
import importlib
import sys
from fastapi import FastAPI

from mortal.lib.redis_conn import setup_redis

from mortal.routers import api_router


app = FastAPI(title="系统")


@app.on_event("startup")
async def startup_event():
    # 暂时用这个方法载入环境配置,后续考虑使用pydantic定义配置
    # 此方法，pycharm识别不了setting包
    env = os.environ.setdefault("ENV", "prod")
    sys.modules["setting"] = importlib.import_module(f'mortal.settings.{env}')
    setting = importlib.import_module(f'mortal.settings.{env}')


    app.include_router(api_router, prefix="/mortal/v1/api")  # 初始化路由

    await setup_redis()  # 启动redis

    await setup_mysql()  # 启动mysql
    middleware_list = []  # 中间件
    await Setup.init_base(setting.SERVICE_NAME, app, settings.BASE_DIR, middleware_list=middleware_list, mis_async=True)




@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()
    await app.state.redis.wait_closed()
