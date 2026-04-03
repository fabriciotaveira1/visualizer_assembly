import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.api import router as api_router
from app.modules.condominio.condominio import models as condominio_models  # noqa: F401
from app.core.database import engine, initialize_database
from app.modules.sistema.integracoes.importador import models as importador_models  # noqa: F401
from app.modules.condominio.morador import models as morador_models  # noqa: F401
from app.modules.assembleia.presenca import models as presenca_models  # noqa: F401
from app.modules.assembleia.procuracao import models as procuracao_models  # noqa: F401
from app.modules.condominio.unidade import models as unidade_models  # noqa: F401
from app.modules.usuarios.auth import models as auth_models  # noqa: F401
from app.modules.sistema.configuracoes import models as configuracoes_models  # noqa: F401
from app.modules.assembleia.votacao import models as votacao_models  # noqa: F401

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

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_application()

