from __future__ import annotations

import csv
from io import StringIO

from app.modules.assembleia.relatorios.schemas import RelatorioAnaliticoResponse


def export_votes_csv(report: RelatorioAnaliticoResponse) -> bytes:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "pauta_id",
            "pauta_titulo",
            "modo_votacao",
            "unidade_id",
            "identificador_externo",
            "bloco",
            "numero",
            "codigo_opcao",
            "descricao_opcao",
            "tipo_voto",
            "tipo_origem",
            "peso",
            "data_voto",
        ]
    )
    for pauta in report.pautas:
        for voto in pauta.votos:
            writer.writerow(
                [
                    pauta.pauta_id,
                    pauta.titulo,
                    pauta.modo_votacao,
                    voto.unidade_id,
                    voto.identificador_externo,
                    voto.bloco,
                    voto.numero,
                    voto.codigo_opcao,
                    voto.descricao_opcao,
                    voto.tipo_voto,
                    voto.tipo_origem,
                    voto.peso,
                    voto.data_voto,
                ]
            )
    return buffer.getvalue().encode("utf-8")


def export_presence_csv(report: RelatorioAnaliticoResponse) -> bytes:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["unidade_id", "identificador_externo", "bloco", "numero", "tipo_presenca"])
    for item in report.presencas:
        writer.writerow([item.unidade_id, item.identificador_externo, item.bloco, item.numero, item.tipo_presenca])
    return buffer.getvalue().encode("utf-8")


def export_results_csv(report: RelatorioAnaliticoResponse) -> bytes:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "pauta_id",
            "pauta_titulo",
            "modo_votacao",
            "codigo_opcao",
            "descricao_opcao",
            "quantidade_votos",
            "peso_total",
            "percentual",
        ]
    )
    for pauta in report.pautas:
        for opcao in pauta.opcoes:
            writer.writerow(
                [
                    pauta.pauta_id,
                    pauta.titulo,
                    pauta.modo_votacao,
                    opcao.codigo_opcao,
                    opcao.descricao_opcao,
                    opcao.quantidade_votos,
                    opcao.peso_total,
                    opcao.percentual,
                ]
            )
    return buffer.getvalue().encode("utf-8")


