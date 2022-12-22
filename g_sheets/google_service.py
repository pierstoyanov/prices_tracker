from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from g_sheets.google_api_operations import goog_logger


def build_google_service(service_acc_file):
    scopes = ['https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive']
    try:
        creds = Credentials.from_service_account_file(
            filename=service_acc_file,
            scopes=scopes
        )

        service = build('sheets', 'v4', credentials=creds,
                        cache_discovery=False)

        return service

    except HttpError as error:
        goog_logger.error(f'An error occurred: {error}')
        return error
