from sqlalchemy import String, Column, SmallInteger, Date, Boolean
from db.db_base import BaseModel


class SysDepartment(BaseModel):
    _table_name_ = 'sys_department'
    __table_args__ = ({'comment': '后台部门表'})
    idx = Column(SmallInteger, default=0, comment='显示排序')
    department_name = Column(String(length=30), nullable=False, comment='部门名称')
    remarks = Column(String(length=200), nullable=True, comment='备注说明')
    parent_id = Column(String(length=20), index=True, comment='部门父级ID')


class SysUser(BaseModel):
    _table_name_ = 'sys_user'
    __tab_args__ = ({'comment': '后台用户表'})

    login_name = Column(String(length=30), nullable=False, comment='登录名')
    password = Column(String(length=50), nullable=False, comment='密码')
    user_name = Column(String(length=50), nullable=False, comment='用户名')
    gender = Column(SmallInteger, nullable=False, default=0, comment='性别， 0为未知，1为男，2为女')
    phone = Column(String(length=30), nullable=False, comment='手机号码')
    wechat_no = Column(String(length=30), nullable=True, comment='微信号')
    email = Column(String(length=30), nullable=True, comment='邮箱'),
    birthday = Column(Date, nullable=True, comment='生日')
    department_id = Column(String(length=20), index=True, comment='部门ID')
    role_id = Column(String(length=20), index=True, comment='角色ID')
    remarks = Column(String(length=200), nullable=True, comment='备注说明')


class SysRole(BaseModel):
    _table_name_ = 'sys_role'
    __table_args__ = ({'comment': '后台角色表'})

    role_name = Column(String(length=30), nullable=False, comment='角色名称')
    data_permission_type = Column(SmallInteger, nullable=False, comment='数据权限，0仅自己参与过的数据,1本部门的权限, 2本部门及所有子部门权限，3表示全部权限,4自定义权限')
    remarks = Column(String(length=200), nullable=True, comment='备注说明')
    idx = Column(SmallInteger, default=0, comment='显示排序')

class RoleDataPermission(BaseModel):
    _table_name_ = 'sys_role_data_permission'
    __table_args__ = ({'comment': '角色数据权限表'})

    role_id = Column(String(length=20), index=True, comment='角色ID')
    department_id = Column(String(length=20), index=True, comment='部门ID')


class SysMenu(BaseModel):
    _table_name_ = 'sys_menu'
    __table_args__ = ({'comment': '菜单表'})

    idx = Column(SmallInteger, default=0, comment='排序')
    parent_id = Column(String(length=20), index=True, comment='父级菜单ID')
    menu_name = Column(String(length=30), nullable=False, comment='菜单名称')
    menu_code = Column(String(length=100), nullable=False, comment='组件路径(前端请求文件的路径里),目录可填Layout')
    menu_url = Column(String(length=100), nullable=False, comment='权限标识,即标识每一个操作权限')
    menu_icon = Column(String(length=100), nullable=True, comment='图标，meta里面的icon')
    menu_type = Column(SmallInteger, default=1, comment='资源类型,0为目录、1为菜单、2为按钮')


class SysRoleMenu(BaseModel):
    # 表名
    _table_name_ = 'sys_role_menu_rel'
    __table_args__ = ({'comment': '角色菜单表'})
    role_id = Column(String(length=20), index=True, comment='角色id')
    menu_id = Column(String(length=20), index=True, comment='菜单id')


class SysOperationLog(BaseModel):
    _table_name_ = 'sys_operation_log'
    operation_url = Column(String(length=100), nullable=True, comment='操作链接')
    name = Column(String(length=200), nullable=True, comment='操作名称')
    ip = Column(String(length=300), nullable=True, comment='操作ip')
    browser = Column(String(length=300), nullable=True, comment='浏览器')
    login_name = Column(String(length=50), nullable=True, comment='操作用户')


class SysLoginLog(BaseModel):
    _table_name_ = 'sys_login_log'
    login_name = Column(String(length=30), nullable=True, comment='登陆账号')
    user_name = Column(String(length=100), nullable=True, comment='用户名')
    login_ip = Column(String(length=30), nullable=True, comment='操作ip')
    browser = Column(String(length=300), nullable=True, comment='浏览器')
    is_success = Column(Boolean, default=False, nullable=True, comment='是否成功登陆')