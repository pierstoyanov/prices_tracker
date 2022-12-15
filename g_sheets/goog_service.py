from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from g_sheets.g_api import goog_logger


def get_goog_service(service_acc_file):
    scopes = ['https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive']
    try:
        creds = Credentials.from_service_account_file(
            filename=service_acc_file,
            scopes=scopes
        )

        service = build('sheets', 'v4', credentials=creds)

        return service.spreadsheets()

    except HttpError as error:
        goog_logger.error(f'An error occurred: {error}')
        return error
