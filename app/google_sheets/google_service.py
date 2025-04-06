from google import auth
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from logger.logger import logging
goog_logger = logging.getLogger(__name__)

class GoogleService:
    @staticmethod
    def build_google_sheets_service(service_account_file = None):
        """Build google service for sheets. Use service account keyfile if provided."""
        scopes = ['https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive']
        
        # fill credentials data
        if not service_account_file:
            creds, project_id = auth.default(scopes=scopes)
        else:
            creds = Credentials.from_service_account_file(
                filename=service_account_file,
                scopes=scopes
            )
        
        try:            
            service = build('sheets', 'v4', credentials=creds,
                            cache_discovery=False)

            return service

        except HttpError as error:
            goog_logger.error('An error occurred: %s', error.error_details)
            raise error
