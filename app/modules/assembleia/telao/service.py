from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.assembleia.presenca.service import get_assembleia_by_id
from app.modules.assembleia.telao.manager import telao_manager
from app.modules.assembleia.votacao.service import get_pauta_by_id, get_resultado_pauta


async def enviar_status_assembleia(assembleia_id: UUID, data: dict) -> None:
    await _broadcast(assembleia_id, "assembleia_status", data)


async def enviar_pauta_ativa(assembleia_id: UUID, data: dict) -> None:
    await _broadcast(assembleia_id, "pauta_ativada", data)


async def enviar_resultado(db: Session, pauta_id: UUID) -> None:
    pauta = get_pauta_by_id(db, pauta_id)
    resultado = get_resultado_pauta(db, pauta_id)
    await _broadcast(
        pauta.assembleia_id,
        "resultado_atualizado",
        resultado.model_dump(mode="json"),
    )


async def enviar_mensagem(assembleia_id: UUID, data: dict) -> None:
    await _broadcast(assembleia_id, "mensagem_telao", data)


async def enviar_voto_atualizado(db: Session, pauta_id: UUID, data: dict) -> None:
    pauta = get_pauta_by_id(db, pauta_id)
    await _broadcast(pauta.assembleia_id, "voto_atualizado", data)


def validar_assembleia(db: Session, assembleia_id: UUID) -> None:
    get_assembleia_by_id(db, assembleia_id)


async def _broadcast(assembleia_id: UUID | None, evento: str, data: dict) -> None:
    if assembleia_id is None:
        return
    await telao_manager.broadcast(
        assembleia_id,
        {
            "evento": evento,
            "data": data,
        },
    )


