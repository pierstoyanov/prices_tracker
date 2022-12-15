import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from logger.logger import logging
# from main import service

goog_logger = logging.getLogger(__name__)


# google api
def append_values(creds, spreadsheet_id, range_name, value_input_option, values):
    try:
        body = {
            'values': values
        }
        result = service.spreadsheets().values().apend(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result

    except HttpError as error:
        goog_logger.error(f'An error occurred {error}')
        return error


def get_values(creds, spreadsheet_id, range_name):
    try:
        service = build('sheets', 'v4', credentials=creds)

        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        rows = result.get('values', [])
        print(f"{len(rows)} rows retrieved")
        return result

    except HttpError as error:
        goog_logger.error(f'An error occurred {error}')
        return error
