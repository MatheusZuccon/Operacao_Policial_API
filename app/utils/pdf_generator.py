from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from app.constants.operation_types import OPERATION_TYPE_LABELS


def generate_operation_pdf(operation) -> BytesIO:
    """Generate a PDF report for the given operation and return it as a BytesIO buffer."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Title styles ──────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#16213e"),
        spaceBefore=14,
        spaceAfter=6,
        borderPad=4,
    )
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        leading=16,
        alignment=TA_LEFT,
    )
    label_style = ParagraphStyle(
        "LabelStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        leading=14,
    )

    # ── Header ────────────────────────────────────────────────────────────────
    elements.append(Paragraph("RELATÓRIO DE OPERAÇÃO POLICIAL", title_style))
    elements.append(Paragraph("Police Operation API — Documento Oficial", subtitle_style))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e")))
    elements.append(Spacer(1, 0.4 * cm))

    # ── Basic information table ───────────────────────────────────────────────
    operation_type_label = OPERATION_TYPE_LABELS.get(operation.operation_type, operation.operation_type)
    info_data = [
        ["ID da Operação", str(operation.id)],
        ["Nome", operation.name],
        ["Tipo", operation_type_label],
        ["Localização", operation.location],
        [
            "Data de Criação",
            operation.created_at.strftime("%d/%m/%Y %H:%M") if operation.created_at else "—",
        ],
    ]
    info_table = Table(info_data, colWidths=[5 * cm, 12 * cm])
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eaf6")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1a1a2e")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ]
        )
    )
    elements.append(info_table)

    # ── Description ───────────────────────────────────────────────────────────
    if operation.description:
        elements.append(Paragraph("Descrição", section_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#aaaaaa")))
        elements.append(Spacer(1, 0.2 * cm))
        elements.append(Paragraph(operation.description, body_style))

    # ── Weapons ───────────────────────────────────────────────────────────────
    elements.append(Paragraph("Armamentos", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#aaaaaa")))
    elements.append(Spacer(1, 0.2 * cm))
    if operation.weapons:
        weapon_names = [w.name.capitalize() for w in operation.weapons]
        for i, name in enumerate(weapon_names, start=1):
            elements.append(Paragraph(f"  {i}. {name}", body_style))
    else:
        elements.append(Paragraph("Nenhum armamento registrado.", label_style))

    # ── Vehicles ──────────────────────────────────────────────────────────────
    elements.append(Paragraph("Viaturas", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#aaaaaa")))
    elements.append(Spacer(1, 0.2 * cm))
    if operation.vehicles:
        vehicle_data = [["#", "Nome", "Blindada"]]
        for i, v in enumerate(operation.vehicles, start=1):
            vehicle_data.append([str(i), v.name, "Sim" if v.armored else "Não"])
        vehicle_table = Table(vehicle_data, colWidths=[1.5 * cm, 10 * cm, 5.5 * cm])
        vehicle_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("PADDING", (0, 0), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f5f5f5")],
                    ),
                ]
            )
        )
        elements.append(vehicle_table)
    else:
        elements.append(Paragraph("Nenhuma viatura registrada.", label_style))

    # ── Roles ─────────────────────────────────────────────────────────────────
    elements.append(Paragraph("Cargos / Funções", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#aaaaaa")))
    elements.append(Spacer(1, 0.2 * cm))
    if operation.roles:
        for i, role in enumerate(operation.roles, start=1):
            elements.append(Paragraph(f"  {i}. {role.name.capitalize()}", body_style))
    else:
        elements.append(Paragraph("Nenhum cargo registrado.", label_style))

    # ── Investigation Equipments ───────────────────────────────────────────────
    elements.append(Paragraph("Equipamentos Investigativos", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#aaaaaa")))
    elements.append(Spacer(1, 0.2 * cm))
    if operation.investigation_equipments:
        for i, eq in enumerate(operation.investigation_equipments, start=1):
            elements.append(Paragraph(f"  {i}. {eq.name.capitalize()}", body_style))
    else:
        elements.append(Paragraph("Nenhum equipamento investigativo registrado.", label_style))

    # ── Footer ────────────────────────────────────────────────────────────────
    elements.append(Spacer(1, 0.6 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a1a2e")))
    elements.append(
        Paragraph(
            "Documento gerado automaticamente pelo sistema Police Operation API.",
            ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=8,
                textColor=colors.HexColor("#888888"),
                alignment=TA_CENTER,
                spaceBefore=6,
            ),
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer
