from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.sistema.integracoes.importador.mappers.morador_mapper import map_morador_row
from app.modules.sistema.integracoes.importador.mappers.unidade_mapper import map_unidade_row
from app.modules.sistema.integracoes.importador.models import Importacao
from app.modules.sistema.integracoes.importador.parsers.csv_moradores import parse_csv_moradores
from app.modules.sistema.integracoes.importador.parsers.csv_unidades import parse_csv_unidades
from app.modules.sistema.integracoes.importador.validators.morador_validator import (
    validate_morador_row,
    validate_moradores_context,
)
from app.modules.sistema.integracoes.importador.validators.unidade_validator import (
    validate_unidade_row,
    validate_unidades_context,
)
from app.modules.condominio.morador.models import Morador
from app.modules.condominio.unidade.models import Unidade


@dataclass
class ImportResult:
    importacao: Importacao
    processados: int
    sucessos: int
    erros: list[dict[str, Any]]

    @property
    def status(self) -> str:
        if self.processados == 0:
            return "erro"
        if not self.erros:
            return "sucesso"
        if self.sucessos == 0:
            return "erro"
        return "parcial"

    def to_dict(self) -> dict[str, Any]:
        return {
            "importacao_id": str(self.importacao.id),
            "tipo": self.importacao.tipo,
            "arquivo_nome": self.importacao.arquivo_nome,
            "status": self.importacao.status,
            "quantidade_processada": self.importacao.quantidade_processada,
            "quantidade_sucesso": self.importacao.quantidade_sucesso,
            "quantidade_erros": len(self.erros),
            "erros": self.erros,
        }


async def import_unidades_csv(
    db: Session,
    condominio_id: UUID,
    file: UploadFile,
) -> dict[str, Any]:
    validate_unidades_context(db, condominio_id)
    rows = parse_csv_unidades(await read_csv_upload(file))
    importacao = create_importacao_log(db, condominio_id, "unidades", file.filename)
    seen_identificadores: set[str] = set()
    erros: list[dict[str, Any]] = []
    sucessos = 0

    for index, row in enumerate(rows, start=1):
        mapped_row = map_unidade_row(row)
        row_errors = validate_unidade_row(mapped_row, seen_identificadores)

        identificador = mapped_row.get("identificador_externo")
        if identificador:
            seen_identificadores.add(identificador.lower())

        if row_errors:
            erros.append(_build_error(index, row_errors, row))
            continue

        try:
            _upsert_unidade(db, condominio_id, mapped_row)
            db.commit()
            sucessos += 1
        except HTTPException as exc:
            db.rollback()
            erros.append(_build_error(index, [str(exc.detail)], row))
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            erros.append(_build_error(index, [f"Unexpected error: {exc}"], row))

    result = finalize_importacao_log(db, importacao, len(rows), sucessos, erros)
    return result.to_dict()


async def import_moradores_csv(
    db: Session,
    condominio_id: UUID,
    file: UploadFile,
) -> dict[str, Any]:
    validate_moradores_context(db, condominio_id)
    rows = parse_csv_moradores(await read_csv_upload(file))
    importacao = create_importacao_log(db, condominio_id, "moradores", file.filename)
    erros: list[dict[str, Any]] = []
    sucessos = 0

    for index, row in enumerate(rows, start=1):
        mapped_row = map_morador_row(row)
        row_errors = validate_morador_row(mapped_row)
        if row_errors:
            erros.append(_build_error(index, row_errors, row))
            continue

        try:
            _upsert_morador(db, condominio_id, mapped_row)
            db.commit()
            sucessos += 1
        except HTTPException as exc:
            db.rollback()
            erros.append(_build_error(index, [str(exc.detail)], row))
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            erros.append(_build_error(index, [f"Unexpected error: {exc}"], row))

    result = finalize_importacao_log(db, importacao, len(rows), sucessos, erros)
    return result.to_dict()


async def read_csv_upload(file: UploadFile) -> str:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    for encoding in ("utf-8-sig", "latin-1", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Could not decode CSV file.",
    )


