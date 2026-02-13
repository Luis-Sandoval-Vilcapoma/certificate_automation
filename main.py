import warnings
import pandas as pd
from pathlib import Path
from datetime import datetime

from Extract.extract import extract_data
from Transform.transform import transform_data
from Load.load import generate_certificate

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

BASE_DIR = Path(__file__).resolve().parent
CURRENT_YEAR = datetime.now().year


def main():
    # 1️⃣ Extraer datos
    df = extract_data()
    df = transform_data(df)

    correlative_path = BASE_DIR / "correlative.xlsx"

    for _, row in df.iterrows():

        # 2️⃣ Calcular correlativo
        if correlative_path.exists():
            df_corr = pd.read_excel(correlative_path)
            next_number = len(df_corr) + 1
        else:
            next_number = 1

        year = row["date_of_service_final"].year
        serial_number = f"{str(next_number).zfill(3)}-{year}"

        # 3️⃣ Generar certificado (sin QR)
        certificate = generate_certificate(
            row=row,
            correlativo=serial_number,
        )

        print(f"✅ Generated: {certificate}")

        # 4️⃣ Registrar correlativo
        new_row = {
            "correlative": serial_number,
            "month_of_service": row["date_of_service_final"].month,
            "date_of_service": row["date_of_service_final"],
            "service": row["SERVICIO"],
        }

        if correlative_path.exists():
            df_corr = pd.read_excel(correlative_path)
            df_corr = pd.concat([df_corr, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df_corr = pd.DataFrame([new_row])

        df_corr.to_excel(correlative_path, index=False)


if __name__ == "__main__":
    main()
