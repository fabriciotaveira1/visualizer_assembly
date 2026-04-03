from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 3},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database() -> None:
    inspector = inspect(engine)
    if inspector.has_table("usuarios"):
        _ensure_importacoes_columns(inspector)
        _ensure_votacao_schema(inspector)
        return

    sql_path = Path(__file__).resolve().parents[2] / "database.sql"
    script = sql_path.read_text(encoding="utf-8")

    raw_connection = engine.raw_connection()
    try:
        cursor = raw_connection.cursor()
        cursor.execute(script)
        raw_connection.commit()
    finally:
        raw_connection.close()

    refreshed_inspector = inspect(engine)
    _ensure_importacoes_columns(refreshed_inspector)
    _ensure_votacao_schema(refreshed_inspector)


def _ensure_importacoes_columns(inspector) -> None:
    if not inspector.has_table("importacoes"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("importacoes")}
    statements: list[str] = []

    if "quantidade_processada" not in existing_columns:
        statements.append(
            "ALTER TABLE importacoes ADD COLUMN quantidade_processada INTEGER DEFAULT 0"
        )
    if "quantidade_sucesso" not in existing_columns:
        statements.append(
            "ALTER TABLE importacoes ADD COLUMN quantidade_sucesso INTEGER DEFAULT 0"
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.exec_driver_sql(statement)


def _ensure_votacao_schema(inspector) -> None:
    statements: list[str] = []

    if inspector.has_table("pautas"):
        pauta_columns = {column["name"] for column in inspector.get_columns("pautas")}
        if "modo_votacao" not in pauta_columns:
            statements.append(
                "ALTER TABLE pautas ADD COLUMN modo_votacao TEXT DEFAULT 'manual'"
            )

    if inspector.has_table("votos"):
        voto_columns = {column["name"] for column in inspector.get_columns("votos")}
        if "tipo_origem" not in voto_columns:
            statements.append("ALTER TABLE votos ADD COLUMN tipo_origem TEXT")
        if "codigo_opcao" not in voto_columns:
            statements.append("ALTER TABLE votos ADD COLUMN codigo_opcao INTEGER")
        if "descricao_opcao" not in voto_columns:
            statements.append("ALTER TABLE votos ADD COLUMN descricao_opcao TEXT")
        if "ip" not in voto_columns:
            statements.append("ALTER TABLE votos ADD COLUMN ip TEXT")
        if "data_voto" not in voto_columns:
            statements.append("ALTER TABLE votos ADD COLUMN data_voto TIMESTAMP")

    if not inspector.has_table("opcoes_votacao"):
        statements.append(
            """
            CREATE TABLE opcoes_votacao (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                pauta_id UUID REFERENCES pautas(id) NOT NULL,
                codigo INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT uq_opcoes_votacao_pauta_codigo UNIQUE (pauta_id, codigo)
            )
            """
        )

    if not inspector.has_table("resultados_manuais"):
        statements.append(
            """
            CREATE TABLE resultados_manuais (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                pauta_id UUID REFERENCES pautas(id) NOT NULL,
                codigo_opcao INTEGER NOT NULL,
                descricao_opcao TEXT NOT NULL,
                quantidade_votos INTEGER NOT NULL,
                peso_total NUMERIC NOT NULL,
                percentual NUMERIC NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.exec_driver_sql(statement)

