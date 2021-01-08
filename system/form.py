from pydantic import BaseModel
from fastapi import Form


class LoginForm(BaseModel):
    login_name: str = Form(...)
    password: str = Form(...)


class DeptForm(BaseModel):
    id: str = None
    parent_id: str = None
    idx: int = 0
    department_name: str
    remarks: str = None


class MenuForm(BaseModel):
    id: str = None
    parent_id: str = None
    idx: int = 0
    menu_type: int = 1
    menu_name: str
    menu_code: str
    menu_url: str
    menu_icon: str = None


class RoleForm(BaseModel):
    id: str = None
    idx: int = 0
    role_name: str
    data_permission_type: int
    remarks: str = None
    menu_id_list: list
    dept_id_list: list = []


class UserForm(BaseModel):
    id: str = None
    login_name: str = None
    password: str = None
    user_name: str
    gender: int = 0
    phone: str
    wechat_no: str = None
    email: str = None
    birthday: str = None
    department_id: str
    role_id: str
