from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

from database import CAPTURES_DIR


REPORTS_DIR = CAPTURES_DIR.parent / "informes"
REPORTS_DIR.mkdir(exist_ok=True)


def generar_pdf(patient_id, values, capture_paths):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"informe_{patient_id}_{stamp}.pdf"
    document = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=36, leftMargin=36)
    styles = getSampleStyleSheet()
    story = [Paragraph("Informe de Termografia Medica", styles["Title"]), Spacer(1, 16)]
    rows = [
        ["Cedula / CURP", values.get("cedula", "")],
        ["Paciente", values.get("nombre_completo", "")],
        ["Edad", values.get("edad") or ""],
        ["Diagnostico", values.get("diagnostico_dx", "")],
        ["Observaciones", values.get("observaciones", "")],
        ["Fecha", datetime.now().strftime("%Y-%m-%d %H:%M")],
    ]
    table = Table(rows, colWidths=[120, 390])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e0f2fe")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))
    story.append(Paragraph("Capturas asociadas: " + ", ".join(capture_paths) if capture_paths else "Sin capturas", styles["BodyText"]))
    document.build(story)
    return path
