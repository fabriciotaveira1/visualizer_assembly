from __future__ import annotations

import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Assembleia(Base):
    __tablename__ = "assembleias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    condominio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    titulo: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class Pauta(Base):
    __tablename__ = "pautas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    assembleia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assembleias.id"),
        nullable=True,
    )
    titulo: Mapped[str | None] = mapped_column(Text, nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo_votacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    regra_votacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ordem: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str | None] = mapped_column(Text, nullable=True)
    versao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bloqueada: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    modo_votacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class OpcaoVotacao(Base):
    __tablename__ = "opcoes_votacao"
    __table_args__ = (
        UniqueConstraint("pauta_id", "codigo", name="uq_opcoes_votacao_pauta_codigo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pauta_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pautas.id"),
        nullable=False,
    )
    codigo: Mapped[int] = mapped_column(Integer, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class Voto(Base):
    __tablename__ = "votos"
    __table_args__ = (
        UniqueConstraint("pauta_id", "unidade_id", name="uq_votos_pauta_unidade"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    pauta_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pautas.id"),
        nullable=True,
    )
    unidade_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("unidades.id"),
        nullable=True,
    )
    voto: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo_voto: Mapped[str | None] = mapped_column(Text, nullable=True)
    peso: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    registrado_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=True,
    )
    tipo_origem: Mapped[str | None] = mapped_column(Text, nullable=True)
    codigo_opcao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    descricao_opcao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_voto: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class ResultadoManual(Base):
    __tablename__ = "resultados_manuais"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pauta_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pautas.id"),
        nullable=False,
    )
    codigo_opcao: Mapped[int] = mapped_column(Integer, nullable=False)
    descricao_opcao: Mapped[str] = mapped_column(Text, nullable=False)
    quantidade_votos: Mapped[int] = mapped_column(Integer, nullable=False)
    peso_total: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    percentual: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


