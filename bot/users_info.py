import os
from googleapiclient.errors import HttpError
from bot.bot import bot_logger, sheets_service
from g_sheets.google_api_operations import find_row_of_item_in_sheet, delete_row

spreadsheet_id = os.environ['SPREADSHEET_USERS']


def get_users_id(service=sheets_service):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='A:A'
        ).execute()
        bot_logger.info("Retrieved user id data")
        return result.get('values', [])

    except HttpError as error:
        bot_logger.error(f"An error occurred: {error}")
        return error


def add_new_user(new_user, service=sheets_service):
    users = get_users_id()
    vals = [[str(x) for x in new_user.__dict__.values()]]
    if new_user.id not in users:
        body = {
            'values': vals
        }
        try:
            service.spreadsheets().values().append(spreadsheetId=spreadsheet_id,
                                                   valueInputOption="USER_ENTERED",
                                                   range="A1:L1",
                                                   body=body).execute()
            bot_logger.info(f"User {new_user.name} with id {new_user.id} added.")
        except HttpError as error:
            bot_logger.error(f"An error occurred: {error}")
            return error
    else:
        bot_logger.info('User already exists')


def remove_user(u_id, s=sheets_service):
    user_row = find_row_of_item_in_sheet(
        item=u_id, col="C", service=s, spreadsheet_id=spreadsheet_id)
    print(user_row)
    if user_row:
        result = delete_row(row_to_delete=user_row,
                            service=s,
                            spreadsheet_id=spreadsheet_id)
        bot_logger.info(f'Removed user with id{u_id} at row {user_row}')
