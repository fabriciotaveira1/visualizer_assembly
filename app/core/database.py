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

    _ensure_importacoes_columns(inspect(engine))


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
