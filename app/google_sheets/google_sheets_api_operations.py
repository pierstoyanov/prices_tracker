import os
from typing import Literal
from googleapiclient.errors import HttpError

# logger
from logger.logger import logging
goog_logger = logging.getLogger(__name__)

# Literals for string params in google sheets api
ValueInputOptionLiterals = Literal['RAW', 'USER_ENTERED']
ValueRenderOptionLiterals = Literal['FORMATTED_VALUE', 'UNFORMATTED_VALUE', 'FORMULA']
DateTimeRenderOptionLiterals = Literal['SERIAL_NUMBER', 'FORMATTED_STRING']
InsertDataOptionLiterals = Literal['OVERWRITE', 'INSERT_ROWS']


def http_error_handler(func):
    """"Wrapper to handle HttpError from Google api client errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as error:
            goog_logger.error('Goog client HTTP error occurred %s',
                              error.error_details)
            return error

    return wrapper


# google api
@http_error_handler
def append_values(service, spreadsheet_id: str, range_name: str,
                  value_input_option: ValueInputOptionLiterals,
                  values: list,
                  insert_data_option: InsertDataOptionLiterals = 'INSERT_ROWS'):
    """ Append values in to the last row of a named range in spreadsheet"""
    body = {'values': values}
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption=value_input_option,
        insertDataOption=insert_data_option,
        body=body).execute()

    u = result.get('updatedCells')
    updated = u if u is not None else result.get('updates').get('updatedCells')

    goog_logger.info("%s cells updated.", updated)

    return result


# @http_error_handler
# def get_values(service, spreadsheet_id: str, range_name):
#     result = service.spreadsheets().values().get(
#         spreadsheetId=spreadsheet_id, range=range_name).execute()
#     rows = result.get('values', [])
#     print(f"{len(rows)} rows retrieved")
#
#     return result


@http_error_handler
def batch_update_table(service, values: list, page: str,
                       start_col: str, end_col: str, start_row: int = 2):
    """"Add multiple rows to page in a table"""
    body = {"values": values}
    result = service.spreadsheets().values().append(
        spreadsheetId=os.environ.get('SPREADSHEET_DATA'),
        valueInputOption='USER_ENTERED',
        body=body,
        range=f"{page}!{start_col}{start_row}:{end_col}{start_row}"
    ).execute()

    return result


@http_error_handler
def find_row_of_item_in_sheet(service, item: str, col: str, spreadsheet_id: str,
                              data_sheet='data', query_sheet='query'):
    """Return row number of item in sheet, if item is not in sheet return None."""
    value_input_option: ValueInputOptionLiterals = 'USER_ENTERED'
    range_name = f'{query_sheet}!A1:B1'
    values = [
        [f"=MATCH(B1;{data_sheet}!{col}1:{col};0)", item]
    ]

    # add search formula to sheet
    search_formula_update = update_values_in_sheet(
        service=service, spreadsheet_id=spreadsheet_id, range_name=range_name,
        value_input_option=value_input_option, values=values)

    if not isinstance(search_formula_update, HttpError):
        goog_logger.info('Added search formula in %s cells.',
                         search_formula_update.get("updatedCells"))

    # get row num from formula
    result = get_values_from_sheet(service=service,
                                   spreadsheet_id=spreadsheet_id,
                                   range_name=f'{query_sheet}!A1',
                                   value_render_option='UNFORMATTED_VALUE',
                                   date_time_render_option='SERIAL_NUMBER')

    result_value = result['values'][0][0]

    return result_value if isinstance(result_value, int) else None


@http_error_handler
def get_values_from_sheet(service, spreadsheet_id: str,
                          range_name: str,
                          value_render_option: ValueRenderOptionLiterals,
                          date_time_render_option: DateTimeRenderOptionLiterals):
    """Return values from named range in sheet"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueRenderOption=value_render_option,
        dateTimeRenderOption=date_time_render_option).execute()
    goog_logger.info("%s cells extracted.", result.get('values'))

    return result


@http_error_handler
def get_last_row_num(service, spreadsheet_id: str,
                     sheet_name: str,
                     value_input_option: ValueInputOptionLiterals = "USER_ENTERED",
                     start_col: str = 'A', end_col: str = 'D', ):
    """Return last row number in named sheet from spreadsheet"""
    # append empty row
    values = []
    result = append_values(
        service=service,
        spreadsheet_id=spreadsheet_id,
        range_name=f'{sheet_name}!{start_col}:{end_col}',
        value_input_option=value_input_option,
        values=values)
    goog_logger.info("added empty row to table %s.", sheet_name)

    # get last row num from result
    end_range = result.get('tableRange').split(':')[1]

    return int(''.join([n for n in end_range if n.isdigit()]))


@http_error_handler
def get_last_row_values(service, spreadsheet_id: str,
                        sheet_name: str,
                        value_input_option: ValueInputOptionLiterals = "USER_ENTERED",
                        start_col: str = 'A', end_col: str = 'D', ):
    """Return values from last row in named sheet from spreadsheet"""

    last_row: int = get_last_row_num(service=service,
                                     spreadsheet_id=spreadsheet_id,
                                     value_input_option=value_input_option,
                                     sheet_name=sheet_name)
    # get last row data
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!{start_col}{last_row}:{end_col}{last_row}'
    ).execute()

    return result


@http_error_handler
def get_multiple_named_ranges(service, spreadsheet_id: str | None, named_ranges: list,
                              value_render_option: ValueRenderOptionLiterals,
                              date_time_render_option: DateTimeRenderOptionLiterals):
    result = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=named_ranges,
        valueRenderOption=value_render_option,
        dateTimeRenderOption=date_time_render_option).execute()
    goog_logger.info('Extracted multiple ranges.')

    return result


@http_error_handler
def update_values_in_sheet(service, values: list, spreadsheet_id: str,
                           range_name: str,
                           value_input_option: ValueInputOptionLiterals):

    body = {'values': values}

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption=value_input_option,
        body=body).execute()
    goog_logger.info("%s cells updated.", result.get('updatedCells'))

    return result


@http_error_handler
def delete_row(service, spreadsheet_id: str, row_to_delete: int, sheet_id: int = 0):
    """Delete row from page (ref by number - sheer_id) in spreadsheet."""
    request_body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": row_to_delete - 1,
                        "endIndex": row_to_delete
                    }
                }
            }
        ]
    }

    result = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request_body
    ).execute()
    goog_logger.info("removed row %s.", row_to_delete)

    return result
