import os
from googleapiclient.errors import HttpError
from bot.bot import bot_logger, service
from g_sheets.g_api import append_values

sheet = os.environ['SPREADSHEET_USERS']


def get_users_id():
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


def add_new_user(new_user):
    users = get_users_id()
    if new_user.id not in users:
        try:
            append_values(spreadsheet_id=sheet,
                          range_name="A1:E1",
                          values=new_user)
            bot_logger.info(f"User {new_user.name} with id {new_user.id} added.")
        except HttpError as error:
            bot_logger.error(f"An error occurred: {error}")
            return error
    else:
        bot_logger.info('User already exists')
