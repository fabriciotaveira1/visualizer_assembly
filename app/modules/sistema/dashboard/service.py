from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.sistema.configuracoes.schemas import DashboardResponse
from app.modules.assembleia.presenca.models import Presenca
from app.modules.assembleia.votacao.models import Assembleia, Voto


def get_dashboard_metrics(db: Session) -> DashboardResponse:
    total_assembleias = int(db.scalar(select(func.count()).select_from(Assembleia)) or 0)
    total_votos = int(db.scalar(select(func.count()).select_from(Voto)) or 0)
    total_presencas = int(db.scalar(select(func.count()).select_from(Presenca)) or 0)
    assembleias_ativas = int(
        db.scalar(
            select(func.count())
            .select_from(Assembleia)
            .where(Assembleia.status.in_(["aberta", "em_andamento"]))
        )
        or 0
    )

    media = Decimal("0")
    if total_assembleias > 0:
        media = (Decimal(total_votos) / Decimal(total_assembleias)).quantize(Decimal("0.01"))

    return DashboardResponse(
        total_assembleias=total_assembleias,
        total_votos=total_votos,
        assembleias_ativas=assembleias_ativas,
        media_votos_por_assembleia=media,
        total_presencas=total_presencas,
    )


