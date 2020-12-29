# 项目配置中心

# 跨域白名单
ALLOW_ORIGINS = ['*']

# 数据库连接, 多个数据库可用元组
# '数据库类型+数据库驱动名称://用户名:数据库密码@数据库连接地址:端口号/数据库名'
DB_CONN_URI = "mysql+pymysql://root:12345678@localhost:3306/love_vote"

# Redis链接配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_DB = 10
REDIS_TIME_OUT = 5 * 60 * 60

