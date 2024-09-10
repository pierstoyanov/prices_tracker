import os
from firebase_rt_db.firebase_serivce import start_firebase
from google_sheets.google_service import GoogleService
import firebase_admin

class StorageManagerSingleton:
    """ Singleton for providing storage connection services. """   
    def __init__(self, storage_strategy=0):
        """ Storage strategy:
            0 - firebase
            1 - gsheets
            2 - both (default)"""
        # Storage [firebase, gsheets, both]
        self.storage_strategy = storage_strategy
        # google api service instance for using sheets
        # self.service = GoogleService.build_default_google_service()
        self.sheets_service = GoogleService.build_google_sheets_service("./service-account.json")
        

    def get_storage_strategy(self):
        """ Storage strategy:
            0 - firebase
            1 - gsheets
            2 - both """
        return self.storage_strategy

    def get_sheets_service(self):
        return self.sheets_service
    
    # def build_firebase(self):
    #     firebase_admin.initialize_app(creds, {
    #         'databaseURL': os.environ.get('FIREBASE_URL')
    #     })

    # def build_firebase_default_creds(self):
    #     firebase_admin.initialize_app(options={
    #         'databaseURL': os.environ.get('FIREBASE_URL')
    #     })

    @staticmethod
    def start_firebase(): # firebase
        start_firebase()


# Storage manger instance
storage_manager = StorageManagerSingleton(2)
