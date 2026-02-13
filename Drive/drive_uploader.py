import os
import pickle
from pathlib import Path
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/drive.file"]
BASE_DIR = Path(__file__).resolve().parent.parent
OAUTH_FILE = BASE_DIR / "Credentials" / "oauth_credentials.json"
TOKEN_FILE = BASE_DIR / "Credentials" / "token.pickle"


def upload_pdf_to_drive(pdf_path, folder_id):
    creds = None

    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                # 🔑 Token revocado → forzar OAuth completo
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(OAUTH_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": Path(pdf_path).name,
        "parents": [folder_id],
    }

    media = MediaFileUpload(pdf_path, mimetype="application/pdf")

    file = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id",
        )
        .execute()
    )

    file_id = file.get("id")

    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return f"https://drive.google.com/file/d/{file_id}/view"
