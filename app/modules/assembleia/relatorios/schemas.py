from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class RelatorioResumoPauta(BaseModel):
    pauta_id: uuid.UUID
    titulo: str | None
    modo_votacao: str | None
    opcao_vencedora: str | None
    percentual_vencedor: Decimal


class RelatorioSinteticoResponse(BaseModel):
    assembleia_id: uuid.UUID
    titulo: str | None
    data: date | None
    total_unidades: int
    total_presentes: int
    total_representados: int
    quorum_percentual_presenca: Decimal
    quorum_percentual_fracao_ideal: Decimal
    pautas: list[RelatorioResumoPauta]


class RelatorioOpcaoItem(BaseModel):
    codigo_opcao: int
    descricao_opcao: str
    quantidade_votos: int
    peso_total: Decimal
    percentual: Decimal


class RelatorioVotoItem(BaseModel):
    unidade_id: uuid.UUID | None
    identificador_externo: str | None
    bloco: str | None
    numero: str | None
    codigo_opcao: int | None
    descricao_opcao: str | None
    tipo_voto: str | None
    tipo_origem: str | None
    peso: Decimal | None
    data_voto: datetime | None


class RelatorioPautaAnalitico(BaseModel):
    pauta_id: uuid.UUID
    titulo: str | None
    descricao: str | None
    status: str | None
    modo_votacao: str | None
    opcoes: list[RelatorioOpcaoItem]
    votos: list[RelatorioVotoItem]
    usa_resultado_manual: bool


class PresencaAtaItem(BaseModel):
    unidade_id: uuid.UUID
    identificador_externo: str
    bloco: str | None
    numero: str | None
    tipo_presenca: str


class RelatorioAnaliticoResponse(BaseModel):
    assembleia_id: uuid.UUID
    titulo: str | None
    data: date | None
    status: str | None
    quorum_percentual_presenca: Decimal
    quorum_percentual_fracao_ideal: Decimal
    total_unidades: int
    total_presentes: int
    total_representados: int
    pautas: list[RelatorioPautaAnalitico]
    presencas: list[PresencaAtaItem]


class AtaAutomaticaResponse(BaseModel):
    assembleia_id: uuid.UUID
    titulo: str | None
    data: date | None
    texto: str


