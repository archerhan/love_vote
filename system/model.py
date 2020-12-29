from sqlalchemy import String, Column, SmallInteger, Date, Boolean
from db.db_base import BaseModel



class SysDepartment(BaseModel):
    _table_name = 'sys_department'
    __table_args__ = ({'comment': '后台部门表'})
    idx = Column(SmallInteger, default=0, comment='显示排序')
    department_name = Column(String(length=30), nullable=False, comment='部门名称')
    remarks = Column(String(length=200), nullable=True, comment='备注说明')
    parent_id = Column(String(length=20), index=True, comment='部门父级ID')

