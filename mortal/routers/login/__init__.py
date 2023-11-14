from fastapi import APIRouter

from .apis import invoice

router = APIRouter()

router.add_api_route(
    ".login",
    invoice.login,
    methods=["post"],
    summary="登录"
)
