from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core import config
from db.db_base import DBHandleBase
from system.model import SysDepartment as Dept, SysUser as User, SysRole as Role
from system.form import UserForm
from public.oppose_crawler import backstage
from public.str_utils import encrypt_password
from public.get_data_by_cache import get_token_key, get_current_user
from public.data_utils import orm_one_to_dict, orm_all_to_dict
import datetime

router = APIRouter()


@router.get('/get-user-list', dependencies=[Depends(backstage)], tags=[config.LOG_QUERY], name='获取用户列表')
async def get_user_list(request: Request, dept_id: str = None, user_name: str = None):
    """
    获取用户列表
    """
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('pageSize', 10))
    start = (page - 1) * page_size
    db: Session = request.state.db
    db_user = db.query(User.id, User.login_name, User.user_name, User.gender, User.phone, User.wechat_no, User.email,
                       User.birthday, User.create_time, Dept.department_name, Role.role_name).join(
        Dept, Dept.id == User.department_id).outerjoin(Role, User.role_id == Role.id).filter(Dept.state == 1,
                                                                                             User.state == 1)
    if dept_id:
        # 递归获取部门下面的所有子部门信息
        dept_ids = get_child_dept(db, dept_id)
        db_user = db_user.filter(User.department_id.in_(dept_ids))
    if user_name:
        db_user = db_user.filter(User.user_name == user_name)
    total = db_user.count()
    db_user_list = db_user.limit(page_size).offset(start).all()
    user_list = orm_all_to_dict(db_user_list)
    return JSONResponse({'code': config.HTTP_200, 'data': {'user_list': user_list, 'total': total}})


def get_child_dept(db, dept_id):
    """
    递归获取所有子部门的id
    """
    dept_ids = [dept_id]
    db_depts = db.query(Dept.id).filter(Dept.state == 1, Dept.parent_id == dept_id).all()
    if db_depts:
        dept_ids.extend([x[0] for x in db_depts])
        for db_dept in db_depts:
            get_child_dept(db, db_dept[0])

    return tuple(dept_ids)


@router.post('/save-user', dependencies=[Depends(backstage)], tags=[config.LOG_SAVE], name='保存用户')
async def save_user(request: Request, form: UserForm):
    token_key = get_token_key(request)
    db: Session = request.state.db
    handle_db = DBHandleBase()
    if form.id:
        if not db.query(User.id).filter(User.id == form.id, User.state == 1).scalar():
            return JSONResponse({'code': config.HTTP_404, 'message': '找不到该部门信息'})
        update_dic = {'user_name': form.user_name, 'gender': form.gender, 'wechat_no': form.wechat_no,
                      'phone': form.phone, 'email': form.email, 'birthday': form.birthday,
                      'department_id': form.department_id, 'role_id': form.role_id}
        db_user = db.query(User).filter(User.id == form.id).update(update_dic)
        db.commit()
        if not db_user:
            return JSONResponse({'code': config.HTTP_404, 'message': '修改用户失败'})
        return JSONResponse({'code': config.HTTP_200, 'message': '修改用户成功'})

    new_user = User()
    new_user.login_name = form.login_name
    new_user.password = encrypt_password(form.password)
    new_user.gender = form.gender
    new_user.user_name = form.user_name
    new_user.phone = form.phone
    new_user.wechat_no = form.wechat_no
    new_user.email = form.email
    new_user.birthday = form.birthday
    new_user.department_id = form.department_id
    new_user.role_id = form.role_id
    status_code, user_obj = handle_db.create(db, token_key, new_user)
    if status_code != 200:
        return JSONResponse({'code': config.HTTP_404, 'message': '创建用户失败'})
    return JSONResponse({'code': config.HTTP_200, 'message': '创建用户成功'})


@router.get('/get-user-info', dependencies=[Depends(backstage)], tags=[config.LOG_QUERY], name='获取用户信息')
async def get_user_info(request: Request, user_id: str = None):
    db: Session = request.state.db
    if not user_id:
        return JSONResponse({'code': config.HTTP_404, 'message': '请选择要编辑的用户！'})
    db_user = db.query(User.id, User.login_name, User.user_name, User.phone, User.birthday, User.email, User.gender,
                       User.wechat_no,
                       User.department_id, User.role_id, Dept.department_name, Role.role_name, User.create_time).join(
        Dept, Dept.id == User.department_id).join(Role, Role.id == User.role_id).filter(
        User.id == user_id, User.state == 1, Role.state == 1, Dept.state == 1).first()
    user_info = orm_one_to_dict(db_user)
    return JSONResponse({'code': config.HTTP_200, 'data': user_info})


@router.get('/del-user', dependencies=[Depends(backstage)], tags=[config.LOG_DELETE], name='删除用户')
async def del_user_info(request: Request, user_id: str = None):
    db: Session = request.state.db
    cache_user = get_current_user(request)
    if not user_id:
        return JSONResponse({'code': config.HTTP_404, 'message': '请选择要删除的用户！'})
    del_time = datetime.datetime.now()
    update_dic = {'state': 0, 'deleted_time': del_time, 'deleted_by_id': cache_user['id']}
    db.query(User).filter(User.id == user_id, User.state == 1).update(update_dic)
    db.commit()
    return JSONResponse({'code': config.HTTP_200, 'message': '删除成功'})


@router.get('/check-login-name', dependencies=[Depends(backstage)], tags=[config.LOG_QUERY], name='注册用户用户名查重')
async def check_login_name(request: Request, login_name: str):
    db: Session = request.state.db
    user_num = db.query(User).filter(User.login_name == login_name, User.state == 1).count()
    return JSONResponse({'code': config.HTTP_200, 'data': user_num})


@router.get('/reset-password', dependencies=[Depends(backstage)], tags=[config.LOG_SAVE], name='重置密码')
async def reset_password(request: Request, user_id: str, password: str, old_pwd: str = None):
    db: Session = request.state.db
    if old_pwd:
        check_password = db.query(User).filter(User.id == user_id, User.password == encrypt_password(password)).count()
        if check_password < 1:
            return JSONResponse({'code': config.HTTP_404, 'message': "原密码错误"})
    db_user = db.query(User).filter(User.id == user_id, User.state == 1).count()
    if not db_user:
        return JSONResponse({'code': config.HTTP_404, 'message': "用户不存在"})
    db.query(User).filter(User.id == user_id, User.state == 1).update({
        'password': encrypt_password(password)
    })
    db.commit()
    return JSONResponse({'code': config.HTTP_200, 'message': "重置密码成功"})
