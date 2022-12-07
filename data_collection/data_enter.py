import os
import gspread

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials


def get_first_empty_row(s: gspread.spreadsheet.Spreadsheet.sheet1, cols_to_sample=2):
    cols = s.range(1, 1, s.row_count, cols_to_sample)
    return max([cell.row for cell in cols if cell.value]) + 1


# gspread
def get_client():
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(os.environ["KEYF_NAME"], scopes)
    return gspread.authorize(credentials)


def add_cu_daily_row(cu_date: str, cu_bid: float, cu_offer: float, cu_stock: int):
    try:
        client = get_client()
        sh = client.open(os.environ['SHEET_NAME'])
        sheet = sh.worksheet("Cu")

        empty_row = get_first_empty_row(sheet)
        last_row_date = sheet.row_values(empty_row - 1)[0]

        if last_row_date == cu_date:
            print("Same day! No rows edited.")
            return

        print(empty_row, cu_date, cu_bid, cu_offer)
        sheet.append_row([cu_date, cu_bid, cu_offer, cu_stock], empty_row)

        return sheet.range(f'A{last_row_date}:C{last_row_date}')

    except HttpError as error:
        return error


def create_avrg_formula(new_row: int):
    return f'=AVERAGE(B{new_row}:C{new_row})'


def add_daily_row(page: str, data: list, average=False):
    print(data)
    try:
        client = get_client()
        sheet = client.open(os.environ['SHEET_NAME']).worksheet(page)

        new_row = get_first_empty_row(sheet)
        last_row_date = sheet.row_values(new_row - 1)[0]

        if last_row_date == data[0]:
            print("Same day! No rows edited.")
            return

        if average:
            data = data + (create_avrg_formula(new_row),)

        # print(new_row, data)
        sheet.append_row(values=data,
                         value_input_option="USER_ENTERED")

        return sheet.range(f'A{new_row}:D{new_row}')

    except HttpError as error:
        return error


# google api
def get_google_client():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = None

    try:
        if os.path.exists(os.environ["KEYF_NAME"]):
            creds = service_account.Credentials.from_service_account_file(os.environ["KEYF_NAME"], scopes=SCOPES)
        return creds
    except HttpError as error:
        return error


def batch_update_table(values: list):
    creds = get_google_client()

    try:
        service = build('sheets', 'v4', credentials=creds)
        body = {"values": values}

        result = service.spreadsheets().values().append(
            spreadsheetId=os.environ['SPREADSHEET_ID'],
            valueInputOption='USER_ENTERED',
            body=body,
            range="copperwm!A2:D2"
        ).execute()
        return result
    except HttpError as error:
        # print(f"An error occurred {error}")
        return error
