import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def extract_data():
    """
    Crea una tabla con los datos de los clientes que se solicita certificado
    """
    database = pd.read_excel(BASE_DIR / "Database" / "database.xlsx")
    request = pd.read_excel(BASE_DIR / "request.xlsx", dtype={"expiration_date": str})
    data = pd.merge(database, request, on="CODIGO")
    return data


extract_data()
