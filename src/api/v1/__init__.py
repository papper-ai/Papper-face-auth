from fastapi import APIRouter
from .router import router as api_router

router = APIRouter(prefix="/v1")

router.include_router(api_router)

__all__ = [
    "router",
]
