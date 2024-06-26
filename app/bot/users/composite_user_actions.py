# class using composite design pattern for strategy in i_user_actions

from viberbot.api.user_profile import UserProfile
from bot.users.firebasee_user_actions import FirebaseUserActions
from bot.users.google_sheets_user_actions import GoogleSheetsUserActions
from bot.users.i_user_actions import UserActions


class CompositeUserActions(UserActions):
    """ This class uses composite design pattern to command the storage strategy instances. """

    def __init__(self, storage_strategy):
        self.storage: str = storage_strategy
        self.managers: list = self.set_storage(storage_strategy)

    def set_storage(self, storage_strategy) -> list:
        """ Create user actions managers based on storage strategy."""
        # first item in list is the primary storage.
        managers = [] # 0=firebase, 1=gsheets
        if storage_strategy == 'firebase' or storage_strategy == 'both':
            managers.append(FirebaseUserActions())
        if storage_strategy == 'gsheets' or storage_strategy == 'both':
            managers.append(GoogleSheetsUserActions())
        return managers

    def get_all_user_ids(self) -> list[str]:
        # method uses only primary storage source 
        return self.managers[0].get_all_user_ids()
    
    def get_all_users(self) -> dict | None:
        # method uses only primary storage source 
        return self.managers[0].get_all_users()

    def get_user_by_id(self, user_id: str) -> dict | None:
        # method uses only primary storage source 
        return self.managers[0].get_user_by_id(user_id)
    
    def add_new_user(self, user: UserProfile) -> bool:
        success = True
        try:
            for manager in self.managers:
                manager.add_new_user(user.id, user)
        except:
            success = False
        return success

    def update_user(self, user_id:str, update_data: dict) -> None:
        """ Update user in all storage sources. """	
        for manager in self.managers:
            try:
                manager.update_user(user_id, update_data)
            except: 
                continue

    def remove_user(self, user_id: str) -> None:
        """ Remove user from all storage sources. """  
        for manager in self.managers:
            try:
                manager.remove_user(user_id)
            except Exception as e: 
                continue
