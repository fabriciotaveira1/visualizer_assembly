from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.presenca.models import Presenca
from app.presenca.service import get_assembleia_by_id, get_quorum
from app.procuracao.models import Procuracao
from app.relatorios.schemas import (
    AtaAutomaticaResponse,
    PresencaAtaItem,
    RelatorioAnaliticoResponse,
    RelatorioOpcaoItem,
    RelatorioPautaAnalitico,
    RelatorioResumoPauta,
    RelatorioSinteticoResponse,
    RelatorioVotoItem,
)
from app.unidade.models import Unidade
from app.votacao.models import Pauta, ResultadoManual, Voto
from app.votacao.service import get_resultado_pauta


def get_relatorio_sintetico(db: Session, assembleia_id: UUID) -> RelatorioSinteticoResponse:
    assembleia = get_assembleia_by_id(db, assembleia_id)
    analitico = get_relatorio_analitico(db, assembleia_id)
    pautas_resumo: list[RelatorioResumoPauta] = []
    for pauta in analitico.pautas:
        vencedor = max(
            pauta.opcoes,
            key=lambda item: (item.percentual, item.peso_total, item.quantidade_votos),
            default=None,
        )
        pautas_resumo.append(
            RelatorioResumoPauta(
                pauta_id=pauta.pauta_id,
                titulo=pauta.titulo,
                modo_votacao=pauta.modo_votacao,
                opcao_vencedora=vencedor.descricao_opcao if vencedor else None,
                percentual_vencedor=vencedor.percentual if vencedor else Decimal("0"),
            )
        )

    return RelatorioSinteticoResponse(
        assembleia_id=assembleia.id,
        titulo=assembleia.titulo,
        data=assembleia.data,
        total_unidades=analitico.total_unidades,
        total_presentes=analitico.total_presentes,
        total_representados=analitico.total_representados,
        quorum_percentual_presenca=analitico.quorum_percentual_presenca,
        quorum_percentual_fracao_ideal=analitico.quorum_percentual_fracao_ideal,
        pautas=pautas_resumo,
    )


def get_relatorio_analitico(db: Session, assembleia_id: UUID) -> RelatorioAnaliticoResponse:
    assembleia = get_assembleia_by_id(db, assembleia_id)
    quorum = get_quorum(db, assembleia_id)

    presencas = list(
        db.execute(
            select(Presenca, Unidade)
            .join(Unidade, Unidade.id == Presenca.unidade_id)
            .where(Presenca.assembleia_id == assembleia_id)
            .order_by(Unidade.bloco.asc(), Unidade.numero.asc(), Unidade.identificador_externo.asc())
        ).all()
    )
    presencas_items = [
        PresencaAtaItem(
            unidade_id=unidade.id,
            identificador_externo=unidade.identificador_externo,
            bloco=unidade.bloco,
            numero=unidade.numero,
            tipo_presenca=presenca.tipo or "presente",
        )
        for presenca, unidade in presencas
        if unidade.id is not None
    ]

    pautas = list(
        db.scalars(
            select(Pauta)
            .where(Pauta.assembleia_id == assembleia_id)
            .order_by(Pauta.ordem.asc(), Pauta.created_at.asc())
        ).all()
    )
    pautas_items = [_build_pauta_analitica(db, pauta) for pauta in pautas]

    return RelatorioAnaliticoResponse(
        assembleia_id=assembleia.id,
        titulo=assembleia.titulo,
        data=assembleia.data,
        status=assembleia.status,
        quorum_percentual_presenca=quorum.percentual_presenca,
        quorum_percentual_fracao_ideal=quorum.percentual_fracao_ideal,
        total_unidades=quorum.total_unidades,
        total_presentes=quorum.total_presentes,
        total_representados=quorum.total_presentes + quorum.total_por_procuracao,
        pautas=pautas_items,
        presencas=presencas_items,
    )