def _upsert_unidade(db: Session, condominio_id: UUID, mapped_row: dict[str, Any]) -> Unidade:
    identificador = mapped_row["identificador_externo"]
    unidade = db.scalar(
        select(Unidade).where(
            Unidade.condominio_id == condominio_id,
            Unidade.identificador_externo == identificador,
        )
    )

    if unidade is None:
        unidade = Unidade(
            condominio_id=condominio_id,
            identificador_externo=identificador,
        )
        db.add(unidade)

    unidade.bloco = mapped_row.get("bloco")
    unidade.numero = mapped_row.get("numero") or identificador
    unidade.fracao_ideal = mapped_row.get("fracao_ideal")
    unidade.ativo = mapped_row.get("ativo", True)
    db.flush()
    return unidade


def _upsert_morador(db: Session, condominio_id: UUID, mapped_row: dict[str, Any]) -> Morador:
    identificador = mapped_row["identificador_externo"]
    unidade = db.scalar(
        select(Unidade).where(
            Unidade.condominio_id == condominio_id,
            Unidade.identificador_externo == identificador,
        )
    )
    if unidade is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unidade '{identificador}' not found for condominio.",
        )
    if unidade.condominio_id != condominio_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unidade does not belong to the provided condominio.",
        )

    morador = _find_existing_morador(db, unidade.id, mapped_row)
    if morador is None:
        morador = Morador(
            condominio_id=condominio_id,
            unidade_id=unidade.id,
            nome=mapped_row["nome"],
            tipo=mapped_row["tipo"],
        )
        db.add(morador)

    morador.condominio_id = condominio_id
    morador.unidade_id = unidade.id
    morador.nome = mapped_row["nome"]
    morador.cpf = mapped_row.get("cpf")
    morador.telefone = mapped_row.get("telefone")
    morador.email = mapped_row.get("email")
    morador.tipo = mapped_row["tipo"]
    morador.ativo = mapped_row.get("ativo", True)
    db.flush()
    return morador


def _find_existing_morador(db: Session, unidade_id: UUID, mapped_row: dict[str, Any]) -> Morador | None:
    cpf = mapped_row.get("cpf")
    email = mapped_row.get("email")
    nome = mapped_row["nome"]

    if cpf:
        morador = db.scalar(
            select(Morador).where(
                Morador.unidade_id == unidade_id,
                Morador.cpf == cpf,
            )
        )
        if morador is not None:
            return morador

    if email:
        morador = db.scalar(
            select(Morador).where(
                Morador.unidade_id == unidade_id,
                func.lower(Morador.email) == email.lower(),
            )
        )
        if morador is not None:
            return morador

    return db.scalar(
        select(Morador).where(
            Morador.unidade_id == unidade_id,
            func.lower(Morador.nome) == nome.lower(),
        )
    )


def _build_error(index: int, messages: list[str], row: dict[str, Any]) -> dict[str, Any]:
    return {
        "linha": index,
        "mensagens": messages,
        "dados": row,
    }


def create_importacao_log(
    db: Session,
    condominio_id: UUID,
    tipo: str,
    arquivo_nome: str | None,
) -> Importacao:
    importacao = Importacao(
        condominio_id=condominio_id,
        tipo=tipo,
        arquivo_nome=arquivo_nome,
        status="processando",
        erros=[],
        quantidade_processada=0,
        quantidade_sucesso=0,
    )
    db.add(importacao)
    db.commit()
    db.refresh(importacao)
    return importacao


def finalize_importacao_log(
    db: Session,
    importacao: Importacao,
    processados: int,
    sucessos: int,
    erros: list[dict[str, Any]],
) -> ImportResult:
    result = ImportResult(
        importacao=importacao,
        processados=processados,
        sucessos=sucessos,
        erros=erros,
    )
    importacao.quantidade_processada = processados
    importacao.quantidade_sucesso = sucessos
    importacao.status = result.status
    importacao.erros = erros
    db.add(importacao)
    db.commit()
    db.refresh(importacao)
    return result


