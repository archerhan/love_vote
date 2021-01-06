from fastapi import APIRouter
from system import urls as auth_urls

api_router = APIRouter()

api_router.include_router(auth_urls.auth_router, prefix='/system')
