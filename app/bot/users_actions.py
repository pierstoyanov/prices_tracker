import os
from googleapiclient.errors import HttpError
from google_sheets.google_sheets_api_operations import find_row_of_item_in_sheet, delete_row
from storage.storage_manager import storage_manager

# logger
from logger.logger import logging
user_actions = logging.getLogger(__name__)

spreadsheet_id = os.environ.get('SPREADSHEET_USERS')
if spreadsheet_id is None:
    raise ValueError("users sheet id is not set")
sheets_service = storage_manager.get_sheets_service()

def get_users_id(service=sheets_service):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='C2:C'
        ).execute()
        user_actions.info("Retrieved user id data")
        if not result.get('values'):
            user_actions.info('No users found')
            return []
        else:
            user_actions.info("Returning list of subs.")
            return [item for sublist in result.get('values') for item in sublist]
    except HttpError as error:
        user_actions.error("An error occurred: %s", error)
        return error


def add_new_user(new_user, service=sheets_service):
    users = get_users_id()
    vals = [[str(x) for x in new_user.__dict__.values()]]
    if len(users) == 0 or new_user.id not in users:
        body = {
            'values': vals
        }
        try:
            result = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id,
                                                            valueInputOption="USER_ENTERED",
                                                            range="A1:L1",
                                                            body=body).execute()
            user_actions.info("User %s with id %s added.", new_user.name, new_user.id)
            return True
        except HttpError as error:
            user_actions.error("An error occurred: %s", error)
            return False
    else:
        user_actions.info('User already exists')
        return False


def remove_user(u_id, s=sheets_service):
    """Function to remove user by id from sheet.
    :returns: bool"""
    user_row = find_row_of_item_in_sheet(
        item=u_id, col="C", service=s, spreadsheet_id=spreadsheet_id)

    if user_row:
        try:
            delete_row(row_to_delete=user_row,
                       service=s,
                       spreadsheet_id=spreadsheet_id)
            user_actions.info('Removed user with id %s at row %s', u_id, user_row)
            return True
        except HttpError as error:
            user_actions.error("An error occurred: %s", error)
            return False

    user_actions.info('User with id %s not found in sheet', u_id)
    return False
