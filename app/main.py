from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router as api_v1_router
from app.core.config import settings


def get_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include routers
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    @app.get("/")
    async def root():
        return JSONResponse(
            content={
                "message": "Welcome to Character Chat Settings Management API",
                "docs_url": "/docs",
                "redoc_url": "/redoc",
            }
        )

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:get_app", host="0.0.0.0", port=8000, reload=True)
