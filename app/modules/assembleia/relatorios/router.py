from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_roles
from app.modules.assembleia.relatorios.csv_exporter import export_presence_csv, export_results_csv, export_votes_csv
from app.modules.assembleia.relatorios.pdf_generator import generate_ata_pdf
from app.modules.assembleia.relatorios.schemas import AtaAutomaticaResponse, RelatorioAnaliticoResponse, RelatorioSinteticoResponse
from app.modules.assembleia.relatorios.service import generate_ata_automatica, get_relatorio_analitico, get_relatorio_sintetico


router = APIRouter(prefix="/relatorios", tags=["relatorios"])


@router.get(
    "/sintetico/{assembleia_id}",
    response_model=RelatorioSinteticoResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def get_relatorio_sintetico_route(
    assembleia_id: UUID,
    db: Session = Depends(get_db),
) -> RelatorioSinteticoResponse:
    return get_relatorio_sintetico(db, assembleia_id)


@router.get(
    "/analitico/{assembleia_id}",
    response_model=RelatorioAnaliticoResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def get_relatorio_analitico_route(
    assembleia_id: UUID,
    db: Session = Depends(get_db),
) -> RelatorioAnaliticoResponse:
    return get_relatorio_analitico(db, assembleia_id)


@router.get(
    "/ata/{assembleia_id}",
    response_model=AtaAutomaticaResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def get_ata_route(
    assembleia_id: UUID,
    db: Session = Depends(get_db),
) -> AtaAutomaticaResponse:
    return generate_ata_automatica(db, assembleia_id)


@router.get(
    "/ata/{assembleia_id}/pdf",
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def get_ata_pdf_route(
    assembleia_id: UUID,
    db: Session = Depends(get_db),
) -> Response:
    ata = generate_ata_automatica(db, assembleia_id)
    pdf_bytes = generate_ata_pdf(ata)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="ata-{assembleia_id}.pdf"'},
    )


@router.get(
    "/analitico/{assembleia_id}/csv/votos",
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def export_votes_csv_route(
    assembleia_id: UUID,
    db: Session = Depends(get_db),
) -> Response:
    report = get_relatorio_analitico(db, assembleia_id)
    return Response(
        content=export_votes_csv(report),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="votos-{assembleia_id}.csv"'},
    )


@router.get(
    "/analitico/{assembleia_id}/csv/presencas",
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def export_presence_csv_route(
    assembleia_id: UUID,
    db: Session = Depends(get_db),
) -> Response:
    report = get_relatorio_analitico(db, assembleia_id)
    return Response(
        content=export_presence_csv(report),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="presencas-{assembleia_id}.csv"'},
    )


@router.get(
    "/analitico/{assembleia_id}/csv/resultados",
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def export_results_csv_route(
    assembleia_id: UUID,
    db: Session = Depends(get_db),
) -> Response:
    report = get_relatorio_analitico(db, assembleia_id)
    return Response(
        content=export_results_csv(report),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="resultados-{assembleia_id}.csv"'},
    )


