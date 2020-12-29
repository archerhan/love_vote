from sqlalchemy import BigInteger, Column, DateTime, SmallInteger, String
from sqlalchemy.ext.declarative import declared_attr, declarative_base
import time, random, datetime
from sqlalchemy.orm import Session
from db.db_cache import cache


class Base:

    """将表名改为小写"""
    @declared_attr
    def __tablename__(cls):
        # 如果有自定义表名就取自定义，没有就取小写类名
        table_name = cls._table_name_
        if not table_name:
            model_name = cls.__name__
            ls = []
            for index, char in enumerate(model_name):
                if char.isupper() and index != 0:
                    ls.append('_')
                ls.append(char)
            table_name = ''.join(ls).lower()
        return table_name


BaseDB = declarative_base(cls=Base)


# 使用命令：alembic init alembic 初始化迁移数据库环境
# 这时会生成alembic文件夹 和 alembic.ini文件
class BaseModel(BaseDB):
    """
    表公共字段，其他模型从此模型继承
    """
    __abstract__ = True

    id = Column(String(length=20), primary_key=True, unique=True,autoincrement=False, comment='主键ID')
    state = Column(SmallInteger, index=True, default=0, comment='状态值，0为已删除，1为正常，2为锁定')

    create_time = Column(DateTime, nullable=False, comment='创建时间')
    create_by_id = Column(BigInteger, nullable=True, index=True, comment='创建者ID')

    last_change_time = Column(DateTime, nullable=True, comment='最后修改时间')
    change_by_id = Column(BigInteger, nullable=True, index=True, comment='最后修改者ID')

    deleted_time = Column(DateTime, nullable=True, comment='删除时间')
    deleted_by_id = Column(BigInteger, nullable=True, index=True, comment='删除者ID')


class DBHandleBase:
    """
    公共新增类
    """
    def __init__(self):
        self.now_time = datetime.datetime.now()

    # 自定义单条记录新增方法
    def create(self, db: Session, token_key, obj):
        try:
            user = eval(cache.get(token_key))
            _id = str(time.time()).split('.')[0]
            if len(_id) != 18:
                _id += str(random.randint(1, 9))
            obj.id = _id
            obj.state = 1
            obj.create_by_id = user['id'] if user else None
            obj.create_time = self.now_time
            obj.change_by_id = user['id'] if user else None
            obj.last_change_time = self.now_time
            db.add(obj)
            db.commit()
            db.refresh(obj)
        except Exception as e:
            db.rollback()
            return 404, e
        return 200, obj

    # 自定义批量记录新增方法
    def batch_create(self, db: Session, token_key, obj_list):
        try:
            user = eval(cache.get(token_key))
            for obj in obj_list:
                _id = str(time.time()).split('.')[0]
                if len(_id) != 18:
                    for i in range(18 - len(_id)):
                        _id += str(random.randint(1, 9))
                obj.id = _id
                obj.state = 1
                obj.create_by_id = user['id'] if user else None
                obj.create_time = self.now_time
                obj.change_by_id = user['id'] if user else None
                obj.last_change_time = self.now_time
            db.add_all(obj_list)
            db.commit()
        except Exception as e:
            db.rollback()
            return 404, e
        return 200, True