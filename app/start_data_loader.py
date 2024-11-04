from firebase_admin import db
from data_unit import DataUnit
from storage.storage_manager import storage_manager


class StartDataLoader:
    def __init__(self):
        self.start = db.reference('start').get()
        self.user_map = self.set_user_map()
        self.last_data = self.set_last_data()
    
    def set_user_map(self):
        return self.start.get('user_map')
    
    def set_last_data(self):
        du = DataUnit()

        if storage_manager.get_storage_strategy() == 1:
            du.fill_last_data_from_gsheets()
            return du
        
        du.fill_last_from_firebase(self.start.get('last'))
        return du
