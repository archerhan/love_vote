from fastapi import APIRouter
from system import auth, user

auth_router = APIRouter()

auth_router.include_router(auth.router, prefix='/auth')
auth_router.include_router(user.router, prefix='/user')
