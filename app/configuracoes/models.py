from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ConfiguracaoCondominio(Base):
    __tablename__ = "configuracoes_condominio"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    condominio_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=True,
    )
    tipo_votacao_padrao: Mapped[str | None] = mapped_column(Text, nullable=True)
    quorum_minimo: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    tempo_votacao_padrao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tempo_fala_padrao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    limite_procuracoes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
