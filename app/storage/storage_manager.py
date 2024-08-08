from firebase_rt_db.firebase_serivce import start_firebase
from google_sheets.google_service import GoogleService

class StorageManagerSingleton:
    """ Singleton for providing storage connection services. """   
    def __init__(self, storage_strategy=0):
        """ Storage strategy:
            0 - firebase
            1 - gsheets
            2 - both (default)"""

        # google api service instance for using sheets
        # self.service = GoogleService.build_default_google_service()
        self.service = GoogleService.build_google_service("./service-account.json")
        # Storage [firebase, gsheets, both]
        self.storage_strategy = storage_strategy

    def get_storage_strategy(self):
        """ Storage strategy:
            0 - firebase
            1 - gsheets
            2 - both"""
        return self.storage_strategy

    def get_sheets_service(self):
        return self.service
    
    @staticmethod
    def start_firebase(): # firebase
        start_firebase()


# Storage manger instance
storage_manager = StorageManagerSingleton(2)
