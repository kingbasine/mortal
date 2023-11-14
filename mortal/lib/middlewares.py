import functools
import json
import logging

from starlette.datastructures import FormData, MutableHeaders
from starlette.formparsers import MultiPartParser, FormParser
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse, JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send, Message

from mortal.lib.req import fail_response

try:
    from multipart.multipart import parse_options_header
except ImportError:  # pragma: nocover
    parse_options_header = None


class SimpleBaseMiddleware:

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        send = functools.partial(self.send, send=send, request=request)

        response = await self.before_request(request) or self.app
        await response(request.scope, request.receive, send)
        await self.after_request(request)

    async def get_body(self, request):
        """获取请求BODY"""
        async def _receive():
            return {"type": "http.request", "body": body}

        body = await request.body()
        request._receive = _receive
        return body

    async def get_json(self, request):
        """获取json请求参数"""
        return json.loads(await self.get_body(request))

    async def get_form(self, request):
        """获取请求表单[以字典方式返回]"""
        body = await self.get_body(request)

        content_type_header = request.headers.get("Content-Type")
        content_type, options = parse_options_header(content_type_header)
        if content_type == b"multipart/form-data":
            multipart_parser = MultiPartParser(request.headers, request.stream())
            form_data = await multipart_parser.parse()
        elif content_type == b"application/x-www-form-urlencoded":
            form_parser = FormParser(request.headers, request.stream())
            form_data = await form_parser.parse()
        else:
            form_data = FormData()

        async def _receive():
            return {"type": "http.request", "body": body}
        request._receive = _receive
        return dict(form_data)

    async def get_body_params(self, request):
        """获取请求的BODY，以字典形式返回【兼容json和表单方式】"""
        try:
            return await self.get_json(request)
        except:
            return await self.get_form(request)

    async def before_request(self, request: Request) -> [Response, None]:
        """如果需要修改请求信息，可直接重写此方法"""
        return self.app

    async def after_request(self, request: Request):
        """请求后的处理【记录请求耗时等，注意这里没办法对响应结果进行处理】"""
        return None

    async def send(self, message: Message, send: Send, request: Request) -> None:
        """重写send方法【不重写则默认使用原来的】"""
        await send(message)

    async def update_request_header(self, request, key, value):
        """更新请求头"""
        key, value = str(key).encode(), str(value).encode()
        for index, item in enumerate(request.scope['headers']):
            if item[0] == key:
                request.scope['headers'][index] = (key, value)
                return

        request.scope['headers'].append((key, value))


class CorsHeader(SimpleBaseMiddleware):
    WEIGHT = 140
    allow_headers = [
        'X-Requested-With',
        'X-Prototype-Version',
        'Content-Type,Cache-Control',
        'Pragma,Origin,Cookie',
        'x-b3-traceid',
        'x-b3-spanid',
        'x-b3-parentspanid',
        'x-b3-sampled',
        'x-request-id',
        'acl-org-serial-no',
        'acl-sys-name',
        "sys-refer",
        'x-weike-force-trace',
    ]

    async def before_request(self, request):
        if request.url.path.startswith('/health_check'):
            return PlainTextResponse('ok', status_code=200)

        headers = {
            'Access-Control-Allow-Origin': request.headers.get('Origin', '*'),
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'POST, PUT, PATCH, DELETE, OPTIONS, GET',
            'Access-Control-Allow-Headers': ','.join(self.allow_headers), 'Access-Control-Max-Age': '3600',
            'X-Served-By': 'lzwk_aio_server'
        }
        if request.method == 'OPTIONS':
            return PlainTextResponse('ok', status_code=200, headers=headers)

        request.rsp_headers = headers

    async def send(self, message, send, request):
        if message["type"] != "http.response.start":
            await send(message)
            return

        headers = MutableHeaders(scope=message)
        if hasattr(request, 'rsp_headers'):
            headers.update(request.rsp_headers)
        await send(message)


class Authorization(SimpleBaseMiddleware):
    """授权"""


class Authentication(SimpleBaseMiddleware):
    """认证"""


class LogRequests(SimpleBaseMiddleware):
    """日志中间件"""


class HeaderContextMiddleware(SimpleBaseMiddleware):
    """后台任务中间件"""


class TraceMiddleware(SimpleBaseMiddleware):
    """trace id 相关处理"""


class TransparentInfoMiddleware(SimpleBaseMiddleware):
    """信息透传中间件"""


class ErrorHandler(SimpleBaseMiddleware):
    """全局错误抓取"""
    WEIGHT = 150

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        except Exception as e:
            logger.exception(e)  # 日志输出
            await JSONResponse(fail_response(e))(scope, receive, send)


def create_middleware(app, middlewares=None):
    """越晚调用越先进入"""
    middleware_list = [
        Authorization,
        Authentication,
        LogRequests,
        HeaderContextMiddleware,
        TraceMiddleware,
        TransparentInfoMiddleware,
        CorsHeader,
        ErrorHandler,
    ]

    middlewares = middlewares or []
    middlewares.extend(middleware_list)
    middleware_list = sorted(middlewares, key=lambda x: getattr(x, 'WEIGHT', 100))
    print('middleware_list：', middleware_list)
    for item in middleware_list:
        app.add_middleware(item)
