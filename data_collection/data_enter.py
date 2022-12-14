import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from g_sheets.g_api import get_google_client
from g_sheets.gspread import get_client, get_first_empty_row
from gspread import Client

# logger
from data_collection.actions import data_logger


# module with specific data inputs
# gspread
def add_cu_daily_row(client: Client, cu_date: str, cu_bid: float, cu_offer: float, cu_stock: int):
    try:
        sh = client.open(os.environ['DATA_SHEET'])
        sheet = sh.worksheet("Cu")

        empty_row = get_first_empty_row(sheet)
        last_row_date = sheet.row_values(empty_row - 1)[0]

        if last_row_date == cu_date:
            data_logger.info('Same day! No rows edited.')
            return

        sheet.append_row([cu_date, cu_bid, cu_offer, cu_stock], empty_row)

        return sheet.range(f'A{last_row_date}:C{last_row_date}')

    except HttpError as error:
        return error


# google api
def batch_update_table(values: list):
    creds = get_google_client(os.environ["DATA_KEYF_NAME"])

    try:
        service = build('sheets', 'v4', credentials=creds)
        body = {"values": values}

        result = service.spreadsheets().values().append(
            spreadsheetId=os.environ['SPREADSHEET_DATA'],
            valueInputOption='USER_ENTERED',
            body=body,
            range="copperwm!A2:D2"
        ).execute()
        return result
    except HttpError as error:
        data_logger.warn(f"An error occurred {error.error_details}")
        return error
