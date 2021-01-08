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


@router.post('/login', dependencies=[Depends(backstage)], name="登录")
async def login(request: Request, form: LoginForm):
    '''
    登录
    '''
    db: Session = request.state.db
    session_user = db.query(SysUser.id, SysUser.login_name, SysUser.user_name, SysUser.role_id).filter(
        SysUser.login_name == form.login_name, SysUser.password == encrypt_password(form.password)).first()
    user = orm_one_to_dict(session_user)
    print(form)
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


@router.post('/login-out', dependencies=[Depends(backstage)], name='登出')
def logout(request: Request):
    """
    登出
    """
    token_key = get_token_key(request)
    if cache.exists(token_key):
        cache.delete(token_key)
        menu_key = 'menu' + token_key[5:]
        cache.delete(menu_key) if cache.exists(menu_key) else None
    return JSONResponse({'code': config.HTTP_200})


@router.post('/get-user-info', dependencies=[Depends(backstage)], tags=[config.LOG_QUERY], name='获取用户基本信息')
async def get_user_info(request: Request):
    token_key = get_token_key(request)
    if not cache.exists(token_key):
        return JSONResponse({'code': config.HTTP_403, 'message': 'token已失效，请重新登录！'})
    user = get_current_user(request)

    return JSONResponse({'code': config.HTTP_200, 'user': user})


@router.get('/get-user-menu', dependencies=[Depends(backstage)], tags=[config.LOG_QUERY], name='获取用户菜单权限')
async def get_user_menu(request: Request):
    """
    获取用户菜单权限
    """
    token_key = get_token_key(request)
    if not cache.exists(token_key):
        return JSONResponse({'code': config.HTTP_403, 'message': 'token已失效，请重新登录！'})
    menu_key = 'menu' + token_key[5:]
    if cache.exists(menu_key):
        tree_menu_list = eval(cache.get(menu_key))
    else:
        db: Session = request.state.db
        user = get_current_user(request)
        role_id = user['role_id']
        all_menu_list = db.query(Menu.id, Menu.parent_id, Menu.menu_name, Menu.menu_code, Menu.menu_url, Menu.menu_icon,
                                 Menu.menu_type).join(roleMenu, Menu.id == roleMenu.menu_id).filter(
            roleMenu.state == 1, Menu.state == 1, roleMenu.role_id == role_id).order_by('idx').all()
        menu_list = orm_all_to_dict(all_menu_list)
        # 使用程序处理树形结构, 使用程序会比访问数据快
        tree_menu_list = []
        paren_menu_list = []
        child_menu_list = []
        if menu_list:
            for menu in menu_list:
                # 第一层
                if not menu['parent_id']:
                    paren_menu_list.append(menu)
                else:
                    child_menu_list.append(menu)
                # 递归获取子的层
            tree_menu_list = get_tree_data(paren_menu_list, child_menu_list)
        cache.set(menu_key, str(tree_menu_list), config.REDIS_TIME_OUT)

    return JSONResponse({'code': config.HTTP_200, 'tree_menu_list': tree_menu_list})


@router.get('/get-setting', dependencies=[Depends(backstage)], tags=[config.LOG_QUERY], name='获取系统设置')
async def get_setting(request: Request):
    info = {
        'name': config.NAME,
        'logo': config.LOGO,
        'header_img': config.HEADER_IMG
    }
    return JSONResponse({'code': config.HTTP_200, 'info': info})
