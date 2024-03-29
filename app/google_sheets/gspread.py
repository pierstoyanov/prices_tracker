# import os
# from gspread import spreadsheet, Client, GSpreadException, service_account
# from logger.logger import logging
#
# gspread_logger = logging.getLogger(__name__)
#
#
# # gspread
# def get_client(key_file):
#     """"
#     :return: authorized gspread client from service account
#     """
#     return service_account(key_file)
#
#
# def get_first_empty_row(s: spreadsheet.Spreadsheet.sheet1,
#                         cols_to_sample=2) -> int:
#     """":return: number of the first empty row of gspread sheet"""
#     cols = s.range(1, 1, s.row_count, cols_to_sample)
#     return max([cell.row for cell in cols if cell.value]) + 1
#
#
# def add_row_to_page(client: Client, page: str, data: tuple, average_cols: object = None) -> object:
#     """Using gspread client and page name adds data to next empty row.
#         Average appends str formula for avrg between cols of the input data
#         cols should be separated by ':'"""
#
#     def average_cols_formula(row_number: int) -> tuple:
#         """":return: Formula for average between cols of n-th row"""
#         start_col, end_col = average_cols.split(':')
#         return f'=AVERAGE({start_col}{row_number}:{end_col}{row_number})',
#
#     try:
#         sheet = client.open(os.environ['DATA_SHEET']).worksheet(page)
#         gspread_logger.info('Sheet: %s', sheet)
#         new_row = get_first_empty_row(sheet)
#         last_row_date = sheet.row_values(new_row - 1)[0]
#
#         if last_row_date == data[0]:
#             gspread_logger.error("Same day! No rows edited.")
#             return
#
#         if average_cols:
#             data = data + (average_cols_formula(new_row))
#
#         # print(new_row, data)
#         sheet.append_row(values=data,
#                          value_input_option="USER_ENTERED")
#
#         return sheet.range(f'A{new_row}:D{new_row}')
#
#     except GSpreadException as error:
#         gspread_logger.error(error)
#         return error
#
#
# def get_named_range_gspread(client: Client, r: str):
#     """Using gspread return a single named range"""
#     try:
#         sheet = client.open(os.environ['DATA_SHEET'])
#         result = sheet.named_range(r)
#         return result
#     except GSpreadException as error:
#         gspread_logger.error(error)
#         return error
#
