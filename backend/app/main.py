from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, log


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log.info("app.start", app=settings.app_name, env=settings.app_env)
    from app.ai.routing import get_bundle

    get_bundle()
    yield
    log.info("app.stop", app=settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Carwork API",
        description="保险理赔 + 车后市场 AI 平台",
        version="0.1.0",
        lifespan=lifespan,
        debug=settings.app_debug,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
