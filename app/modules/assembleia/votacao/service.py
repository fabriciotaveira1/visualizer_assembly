from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.usuarios.auth.models import User
from app.modules.condominio.condominio.service import get_condominio_by_id
from app.modules.sistema.integracoes.importador.models import Importacao
from app.modules.sistema.integracoes.importador.service import (
    create_importacao_log,
    finalize_importacao_log,
    read_csv_upload,
)
from app.modules.sistema.integracoes.importador.csv_votos import parse_csv_votos
from app.modules.sistema.integracoes.importador.voto_mapper import map_voto_row
from app.modules.sistema.integracoes.importador.voto_validator import validate_voto_import_row
from app.modules.condominio.unidade.models import Unidade
from app.modules.assembleia.votacao.models import Assembleia, OpcaoVotacao, Pauta, ResultadoManual, Voto
from app.modules.assembleia.votacao.schemas import (
    OpcaoVotacaoCreate,
    ResultadoManualCreate,
    ResultadoPautaOpcao,
    ResultadoPautaResponse,
    VotoCreate,
)


def create_opcao_votacao(db: Session, pauta_id: UUID, payload: OpcaoVotacaoCreate) -> OpcaoVotacao:
    pauta = get_pauta_by_id(db, pauta_id)
    _ensure_pauta_not_closed(pauta)

    existing = db.scalar(
        select(OpcaoVotacao).where(
            OpcaoVotacao.pauta_id == pauta_id,
            OpcaoVotacao.codigo == payload.codigo,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Option code already exists for this pauta.",
        )

    option = OpcaoVotacao(
        pauta_id=pauta_id,
        codigo=payload.codigo,
        descricao=payload.descricao,
    )
    db.add(option)
    db.commit()
    db.refresh(option)
    return option


def register_manual_vote(
    db: Session,
    payload: VotoCreate,
    current_user: User,
    client_ip: str | None,
) -> Voto:
    pauta = get_pauta_by_id(db, payload.pauta_id)
    condominio_id = get_pauta_condominio_id(db, pauta)
    unidade = _get_unidade_for_pauta(db, payload.unidade_id, condominio_id)

    _ensure_pauta_allows_individual_votes(db, pauta, expected_mode="manual")

    existing_vote = db.scalar(
        select(Voto).where(
            Voto.pauta_id == payload.pauta_id,
            Voto.unidade_id == payload.unidade_id,
        )
    )
    if existing_vote is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This unidade has already voted on this pauta.",
        )

    codigo_opcao, descricao_opcao = _resolve_vote_option(
        db,
        pauta.id,
        payload.codigo_opcao,
        payload.descricao_opcao,
    )

    peso = payload.peso if payload.peso is not None else _resolve_unidade_peso(unidade)
    vote = Voto(
        pauta_id=pauta.id,
        unidade_id=unidade.id,
        tipo_voto=payload.tipo_voto,
        tipo_origem="manual",
        codigo_opcao=codigo_opcao,
        descricao_opcao=descricao_opcao,
        voto=descricao_opcao,
        peso=peso,
        ip=client_ip,
        data_voto=datetime.now(UTC),
        registrado_por=current_user.id,
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote


async def import_votes_csv(
    db: Session,
    pauta_id: UUID,
    file: UploadFile,
    current_user: User,
) -> dict[str, Any]:
    pauta = get_pauta_by_id(db, pauta_id)
    condominio_id = get_pauta_condominio_id(db, pauta)
    _ensure_pauta_allows_individual_votes(db, pauta, expected_mode="importado")
    get_condominio_by_id(db, condominio_id)

    rows = parse_csv_votos(await read_csv_upload(file))
    importacao = create_importacao_log(db, condominio_id, "votos", file.filename)
    erros: list[dict[str, Any]] = []
    sucessos = 0
    seen_identificadores: set[str] = set()

    for index, row in enumerate(rows, start=1):
        mapped_row = map_voto_row(row)
        row_errors = validate_voto_import_row(mapped_row, seen_identificadores)
        unidade_key = (mapped_row.get("identificador_externo") or "").lower()
        if unidade_key:
            seen_identificadores.add(unidade_key)

        if row_errors:
            erros.append(_build_row_error(index, row_errors, row))
            continue

        try:
            _upsert_imported_vote(db, pauta, condominio_id, mapped_row, current_user)
            db.commit()
            sucessos += 1
        except HTTPException as exc:
            db.rollback()
            erros.append(_build_row_error(index, [str(exc.detail)], row))
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            erros.append(_build_row_error(index, [f"Unexpected error: {exc}"], row))

    finalize_importacao_log(db, importacao, len(rows), sucessos, erros)
    return {
        "importacao_id": str(importacao.id),
        "tipo": importacao.tipo,
        "arquivo_nome": importacao.arquivo_nome,
        "status": importacao.status,
        "quantidade_processada": importacao.quantidade_processada,
        "quantidade_sucesso": importacao.quantidade_sucesso,
        "quantidade_erros": len(erros),
        "erros": erros,
    }


def register_manual_result(
    db: Session,
    payload: ResultadoManualCreate,
) -> list[ResultadoManual]:
    pauta = get_pauta_by_id(db, payload.pauta_id)
    _ensure_pauta_in_votacao(pauta)
    if pauta.modo_votacao != "resultado_manual":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pauta is not configured for resultado_manual.",
        )
    if _pauta_has_votes(db, pauta.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot insert manual result when individual votes already exist.",
        )

    options_map = _get_options_map(db, pauta.id)

    db.execute(delete(ResultadoManual).where(ResultadoManual.pauta_id == pauta.id))
    resultados: list[ResultadoManual] = []
    for item in payload.resultados:
        descricao = _resolve_option_description(options_map, item.codigo_opcao, item.descricao_opcao)
        resultado = ResultadoManual(
            pauta_id=pauta.id,
            codigo_opcao=item.codigo_opcao,
            descricao_opcao=descricao,
            quantidade_votos=item.quantidade_votos,
            peso_total=item.peso_total,
            percentual=item.percentual,
        )
        db.add(resultado)
        resultados.append(resultado)

    db.commit()
    for resultado in resultados:
        db.refresh(resultado)
    return resultados


