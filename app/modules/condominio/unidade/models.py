from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Unidade(Base):
    __tablename__ = "unidades"
    __table_args__ = (
        UniqueConstraint(
            "condominio_id",
            "identificador_externo",
            name="uq_unidades_condominio_identificador_externo",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    condominio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
    )
    bloco: Mapped[str | None] = mapped_column(Text, nullable=True)
    numero: Mapped[str | None] = mapped_column(Text, nullable=True)
    identificador_externo: Mapped[str] = mapped_column(Text, nullable=False)
    fracao_ideal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )


