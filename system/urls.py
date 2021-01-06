from fastapi import APIRouter
from system import auth

auth_router = APIRouter()

auth_router.include_router(auth.router, prefix='/auth')
