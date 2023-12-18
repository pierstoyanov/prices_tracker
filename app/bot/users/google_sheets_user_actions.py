import os
from .i_user_actions import UserActions
from googleapiclient.errors import HttpError
from bot.bot import bot_logger, sheets_service
from google_sheets.google_sheets_api_operations import find_row_of_item_in_sheet, delete_row


class GoogleSheetsUserActions(UserActions):
    def __init__(self, sheets_service):
        self.spreadsheet_id = os.environ.get('SPREADSHEET_USERS')
        self.service = sheets_service


    def get_all_user_id(self):
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='C2:C'
            ).execute()
            bot_logger.info("Retrieved user id data")
            if not result.get('values'):
                bot_logger.info('No users found')
                return []
            else:
                bot_logger.info("Returning list of subs.")
                return [item for sublist in result.get('values') for item in sublist]
        except HttpError as error:
            bot_logger.error("An error occurred: %s", error)
            return error


    def get_user_by_id(self, user_id: int):
        # returntype tbd
        pass


    def add_new_user(self, user: dict) -> None:
        users = self.get_all_user_id()
        vals = [[str(x) for x in new_user.__dict__.values()]]
        if len(users) == 0 or new_user.id not in users:
            body = {
                'values': vals
            }
            try:
                result = service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    valueInputOption="USER_ENTERED",
                    range="A1:L1",
                    body=body).execute()
                bot_logger.info("User %s with id %s added.", new_user.name, new_user.id)
                return True
            except HttpError as error:
                bot_logger.error("An error occurred: %s", error)
                return False
        else:
            bot_logger.info('User already exists')
            return False


    def update_user(self, user: dict) -> None:
        pass


    def remove_user(self, user_id: str) -> None:
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
                bot_logger.info('Removed user with id %s at row %s', user_id, user_row)
                return True
            except HttpError as error:
                bot_logger.error("An error occurred: %s", error)
                return False

        bot_logger.info('User with id %s not found in sheet', user_id)
        return False

