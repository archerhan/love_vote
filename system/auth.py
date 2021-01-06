from fastapi import APIRouter, Request, Depends
from system.model import SysUser, SysLoginLog
from sqlalchemy.orm import Session
from db.db_cache import cache
from db.db_base import DBHandleBase
from public.str_utils import encrypt_password
from core import config
from system.form import LoginForm
from system.model import SysMenu as Menu, SysRoleMenu as roleMenu
from public.oppose_crawler import backstage
from public.data_utils import get_tree_data, orm_one_to_dict, sql_all_to_dict, orm_all_to_dict
from fastapi.responses import JSONResponse
from public.get_data_by_cache import get_current_user, get_token_key


router = APIRouter()


@router.post('/login')
async def login(request: Request, form: LoginForm):
    """
    登录
    """
    db: Session = request.state.db
    session_user = db.query(SysUser.id, SysUser.login_name, SysUser.user_name, SysUser.role_id).filter(
        SysUser.login_name == form.login_name, SysUser.password == encrypt_password(form.password)).first()
    user = orm_one_to_dict(session_user)
    # 写入登录日志
    new_log = SysLoginLog()
    new_log.login_name = form.login_name
    new_log.login_ip = request.scope['client'][0] if request.scope and request.scope['client'] else ''
    # 获取浏览器信息
    db_handle = DBHandleBase()
    for raw in request.headers.raw:
        if bytes.decode(raw[0]) == 'user-agent':
            new_log.browser = bytes.decode(raw[1])
    if not user:
        new_log.is_success = False
        db_handle.create(db, get_token_key(request), new_log)
        return JSONResponse({'code': config.HTTP_400, 'message': '账号或密码错误'})
    token_key = 'token' + encrypt_password(str(user['id']))
    if not cache.exists(token_key):
        token = 'token' + encrypt_password(str(user['id']))
        cache.set(token, str(user), config.REDIS_TIME_OUT)
    new_log.user_name = user['user_name']
    new_log.is_success = True
    db_handle.create(db, token_key, new_log)
    return JSONResponse({'code': config.HTTP_200, 'token': token_key, 'user': user})