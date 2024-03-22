from firebase_rt_db.firebase_serivce import start_firebase
from google_sheets.google_service import GoogleService


class StorageManager:
    
    def __init__(self):
        # google api service instance for using sheets
        # self.service = GoogleService.build_default_google_service()
        self.service = GoogleService.build_google_service("./service-account.json")

    @staticmethod
    def firebase(): # firebase
        start_firebase()
    
    def get_sheets_service(self):
        return self.service


# Storage manger instance
storage_manager = StorageManager()
