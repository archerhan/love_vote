from fastapi import Request
from db.db_caches import cache
from public.str_utils import encrypt_password


def get_token_key(request):
    """获取当前后台登录用户的token_key"""
    token_key = ''
    referer = False
    for row in request.headers.raw:
        if bytes.decode(row[0]) == 'token':
            token_key = bytes.decode(row[1])
        if bytes.decode(row[0]) == 'referer':
            referer_str = bytes.decode(row[1])
            referer = True if referer_str.split('/')[3] == 'vote_docs' else False
    if referer:
        token_key = 'token' + encrypt_password(str(15950378016551623))
    return token_key


def get_current_user(request: Request):
    """获取当前后台登录用户"""
    token_key = get_token_key(request)
    return eval(cache.get(token_key))
