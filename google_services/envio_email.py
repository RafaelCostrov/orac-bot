import os
import base64
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json


load_dotenv()
info = os.getenv('SERVICE_ACCOUNT_FILE')
creds_json = json.loads(info)
SCOPES = os.getenv('SCOPES_EMAIL').split(',')
EMAIL_USER = os.getenv('EMAIL_USER')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "email", "extratos.html")

credentials = service_account.Credentials.from_service_account_info(
    creds_json, scopes=SCOPES, subject=EMAIL_USER)
service = build('gmail', 'v1', credentials=credentials)


def carregar_template(link):
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as file:
        template = file.read()
        return template.replace("{{extrato}}", link)


def criar_email(destinatario, assunto, link):
    email = MIMEMultipart()
    email['to'] = destinatario
    email['from'] = EMAIL_USER
    email['subject'] = assunto
    email.attach(MIMEText(carregar_template(link), 'html'))

    raw_message = base64.urlsafe_b64encode(email.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


def enviar(destinatario, assunto, link):
    email = criar_email(destinatario, assunto, link)
    service.users().messages().send(
        userId='me',
        body=email
    ).execute()

    return destinatario
