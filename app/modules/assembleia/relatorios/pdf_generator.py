from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.modules.assembleia.relatorios.schemas import AtaAutomaticaResponse


def generate_ata_pdf(ata: AtaAutomaticaResponse) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Ata Automatica da Assembleia", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Assembleia: {ata.titulo or '-'}", styles["Heading2"]),
        Paragraph(f"Data: {ata.data or '-'}", styles["Normal"]),
        Spacer(1, 12),
    ]

    for paragraph in ata.texto.split("\n\n"):
        story.append(Paragraph(paragraph.replace("\n", "<br/>"), styles["Normal"]))
        story.append(Spacer(1, 10))

    document.build(story)
    return buffer.getvalue()