def generate_ata_automatica(db: Session, assembleia_id: UUID) -> AtaAutomaticaResponse:
    analitico = get_relatorio_analitico(db, assembleia_id)
    linhas: list[str] = []
    linhas.append(f"As {analitico.data} realizou-se a assembleia \"{analitico.titulo or '-'}\".")
    linhas.append(
        "Foram registradas "
        f"{analitico.total_presentes} presencas fisicas e "
        f"{analitico.total_representados - analitico.total_presentes} representacoes por procuracao, "
        f"atingindo quorum de {analitico.quorum_percentual_presenca}% das unidades "
        f"e {analitico.quorum_percentual_fracao_ideal}% da fracao ideal."
    )

    if analitico.presencas:
        presencas_texto = ", ".join(
            f"{item.identificador_externo} ({item.tipo_presenca})" for item in analitico.presencas
        )
        linhas.append(f"Lista de presenca: {presencas_texto}.")

    for pauta in analitico.pautas:
        linhas.append(f"Pauta: {pauta.titulo or '-'}")
        if pauta.opcoes:
            partes = []
            for opcao in pauta.opcoes:
                partes.append(
                    f"{opcao.descricao_opcao}: {opcao.quantidade_votos} votos, "
                    f"peso {opcao.peso_total}, {opcao.percentual}%"
                )
            linhas.append("Resultado: " + "; ".join(partes) + ".")
        else:
            linhas.append("Resultado: sem registros de voto.")

    return AtaAutomaticaResponse(
        assembleia_id=analitico.assembleia_id,
        titulo=analitico.titulo,
        data=analitico.data,
        texto="\n\n".join(linhas),
    )


def _build_pauta_analitica(db: Session, pauta: Pauta) -> RelatorioPautaAnalitico:
    resultado = get_resultado_pauta(db, pauta.id)
    opcoes = [
        RelatorioOpcaoItem(
            codigo_opcao=item.codigo_opcao,
            descricao_opcao=item.descricao_opcao,
            quantidade_votos=item.quantidade_votos,
            peso_total=item.peso_total,
            percentual=item.percentual,
        )
        for item in resultado.opcoes
    ]

    if pauta.modo_votacao == "resultado_manual":
        votos = [
            RelatorioVotoItem(
                unidade_id=None,
                identificador_externo=None,
                bloco=None,
                numero=None,
                codigo_opcao=item.codigo_opcao,
                descricao_opcao=item.descricao_opcao,
                tipo_voto=None,
                tipo_origem="resultado_manual",
                peso=item.peso_total,
                data_voto=item.created_at,
            )
            for item in db.scalars(
                select(ResultadoManual)
                .where(ResultadoManual.pauta_id == pauta.id)
                .order_by(ResultadoManual.codigo_opcao.asc())
            ).all()
        ]
        return RelatorioPautaAnalitico(
            pauta_id=pauta.id,
            titulo=pauta.titulo,
            descricao=pauta.descricao,
            status=pauta.status,
            modo_votacao=pauta.modo_votacao,
            opcoes=opcoes,
            votos=votos,
            usa_resultado_manual=True,
        )

    rows = db.execute(
        select(Voto, Unidade)
        .join(Unidade, Unidade.id == Voto.unidade_id)
        .where(Voto.pauta_id == pauta.id)
        .order_by(Unidade.bloco.asc(), Unidade.numero.asc(), Unidade.identificador_externo.asc())
    ).all()
    votos = [
        RelatorioVotoItem(
            unidade_id=unidade.id,
            identificador_externo=unidade.identificador_externo,
            bloco=unidade.bloco,
            numero=unidade.numero,
            codigo_opcao=voto.codigo_opcao,
            descricao_opcao=voto.descricao_opcao,
            tipo_voto=voto.tipo_voto,
            tipo_origem=voto.tipo_origem,
            peso=voto.peso,
            data_voto=voto.data_voto,
        )
        for voto, unidade in rows
    ]
    return RelatorioPautaAnalitico(
        pauta_id=pauta.id,
        titulo=pauta.titulo,
        descricao=pauta.descricao,
        status=pauta.status,
        modo_votacao=pauta.modo_votacao,
        opcoes=opcoes,
        votos=votos,
        usa_resultado_manual=False,
    )
