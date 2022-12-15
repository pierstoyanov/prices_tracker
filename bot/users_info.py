import os
from googleapiclient.errors import HttpError
from bot.bot import bot_logger, sheets_service

sheet = os.environ['SPREADSHEET_USERS']


def get_users_id():
    try:
        result = sheets_service.values().get(
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
        body = {
            'values': new_user
        }

        try:
            sheets_service.values().append(spreadsheetId=sheet,
                                           valueInputOption="USER_ENTERED",
                                           range="A1:L1",
                                           body=body)
            bot_logger.info(f"User {new_user.name} with id {new_user.id} added.")
        except HttpError as error:
            bot_logger.error(f"An error occurred: {error}")
            return error
    else:
        bot_logger.info('User already exists')
