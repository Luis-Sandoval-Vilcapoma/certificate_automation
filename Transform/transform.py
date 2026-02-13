import calendar
import pandas as pd
from datetime import datetime, timedelta


def expiration_date_moth(date):
    """Devuelve la fecha de vencimiento el ultimo dia del siguiente mes"""
    if pd.isna(date):
        return None

    year = date.year
    month = date.month + 1

    if month > 12:
        month = 1
        year += 1
    last_day = calendar.monthrange(year, month)[1]
    return datetime(year, month, last_day)


def expiration_date_30_days(date):
    """Devuelve la fecha de vencimiento 30 días después del servicio"""
    if pd.isna(date):
        return None

    return date + timedelta(days=30)


def expiration_date_semester(date):
    """Devuelve la fecha de vencimiento el ultimo dia del siguiente semestre"""
    if pd.isna(date):
        return None

    year = date.year
    month = date.month + 6

    if month > 12:
        month -= 12
        year += 1
    last_day = calendar.monthrange(year, month)[1]
    return datetime(year, month, last_day)


def format_service_dates_short(row):
    """
    Devuelve:
    - 20.01.26
    - 20.01.26 y 28.01.26
    """
    d1 = row["date_of_service_1"]
    d2 = row["date_of_service_2"]

    if pd.notna(d2):
        return f"{d1:%d.%m.%Y} y {d2:%d.%m.%Y}"
    else:
        return f"{d1:%d.%m.%Y}"


def transform_data(df):
    df = df.copy()

    # ✅ Convertir fechas
    df["date_of_service_1"] = pd.to_datetime(df["date_of_service_1"])
    df["date_of_service_2"] = pd.to_datetime(df["date_of_service_2"], errors="coerce")

    # ✅ Fecha para mostrar en certificado
    df["fecha_de_servicio"] = df.apply(
        format_service_dates_short, axis=1, result_type="reduce"
    )

    # ✅ Tomar la segunda fecha si existe, si no la primera
    df["date_of_service_final"] = df["date_of_service_2"].fillna(
        df["date_of_service_1"]
    )

    # ✅ Fecha de emisión basada en la fecha final
    df["fecha_de_emision"] = pd.Timestamp.today().date()

    # ✅ Columna vencimiento vacía
    df["fecha_de_vencimiento"] = pd.NaT

    # ✅ Filtrar solo certificados que expiran
    mask_expira = df["VENCIMIENTO"].astype(str).str.strip().str.lower() == "si"

    # ✅ Servicios semestrales
    mask_semester = df["SERVICIO"].isin(
        [
            "Limpieza y desinfección de reservorios de agua",
            "Limpieza de Tanque séptico",
            "Limpieza de Ambientes",
        ]
    )

    # ✅ Vencimiento semestral
    df.loc[mask_expira & mask_semester, "fecha_de_vencimiento"] = df.loc[
        mask_expira & mask_semester, "date_of_service_1"
    ].apply(expiration_date_semester)

    # ✅ Vencimiento mensual
    df.loc[mask_expira & ~mask_semester, "fecha_de_vencimiento"] = df.loc[
        mask_expira & ~mask_semester, "date_of_service_1"
    ].apply(expiration_date_moth)

    return df


def transform_format_month(month):
    months = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }
    return months.get(month, "Mes inválido")
