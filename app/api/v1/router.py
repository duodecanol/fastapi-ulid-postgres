from fastapi import APIRouter

from app.api.v1.endpoints import characters

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(characters.router, prefix="/characters", tags=["characters"])
