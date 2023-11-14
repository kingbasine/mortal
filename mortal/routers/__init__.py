"""主路由注册"""

from fastapi import APIRouter
from mortal.routers import login

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
