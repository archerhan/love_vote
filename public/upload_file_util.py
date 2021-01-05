from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from core import config
import os, time, random

router = APIRouter()


@router.post('/upload_file')
async def upload_file(save_path: str = Form(...), file: UploadFile = File(...)):
    # 判断文件夹是否定义
    if not ('STATIC_DIR' in vars(config)):
        return JSONResponse({'code': config.HTTP_404, 'message': '静态文件根目录未创建'})
    # 文件大小
    if (file.spool_max_size / 1024 / 1024) > 5:
        return JSONResponse({'code': config.HTTP_404, 'message': '上传的文件不能大于5m'})
    # 插入的真实路径 如: 'H:\python\project\love_vote\static'
    insert_file_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)).split('love_vote')[0], 'love_vote'), config.STATIC_DIR)
    # 插入表的字段的路径
    file_name = '爱投票管理系统_' + str(time.time()).split('.')[0] + str(random.randrange(1, 999, 3)) + '.' + file.filename.split('.')[len(file.filename.split('.')) - 1]
    # 文件后缀
    # name_suffix = '.' + file.filename.split('.')[len(file.filename.split('.')) - 1]
    # 获取静态文件夹的目录
    if not save_path:
        insert_file_path = os.path.join(insert_file_path, file_name)
        # 返回前端供入库的路径
        file_path = os.path.join(config.STATIC_DIR, file_name)
    else:
        save_path = save_path[1:] if save_path[0] == '/' or save_path[0] == '\\' else save_path
        insert_file_path = os.path.join(os.path.join(insert_file_path, save_path))
        if not os.path.exists(insert_file_path):
            os.makedirs(insert_file_path)
        insert_file_path = os.path.join(insert_file_path, file_name)
        file_path = os.path.join(config.STATIC_DIR, os.path.join(save_path, file_name))
    file_content = await file.read()
    with open(insert_file_path, 'wb') as f:
        f.write(file_content)
    f.close()

    return JSONResponse({'code': config.HTTP_200, 'file_name': file_name, 'file_path': ('/' + file_path).replace('\\', '/')})
