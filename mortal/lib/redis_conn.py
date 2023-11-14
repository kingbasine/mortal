from mortal import setting
from aioredis import create_redis_pool, Redis
from mortal.uitils.uitils import GetSetTer

r_pool = GetSetTer()


async def setup_redis():
    """初始化redis连接池"""
    for name, conf in setting.REDIS_SETTINGS.items():
        redis_conn = await get_redis_pool_with_kwargs(**conf)
        setattr(r_pool, name, redis_conn)


async def get_redis_pool(rdb_conf, **kwargs) -> Redis:
    """
    redis连接池
    """
    return await get_redis_pool_with_kwargs(
        host=rdb_conf.host,
        port=rdb_conf.port,
        db=rdb_conf.db,
        password=rdb_conf.password,
        **kwargs
    )


async def get_redis_connection(name=None):
    """获取一个redis连接"""
    name = name or 'default'
    redis_setting = setting.REDIS_SETTINGS.get(name)
    if not redis_setting:
        return None

    if hasattr(r_pool, name):
        return getattr(r_pool, name)

    redis_conn = await get_redis_pool_with_kwargs(**redis_setting)
    setattr(r_pool, name, redis_conn)
    return redis_conn


async def get_redis_pool_with_kwargs(host, port, db, password, **kwargs) -> Redis:
    """redis连接池【显式传参】"""
    minsize = kwargs.get('minsize') or 1
    maxsize = kwargs.get('maxsize') or 5
    timeout = kwargs.get('timeout') or 3

    pool = await create_redis_pool(
        f"redis://:{password}@{host}:{port}/{db}?encoding=utf-8",
        minsize=minsize,
        maxsize=maxsize,
        timeout=timeout
    )
    return pool
