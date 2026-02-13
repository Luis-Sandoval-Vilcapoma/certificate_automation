import os
import pandas as pd
from pathlib import Path
from docx.shared import Cm
from datetime import datetime
from docx2pdf import convert
from docxtpl import DocxTemplate, InlineImage
from Drive.drive_uploader import upload_pdf_to_drive
from Transform.transform import transform_format_month

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "Template"


def clean_text(text):
    """
    Limpia texto para usarlo en nombre de archivos
    """
    return str(text).replace("/", "-").replace("\\", "-").strip()


def generate_certificate(row: pd.Series, correlativo):
    """Genera  certificado en formato Word y PDF"""
    # Selecciona el tipo de fomato dependiendo si va a tener fecha de vencimiento
    if str(row["VENCIMIENTO"]).lower() == "si":
        template_path = TEMPLATE_DIR / "formato_con_fecha_de_vencimiento.docx"
    else:
        template_path = TEMPLATE_DIR / "formato_de_certificado.docx"

    # Verifica que exista la carpeta output y sen caso de que no exista la crea
    output_dir = BASE_DIR / "output"
    output_dir.mkdir(exist_ok=True)
    output_year = BASE_DIR / "output" / f"{row['fecha_de_emision'].year}"
    output_year.mkdir(exist_ok=True)

    store_name = clean_text(row["RAZON SOCIAL"])

    # Lee el fomato y carga las variables que estan en el formato
    doc = DocxTemplate(template_path)

    # Se le asigna el valor a cada variable del formato
    context = {
        # 🔢 Encabezado
        "correlativo": correlativo,
        # 🏢 Datos del cliente
        "razon_social": f'{row["RAZON SOCIAL"]}',
        "direccion": row["DIRECCION"],
        "giro": row["GIRO"],
        "area": row["AREA TRATADA"],
        # 🧪 Servicio (clave para los IF del Word)
        "servicio": row["SERVICIO"],
        # 📅 Fechas
        "fecha_de_servicio": row["fecha_de_servicio"],
        "fecha_de_emision": row["fecha_de_emision"].strftime(
            f"%d de {transform_format_month(row['fecha_de_emision'].month)} del %Y"
        ),
    }
    if str(row["VENCIMIENTO"]).lower() == "si":
        context["fecha_de_vencimiento"] = row["fecha_de_vencimiento"].strftime(
            "%d.%m.%Y"
        )

    doc.render(context)

    # Nombre del archivo del certrificado
    docx_path = (
        output_year
        / f"CERTIFICADO N°{correlativo} - {store_name} - {context['servicio']} - {transform_format_month(row['fecha_de_emision'].month)}.docx"
    )

    # Guarda el documento generado
    doc.save(docx_path)

    # Convierte el documento a PDF
    pdf_path = docx_path.with_suffix(".pdf")
    convert(str(docx_path), str(pdf_path))

    doc.render(context)
    doc.save(docx_path)

    convert(str(docx_path), str(pdf_path))

    return pdf_path
