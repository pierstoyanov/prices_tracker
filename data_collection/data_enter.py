import os

from googleapiclient.errors import HttpError
from g_sheets.gspread import get_first_empty_row
from gspread import Client

# logger
from data_collection.act_playwright import data_logger


# module with specific data inputs
# gspread
def add_cu_daily_row(client: Client, cu_date: str, offer: float, three_m: float, stock: int):
    try:
        sheet = client.open(os.environ['DATA_SHEET']).worksheet("Cu")
        empty_row = get_first_empty_row(sheet)
        last_row_date = sheet.row_values(empty_row - 1)[0]

        if last_row_date == cu_date:
            data_logger.info('Same day! No rows edited.')
            return

        sheet.append_row([cu_date, offer, three_m, stock], empty_row)

        return sheet.range(f'A{last_row_date}:C{last_row_date}')

    except HttpError as error:
        return error