def get_resultado_pauta(db: Session, pauta_id: UUID) -> ResultadoPautaResponse:
    pauta = get_pauta_by_id(db, pauta_id)

    if pauta.modo_votacao == "resultado_manual":
        resultados = list(
            db.scalars(
                select(ResultadoManual)
                .where(ResultadoManual.pauta_id == pauta_id)
                .order_by(ResultadoManual.codigo_opcao.asc())
            ).all()
        )
        total_votos = sum(item.quantidade_votos for item in resultados)
        total_peso = sum((item.peso_total for item in resultados), start=Decimal("0"))
        opcoes = [
            ResultadoPautaOpcao(
                codigo_opcao=item.codigo_opcao,
                descricao_opcao=item.descricao_opcao,
                quantidade_votos=item.quantidade_votos,
                peso_total=item.peso_total,
                percentual=item.percentual,
            )
            for item in resultados
        ]
        return ResultadoPautaResponse(
            pauta_id=pauta.id,
            modo_votacao=pauta.modo_votacao,
            total_votos=total_votos,
            total_peso=total_peso,
            opcoes=opcoes,
        )

    rows = db.execute(
        select(
            Voto.codigo_opcao,
            Voto.descricao_opcao,
            func.count(Voto.id),
            func.coalesce(func.sum(Voto.peso), 0),
        )
        .where(Voto.pauta_id == pauta_id)
        .group_by(Voto.codigo_opcao, Voto.descricao_opcao)
        .order_by(Voto.codigo_opcao.asc())
    ).all()
    total_votos = sum(int(row[2]) for row in rows)
    total_peso = sum((Decimal(str(row[3])) for row in rows), start=Decimal("0"))
    opcoes: list[ResultadoPautaOpcao] = []
    for codigo, descricao, quantidade, peso_total in rows:
        peso_decimal = Decimal(str(peso_total))
        percentual = Decimal("0")
        if total_peso > 0:
            percentual = (peso_decimal / total_peso) * Decimal("100")
        elif total_votos > 0:
            percentual = (Decimal(int(quantidade)) / Decimal(total_votos)) * Decimal("100")
        opcoes.append(
            ResultadoPautaOpcao(
                codigo_opcao=int(codigo),
                descricao_opcao=str(descricao),
                quantidade_votos=int(quantidade),
                peso_total=peso_decimal,
                percentual=percentual.quantize(Decimal("0.01")),
            )
        )

    return ResultadoPautaResponse(
        pauta_id=pauta.id,
        modo_votacao=pauta.modo_votacao or "manual",
        total_votos=total_votos,
        total_peso=total_peso,
        opcoes=opcoes,
    )


def get_pauta_by_id(db: Session, pauta_id: UUID) -> Pauta:
    pauta = db.scalar(select(Pauta).where(Pauta.id == pauta_id))
    if pauta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pauta not found.")
    return pauta


