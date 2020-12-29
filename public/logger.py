import os
import time
from loguru import logger

basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


log_path = os.path.join(basedir, 'logs')

if not os.path.exists(log_path):
    os.mkdir(log_path)

log_path_error = os.path.join(log_path, 'all.log')


logger.add(log_path_error, retention='30 days', enqueue=True)