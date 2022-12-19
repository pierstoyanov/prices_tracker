import os
from googleapiclient.errors import HttpError
from bot.bot import bot_logger, sheets_service
from g_sheets.g_api import find_row_of_item_in_sheet


sheet = os.environ['SPREADSHEET_USERS']


def get_users_id(service=sheets_service):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet,
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
            service.spreadsheets().values().append(spreadsheetId=sheet,
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
        item=u_id, col="C", service=s, spreadsheet_id=sheet)['values'][0][0]
    print(user_row)
    request_body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet,
                        "dimension": "ROWS",
                        "startIndex": user_row,
                        "endIndex": user_row + 1
                    }
                }
            }
        ]
    }

    try:
        result = s.spreadsheets().batchUpdate(
            spreadsheetId=sheet,
            body=request_body
        ).execute()
        bot_logger.info(f"removed with id {u_id} at row {user_row}.")
        return result
    except HttpError as error:
        bot_logger.error(f"An error occurred: {error}")
        return error
