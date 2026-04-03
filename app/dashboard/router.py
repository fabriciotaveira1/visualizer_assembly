from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.configuracoes.schemas import DashboardResponse
from app.core.security import require_role
from app.dashboard.service import get_dashboard_metrics


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "",
    response_model=DashboardResponse,
    dependencies=[Depends(require_role("admin"))],
)
def get_dashboard_route(
    db: Session = Depends(get_db),
) -> DashboardResponse:
    return get_dashboard_metrics(db)
