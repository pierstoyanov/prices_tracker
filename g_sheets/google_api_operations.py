import os
from typing import Literal

from googleapiclient.errors import HttpError

# logger
from logger.logger import logging

goog_logger = logging.getLogger(__name__)

# literals for string params in goog api
ValueInputOptionLiterals = Literal['RAW', 'USER_ENTERED']
ValueRenderOptionLiterals = Literal['FORMATTED_VALUE', 'UNFORMATTED_VALUE', 'FORMULA']
DateTimeRenderOptionLiterals = Literal['SERIAL_NUMBER', 'FORMATTED_STRING']
InsertDataOptionLiterals = Literal['OVERWRITE', 'INSERT_ROWS']


# google api
def append_values(service, spreadsheet_id: str, range_name: str,
                  value_input_option: ValueInputOptionLiterals,
                  values: list,
                  insert_data_option: InsertDataOptionLiterals = 'INSERT_ROWS',
                  sheet_id: int = 0):
    try:
        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result

    except HttpError as error:
        goog_logger.error(f'An error occurred {error}')
        return error


# def get_values(service, spreadsheet_id: str, range_name):
#     try:
#         result = service.spreadsheets().values().get(
#             spreadsheetId=spreadsheet_id, range=range_name).execute()
#         rows = result.get('values', [])
#         print(f"{len(rows)} rows retrieved")
#         return result
#
#     except HttpError as error:
#         goog_logger.error(f'An error occurred {error}')
#         return error


def batch_update_table(service, values: list, page: str,
                       start_col: str, end_col: str, start_row: int = 2):
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


def find_row_of_item_in_sheet(item: str, col: str, service, spreadsheet_id: str,
                              data_sheet='data', query_sheet='query'):
    try:
        value_input_option: ValueInputOptionLiterals = 'USER_ENTERED'
        range_name = f'{query_sheet}!A1:B1'
        values = [
            [f"=MATCH(B1;{data_sheet}!{col}1:{col};0)", item]
        ]

        # add search formula to sheet
        search_formula_update = update_values_in_sheet(
            service=service, spreadsheet_id=spreadsheet_id, range_name=range_name,
            value_input_option=value_input_option, values=values)

        goog_logger.info(f'Added search formula in {search_formula_update.get("updatedCells")} cells.')

        # get row num from formula
        result = get_values_from_sheet(service=service, spreadsheet_id=spreadsheet_id,
                                       range_name=f'{query_sheet}!A1',
                                       value_render_option='UNFORMATTED_VALUE',
                                       date_time_render_option='SERIAL_NUMBER')

        result_value = result['values'][0][0]
        return result_value if isinstance(result_value, int) else None
    except HttpError as error:
        goog_logger.warning(f"An error occurred {error.error_details}")
        return error


def get_values_from_sheet(service, spreadsheet_id: str,
                          range_name: str,
                          value_render_option: ValueRenderOptionLiterals,
                          date_time_render_option: DateTimeRenderOptionLiterals):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueRenderOption=value_render_option,
            dateTimeRenderOption=date_time_render_option).execute()
        goog_logger.info(f"{result.get('updatedCells')} cells extracted.")
        return result
    except HttpError as error:
        goog_logger.warning(f"An error occurred {error.error_details}")
        return error


def get_last_row_num(service, spreadsheet_id: str,
                     sheet_name: str,
                     value_input_option: ValueInputOptionLiterals = "USER_ENTERED",
                     sheet_id: int = 0,
                     start_col: str = 'A', end_col: str = 'D', ):
    # append empty row
    try:
        values = []
        result = append_values(
            service=service, spreadsheet_id=spreadsheet_id,
            range_name=f'{sheet_name}!{start_col}:{end_col}',
            value_input_option=value_input_option,
            values=values,
            sheet_id=sheet_id)
        goog_logger.info(f"added empty row to table {sheet_name}.")

        # get last row num from result
        end_range = result.get('tableRange').split(':')[1]
        return int(''.join([n for n in end_range if n.isdigit()]))
    except HttpError as error:
        goog_logger.warning(f"An error occurred {error.error_details}")
        return error


def get_last_row_values(service, spreadsheet_id: str,
                        sheet_name: str,
                        value_input_option: ValueInputOptionLiterals = "USER_ENTERED",
                        sheet_id: int = 0,
                        start_col: str = 'A', end_col: str = 'D', ):
    last_row: int = get_last_row_num(service=service, spreadsheet_id=spreadsheet_id,
                                     value_input_option=value_input_option,
                                     sheet_id=sheet_id)
    # get last row data
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}!{start_col}{last_row}:{end_col}{last_row}'
        ).execute()
        return result
    except HttpError as error:
        goog_logger.warning(f"ERR: {error.error_details}")
        return error


def get_multiple_named_ranges(service, spreadsheet_id: str, named_ranges: list,
                              value_render_option: ValueRenderOptionLiterals,
                              date_time_render_option: DateTimeRenderOptionLiterals):
    try:
        result = service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=named_ranges,
            valueRenderOption=value_render_option,
            dateTimeRenderOption=date_time_render_option).execute()
        goog_logger.info(f'successfully extracted data: {result.get("valueRanges")}')
        return result
    except HttpError as error:
        goog_logger.warning(f"Error: {error.error_details}")
        return error


def update_values_in_sheet(service, values: list, spreadsheet_id: str,
                           range_name: str, value_input_option: ValueInputOptionLiterals):
    try:
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option,
            body=body).execute()
        goog_logger.info(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        goog_logger.warning(f"An error occurred {error.error_details}")
        return error


def delete_row(service, spreadsheet_id: str,
               row_to_delete: int, sheet_id: int = 0):
    request_body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": row_to_delete,
                        "endIndex": row_to_delete + 1
                    }
                }
            }
        ]
    }

    try:
        result = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()
        goog_logger.info(f"removed row {row_to_delete}.")
        return result
    except HttpError as error:
        goog_logger.error(f"An error occurred: {error}")
        return error