def get_pauta_condominio_id(db: Session, pauta: Pauta) -> UUID:
    assembleia = db.scalar(select(Assembleia).where(Assembleia.id == pauta.assembleia_id))
    if assembleia is None or assembleia.condominio_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pauta is not linked to a valid condominio.",
        )
    return assembleia.condominio_id


def _ensure_pauta_not_closed(pauta: Pauta) -> None:
    if pauta.status == "encerrada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pauta is closed.",
        )


def _ensure_pauta_in_votacao(pauta: Pauta) -> None:
    if pauta.status != "em_votacao":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pauta is not in voting status.",
        )


def _ensure_pauta_allows_individual_votes(db: Session, pauta: Pauta, expected_mode: str) -> None:
    _ensure_pauta_in_votacao(pauta)
    if pauta.modo_votacao != expected_mode:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Pauta is not configured for {expected_mode}.",
        )
    if _pauta_has_manual_results(db, pauta.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pauta already has manual aggregated results.",
        )


def _get_unidade_for_pauta(db: Session, unidade_id: UUID, condominio_id: UUID) -> Unidade:
    unidade = db.scalar(select(Unidade).where(Unidade.id == unidade_id))
    if unidade is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade not found.")
    if unidade.condominio_id != condominio_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unidade does not belong to the pauta condominio.",
        )
    return unidade


def _resolve_vote_option(
    db: Session,
    pauta_id: UUID,
    codigo_opcao: int,
    descricao_opcao: str | None,
) -> tuple[int, str]:
    options_map = _get_options_map(db, pauta_id)
    descricao = _resolve_option_description(options_map, codigo_opcao, descricao_opcao)
    return codigo_opcao, descricao


def _resolve_option_description(
    options_map: dict[int, str],
    codigo_opcao: int,
    descricao_opcao: str | None,
) -> str:
    if codigo_opcao in options_map:
        return options_map[codigo_opcao]
    if descricao_opcao:
        return descricao_opcao
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="descricao_opcao is required when no option is configured for the given code.",
    )


def _get_options_map(db: Session, pauta_id: UUID) -> dict[int, str]:
    options = list(
        db.scalars(select(OpcaoVotacao).where(OpcaoVotacao.pauta_id == pauta_id)).all()
    )
    return {option.codigo: option.descricao for option in options}


def _resolve_unidade_peso(unidade: Unidade) -> Decimal:
    if unidade.fracao_ideal is None:
        return Decimal("1")
    peso = Decimal(str(unidade.fracao_ideal))
    return peso if peso > 0 else Decimal("1")


def _pauta_has_votes(db: Session, pauta_id: UUID) -> bool:
    return bool(db.scalar(select(func.count()).select_from(Voto).where(Voto.pauta_id == pauta_id)))


def _pauta_has_manual_results(db: Session, pauta_id: UUID) -> bool:
    return bool(
        db.scalar(
            select(func.count()).select_from(ResultadoManual).where(ResultadoManual.pauta_id == pauta_id)
        )
    )


def _upsert_imported_vote(
    db: Session,
    pauta: Pauta,
    condominio_id: UUID,
    mapped_row: dict[str, Any],
    current_user: User,
) -> Voto:
    unidade = db.scalar(
        select(Unidade).where(
            Unidade.condominio_id == condominio_id,
            Unidade.identificador_externo == mapped_row["identificador_externo"],
        )
    )
    if unidade is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unidade '{mapped_row['identificador_externo']}' not found for condominio.",
        )

    existing_vote = db.scalar(
        select(Voto).where(
            Voto.pauta_id == pauta.id,
            Voto.unidade_id == unidade.id,
        )
    )
    if existing_vote is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate vote for unidade '{mapped_row['identificador_externo']}'.",
        )

    codigo_opcao, descricao_opcao = _resolve_vote_option(
        db,
        pauta.id,
        mapped_row["codigo_opcao"],
        mapped_row.get("descricao_opcao"),
    )
    peso = mapped_row.get("peso")
    if peso is None:
        peso = _resolve_unidade_peso(unidade)

    voto = Voto(
        pauta_id=pauta.id,
        unidade_id=unidade.id,
        tipo_voto=mapped_row.get("tipo_voto") or "direto",
        tipo_origem="importado",
        codigo_opcao=codigo_opcao,
        descricao_opcao=descricao_opcao,
        voto=descricao_opcao,
        peso=peso,
        data_voto=datetime.now(UTC),
        registrado_por=current_user.id,
    )
    db.add(voto)
    db.flush()
    return voto


def _build_row_error(index: int, messages: list[str], row: dict[str, Any]) -> dict[str, Any]:
    return {"linha": index, "mensagens": messages, "dados": row}


