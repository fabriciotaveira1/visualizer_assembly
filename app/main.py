import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import router as api_router
from app.condominio import models as condominio_models  # noqa: F401
from app.core.database import engine, initialize_database
from app.integracoes.importador import models as importador_models  # noqa: F401
from app.morador import models as morador_models  # noqa: F401
from app.unidade import models as unidade_models  # noqa: F401
from app.auth import models as auth_models  # noqa: F401
from app.votacao import models as votacao_models  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        initialize_database()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.warning("Database unavailable during startup; continuing without DB: %s", exc)
    yield


def create_application() -> FastAPI:
    app = FastAPI(
        title="Modular FastAPI Service",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(api_router)

    return app


app = create_application()
