import time
from datetime import datetime

DATE_FORMAT_NORMAL = '%Y-%m-%d %H:%M:%S.%f'

DATE_FORMAT_DB = '%Y-%m-%dT%H:%M:%S'

DATE_FORMAT_YMD = '%Y-%m-%d'

DATE_FORMAT_YMD_CHI = '%Y年%m月%d日'

DATETIME_FORMAT_NORMAL = '%Y-%m-%d %H:%M:%S'


def str_to_timestamp(str_date, _format=DATETIME_FORMAT_NORMAL):
    try:
        return time.mktime(time.strptime(str_date[:19], _format))
    except:
        return str_date


def ts_to_datetime(timestamp):
    """时间戳转成datetime"""
    return datetime.fromtimestamp(timestamp)


def time_to_timestamp(_time: time):
    return (_time.hour * 60 + _time.minute) * 60 + _time.second


def now_ms_timestamp():
    return int(datetime.now().timestamp() * 1000)


def now_s_timestamp():
    return int(datetime.now().timestamp())


def to_int(num_str, default_num=0):
    try:
        return int(num_str)
    except:
        return default_num


def to_datetime_str(timestamp):
    """时间戳转成标准时间格式"""
    timestamp = to_int(timestamp, int(time.time()))
    return datetime.fromtimestamp(timestamp).strftime(DATETIME_FORMAT_NORMAL)