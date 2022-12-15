import os
from googleapiclient.errors import HttpError

# logger
from logger.logger import logging
goog_logger = logging.getLogger(__name__)


# google api
def append_values(service, spreadsheet_id, range_name, value_input_option, values):
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


def get_values(service, spreadsheet_id, range_name):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        rows = result.get('values', [])
        print(f"{len(rows)} rows retrieved")
        return result

    except HttpError as error:
        goog_logger.error(f'An error occurred {error}')
        return error


def batch_update_table(service, values: list, page: str,
                       start_col: str, end_col: str, start_row=2):
    """"Add multiple rows to table"""
    try:
        body = {"values": values}
        result = service.spreadsheets().values().append(
            spreadsheetId=os.environ['SPREADSHEET_DATA'],
            valueInputOption='USER_ENTERED',
            body=body,
            range=f"{page}!{start_col}{start_row}:{end_col}{start_row}"
        ).execute()
        return result

    except HttpError as error:
        goog_logger.warning(f"An error occurred {error.error_details}")
        return error
