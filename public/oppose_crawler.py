import time
import base64
from fastapi import Request, HTTPException
from core import config
from public.str_utils import encrypt_password
from db.db_cache import cache
from sqlalchemy.orm import Session
from db.db_base import DBHandleBase
from system.model import SysOperationLog
from public.get_data_by_cache import get_token_key, get_current_user
from public.logger import logger


async def backstage(request: Request):
    pass
    # """后台防爬方法"""""
    # raw_list = request.headers.raw
    # token_check = None
    # referer = False
    # for raw in raw_list:
    #     if bytes.decode(raw[0]) == 'tokencheck':
    #         token_check = bytes.decode(raw[1])
    #     if bytes.decode(raw[0]) == 'referer':
    #         referer_str = bytes.decode(raw[1])
    #         referer = True if referer_str.split('/')[3] == 'vote_docs' else False
    # #  访问的是文档接口
    # if referer:
    #     user = {'login_name': 'admin', 'user_name': '吾延', 'id': 15950378016551623}
    #     token_key = 'token' + encrypt_password(str(user['id']))
    #     if not cache.exists(token_key):
    #         token = 'token' + encrypt_password(str(user['id']))
    #         cache.set(token, str(user), config.REDIS_TIME_OUT)
    # else:
    #     if request.url.path.split('/')[-1] != 'login' and request.url.path.split('/')[-1] != 'login-out' and request.url.path.split('/')[-1] !='get-setting':
    #         token = None
    #         for raw in raw_list:
    #             if bytes.decode(raw[0]) == 'token':
    #                 token = bytes.decode(raw[1])
    #         if token is None or not cache.get(token):
    #             raise HTTPException(status_code=403, detail='token失效，请重新登录')
    #     # 自定义你的反爬逻辑
    #     token_check_num = token_check[0: 2]
    #     if int(token_check_num) < 9 or int(token_check_num) > 99:
    #         raise HTTPException(status_code=404, detail='数字-系统操作错误')
    # # 插入操作日志
    # operation_log(request)


async def onstage(request: Request):
    """
    前端反爬
    """


def operation_log(request):
    """
    插入日志
    """
    if not config.OPEN_OPERATION_LOG:
        return
    operation_type = "query"
    name = ""
    for route in request.app.routes:
        if request.scope['path'] == route.path:
            operation_type = route.tags[0] if route.tags else operation_type
            name = route.name
    # 是否开启查询日志
    if not config.OPEN_QUERY_OPERATION_LOG and operation_type == 'query':
        return

    token_key = get_token_key(request)
    if token_key:
        user = get_current_user(request)
        db: Session = request.state.db
        operation_log = SysOperationLog()
        dh_handle = DBHandleBase()
        browser = None
        operation_log.operation_url = request.scope['path']
        operation_log.ip = request.scope['client'][0]
        operation_log.login_name = user['login_name']
        operation_log.name = name
        for raw in request.headers.raw:
            if bytes.decode(raw[0]) == 'user-agent':
                browser = bytes.decode(raw[1])
        operation_log.browser = browser
        dh_handle.create(db, token_key, operation_log)