import time
from datetime import datetime
from copy import deepcopy

from mortal.uitils.time_uitils import str_to_timestamp


class HTTPException(Exception):
    def __init__(self, code: str, message: str, service_name: str = None):
        self.code = str(code)
        self.message = message
        self.service_name = service_name


class ErrorNode:
    def __init__(self, code, msg):
        self.code = code
        self.message = msg

    @property
    def service_name(self):
        return setting.SERVICE_NAME

    def unpack(self):
        return self.code, self.message

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message
        }

    def apply(self, *args, **kwargs):
        _node = deepcopy(self)
        _node.message = _node.message.format(*args, **kwargs)
        return _node

    def to_exception(self):
        return HTTPException(self.code, self.message)


class Error:
    success = ErrorNode("0000", "success")
    no_auth = ErrorNode("0403", "您没有操作权限")
    lock_fail = ErrorNode("9998", "获取锁失败")
    timeout_error = ErrorNode("9999", "timeout")
    code_not_found = ErrorNode("ffff", "code not found")
    request_error = ErrorNode("FFFF", "request error")
    frequently_request_error = ErrorNode("0428", "request too frequently")
    service_unavailable = ErrorNode("FFFF", "service unavailable")


def handle_datetime(_obj):
    """
    正则匹配时间，获取format_str
    2020-11-20 15:49:38.000

    """
    try:
        # 兼容db_server
        if isinstance(_obj, str):
            _obj = _obj.replace("T", " ")
            return str_to_timestamp(_obj)
        elif isinstance(_obj, int):
            return _obj
        elif isinstance(_obj, datetime):
            return _obj.timestamp()
        elif _obj is None:
            return
        else:
            raise Exception(f"意外的时间格式: {_obj},{type(_obj)}")
    except:
        raise Exception(f"意外的时间格式: {_obj},{type(_obj)}")


def format_response(_obj, _key=None):
    _new_obj = None
    if isinstance(_obj, dict):
        _new_obj = {}
        for k, v in _obj.items():
            key, info = format_response(v, k)
            _new_obj[key] = info

    elif isinstance(_obj, list):
        _new_obj = []
        for i in _obj:
            _, info = format_response(i)
            _new_obj.append(info)
    elif _key and _key.endswith("_time"):
        _new_obj = handle_datetime(_obj)
        _key = f"{_key[:-5]}_ts"
    else:
        _new_obj = _obj
    return _key, _new_obj


def set_response(content, do_format=True):
    """
    在model检查前处理数据
    用于统一响应数据
    此时拿到的数据已经是未经过model检查的
    """
    content["now_ts"] = int(time.time())
    if content.get("data") and do_format:
        _, content["data"] = format_response(content["data"])
    return content


def format_success_response(data=None, do_format=True):
    """成功的响应【格式化时间：将 _time 结尾的字段全部转化为 _ts】"""
    data = data or {}
    content = {
        'code': Error.success.code,
        'message': "SUCCESS",
        'service_name': Error.success.service_name,
        'data': data
    }
    return set_response(content, do_format)


def format_fail_response(message, data=None, code='FFFF', do_format=True, service_name=None):
    """失败的响应【格式化时间：将 _time 结尾的字段全部转化为 _ts】"""
    if data is None:
        data = {}
    content = {
        'code': code,
        'message': str(message),
        'data': data
    }
    if service_name:
        content['service_name'] = service_name
    return set_response(content, do_format)


def success_response(data=None):
    """成功的响应【不格式化时间】"""
    return format_success_response(data, do_format=False)


def fail_response(message, data=None, code='FFFF', service_name=None):
    """失败的响应【不格式化时间】"""
    return format_fail_response(message, data, code, do_format=False, service_name=service_name)
