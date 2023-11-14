import setting
import aiohttp
from fastapi import Request, APIRouter
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from mortal.lib.middlewares import create_middleware
from mortal.lib.req import fail_response, HTTPException
from mortal.settings.common import LIMIT, REQUEST_LIMIT_PER_HOST, KEEPALIVE_TIMEOUT
from mortal.uitils.uitils import GetSetTer

c = GetSetTer()


def init_setting(service_name=None, base_dir="./"):
    """初始化setting"""
    pass


class Setup:
    @classmethod
    async def init_base(
            cls, service_name=None, app=None, base_dir=None,
            middlewares=None, is_async=False, limit_redis_key="default"
    ):
        await cls.init_rate_limit(limit_redis_key=limit_redis_key)
        # 初始化中间件
        create_middleware(app, middlewares)
        create_global_exception(app)
        create_router(app)
        await setup_req(app)

    @classmethod
    async def init_rate_limit(cls, limit_redis_key="default"):
        """
        初始化流量控制，这里只是把redis的key保存起来，具体的配置初始化，在remote_config里面做
        @param limit_redis_key 限流redis-cell配置的key，默认使用default
        """
        setting.LIMIT_REDIS_KEY = limit_redis_key


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """全局捕捉参数验证异常"""
    message = '.'.join([f'{".".join(map(lambda x: str(x), error.get("loc")))}:{error.get("msg")};'
                        for error in exc.errors()])
    return JSONResponse(
        status_code=200,
        content=fail_response(message),
    )


def create_global_exception(app):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)


async def setup_req(*args):
    c.pool = aiohttp.TCPConnector(
        limit=LIMIT,
        limit_per_host=REQUEST_LIMIT_PER_HOST,
        keepalive_timeout=KEEPALIVE_TIMEOUT,
        force_close=False,
    )


router = APIRouter()


def create_router(app):
    app.include_router(
        router,
        tags=["common"]
    )
