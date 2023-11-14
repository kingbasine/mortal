from functools import wraps
import hashlib
import re
import socket
from typing import Iterator, Callable


class GetSetTer(object):
    def __init__(self):
        self._x = None

    @property
    def x(self):
        """I'm the 'x' property."""
        print("getter of x called")
        return self._x

    @x.setter
    def x(self, value):
        print("setter of x called")
        self._x = value

    @x.deleter
    def x(self):
        print("deleter of x called")
        del self._x


def get_host():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('114.114.114.114', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def to_int(num_str, default_num=0):
    try:
        return int(num_str)
    except:
        return default_num


def to_float(num_str, default_num=0):
    try:
        return float(num_str)
    except:
        return default_num


def verify_phone(phone):
    """校验是否手机号码"""
    return bool(re.match(re.compile(r'^1[3-9]\d{9}$'), phone))


def add_param_if_true(params, key, value, only_check_none=False):
    """
    不为空则添加到参数中
    :param params 要加入元素的字典
    :param key 要加入字典的key值
    :param value 要加入字典的value值
    :param only_check_none 是否只检查空值 [0、false等是有意义的]
    """
    if value or (only_check_none and value is not None):
        params[key] = value


def get_params_str(params: dict, sort: bool = False) -> str:
    """
    用于拼接 param query string
    :param params: 字典参数
    :param sort: 是否需要对字典进行按键升序排序, 这通常用于加密相关
    :return: k1=v1&k2=v2
    """
    if sort:
        return "&".join([f"{key}={params[key]}" for key in sorted(params.keys())])
    else:
        return "&".join([f"{key}={value}" for key, value in params.items()])


def get_md5_str(sign_dict: dict, salt: str = "", sort: bool = True) -> str:
    """
    根据盐加密对应的字典, 返回对应的md5字符串
    参与加密的参数字典默认会按照键升序排序
    :param sign_dict: 加密字典参数
    :param salt: 加密盐, 默认为空串
    :param sort: 通常需要对字典进行按键升序排序, 默认为真
    :return: 32位的md5加密字符串
    """
    sign_str = get_params_str(sign_dict, sort=sort)
    md5_obj = hashlib.md5()
    md5_obj.update((sign_str + salt).encode())
    return md5_obj.hexdigest()


def groupby(iterable: Iterator, keyfunc: Callable):
    """
    按照keyfunc返回的值分组
    """
    ret = {}

    if not iterable:
        return {}

    if not keyfunc:
        def keyfunc(x):
            return x

    for item in iterable:
        key = keyfunc(item)
        ret.setdefault(key, []).append(item)

    return ret


async def async_partial(func, *args, **kwargs):
    @wraps(func)
    async def _wrapper():
        return await func(*args, **kwargs)
    return _wrapper
