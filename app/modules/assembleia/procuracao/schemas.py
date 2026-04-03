from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProcuracaoCreate(BaseModel):
    assembleia_id: uuid.UUID
    unidade_origem_id: uuid.UUID
    unidade_destino_id: uuid.UUID


class ProcuracaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assembleia_id: uuid.UUID | None
    unidade_origem_id: uuid.UUID | None
    unidade_destino_id: uuid.UUID | None
    created_at: datetime


