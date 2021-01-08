from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from core import config

engine = create_engine(config.DB_CONN_URI, pool_pre_ping=True)
# 创建连接工厂，关闭自动提交和自动刷新， 工厂（给它传值，它会返回一个结果给你）
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 类似单例模式，线程安全
SessionLocal = scoped_session(session_factory)