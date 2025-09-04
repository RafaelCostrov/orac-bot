import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

load_dotenv()


def acessando_drive():
    info = os.getenv('SERVICE_ACCOUNT_FILE')
    creds_json = json.loads(info)
    EMAIL_USER = os.getenv('EMAIL_USER')
    SCOPES = os.getenv('SCOPES_DRIVE').split(',')
    creds = service_account.Credentials.from_service_account_info(
        creds_json, scopes=SCOPES, subject=EMAIL_USER)
    drive_service = build("drive", "v3", credentials=creds)
    return drive_service
