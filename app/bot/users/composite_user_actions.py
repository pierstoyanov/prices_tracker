# class using composite design pattern for strategy in i_user_actions

from numpy import False_
from bot.users.firebasee_user_actions import FirebaseUserActions
from bot.users.google_sheets_user_actions import GoogleSheetsUserActions
from bot.users.i_user_actions import UserActions


class CompositeUserActions(UserActions):
    """ This class uses composite design pattern to command the storage strategy instances. """

    def __init__(self, storage_strategy, start_usr_map):
        self.storage: str = storage_strategy
        self.managers: list[UserActions] = self.set_storage(storage_strategy, start_usr_map)

    def set_storage(self, storage_strategy, start_usr_map) -> list:
        """ Create user actions managers based on storage strategy."""
        # first item in list is the primary storage.
        managers = [] # 0=firebase, 1=gsheets 2=both
        if storage_strategy == 0 or storage_strategy == 2:
            managers.append(FirebaseUserActions(start_usr_map))
        if storage_strategy == 1 or storage_strategy == 2:
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
    
    def apply_to_managers(self, operation, *args, **kwargs) -> bool:
        """
        Template method that applies a given operation to all managers.
        
        :param operation: A method or function to call for each manager.
        :return: True if the operation succeeds for all managers, False otherwise.
        """
        success_counter = 0
        
        for manager in self.managers:
            success_counter += operation(manager, *args, **kwargs)
        
        return success_counter == len(self.managers)
    
    def add_new_user(self, user) -> bool:
        return self.apply_to_managers(
            lambda mngr, usr: mngr.add_new_user(usr),
            user)

    def update_user(self, user_id:str, update_data: dict):
        """ Update user in all storage sources. """	
        success = True
        for manager in self.managers:
            try:
                manager.update_user(user_id, update_data)
            except: 
                success = False
                continue
        return success

    def remove_user(self, user_id: str) -> bool:
        """ Remove user from all storage sources. """ 
        return self.apply_to_managers(
            lambda manager, usr_id: manager.remove_user(usr_id), 
            user_id
        )
