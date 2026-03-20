from fastapi import APIRouter

from app.api.routes.links import router as links_router


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(links_router)
    return router