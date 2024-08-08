import os
from bot.users.i_user_actions import UserActions
from googleapiclient.errors import HttpError
from logger.logger import logging
from storage.storage_manager import storage_manager
from google_sheets.google_sheets_api_operations import \
    find_row_of_item_in_sheet, delete_row


class GoogleSheetsUserActions(UserActions):
    gsheets_logger = logging.getLogger(__name__)
    
    def __init__(self):
        self.spreadsheet_id = os.environ.get('SPREADSHEET_USERS')
        self.service = storage_manager.get_sheets_service()

    def get_all_user_ids(self):
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='C2:C'
            ).execute()
            self.gsheets_logger.info("Retrieved user id data")
            if not result.get('values'):
                self.gsheets_logger.info('No users found')
                return []
            else:
                self.gsheets_logger.info("Returning list of subs.")
                return [item for sublist in result.get('values') for item in sublist]
        except HttpError as error:
            self.gsheets_logger.error("An error occurred: %s", error)
        return []

    def get_all_users(self) -> list:
        # TODO test&fix
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='A2:H'
            ).execute()
            self.gsheets_logger.info("Retrieved user id data")
            if not result.get('values'):
                self.gsheets_logger.info('No users found')
                return []
            else:
                self.gsheets_logger.info("Returning list of subs.")
                return [item for sublist in result.get('values') for item in sublist]
        except HttpError as error:
            self.gsheets_logger.error("An error occurred: %s", error)
        return []

    def get_user_by_id(self, user_id: int):
        # returntype tbd
        pass

    def add_new_user(self, user: dict) -> bool:
        users = self.get_all_user_ids()
        vals = [[str(x) for x in user.__dict__.values()]]
        user_id = user.get('id')
        if len(users) == 0 or user_id not in users:
            body = {
                'values': vals
            }
            try:
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    valueInputOption="USER_ENTERED",
                    range="A1:L1",
                    body=body).execute()
                self.gsheets_logger.info("User with id %s added.", user_id)
                return True
            except HttpError as error:
                self.gsheets_logger.error("An error occurred: %s", error)
                return False
        else:
            self.gsheets_logger.info('User already exists')
            return False


    def update_user(self, user: dict) -> None:
        pass


    def remove_user(self, user_id: str) -> bool:
        """Function to remove user by id from sheet.
        :returns: bool"""
        user_row = find_row_of_item_in_sheet(
            item=user_id, col="C", 
            service=self.service, 
            spreadsheet_id=self.spreadsheet_id)

        if user_row:
            try:
                delete_row(row_to_delete=user_row,
                        service=self.service,
                        spreadsheet_id=self.spreadsheet_id)
                self.gsheets_logger.info('Removed user with id %s at row %s', user_id, user_row)
                return True
            except HttpError as error:
                self.gsheets_logger.error("An error occurred: %s", error)
                return False

        self.gsheets_logger.info('User with id %s not found in sheet', user_id)
        return False

