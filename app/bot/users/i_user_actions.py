from abc import ABC, abstractmethod
from typing import List


class UserActions(ABC):
    """Strategy interface for user actions."""	
    @abstractmethod
    def get_all_user_ids(self):
        pass

    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int):
        pass
    
    @abstractmethod
    def add_new_user(self, key: str, user: dict) -> None:
        pass

    @abstractmethod
    def update_user(self, key:str, user: dict) -> None:
        pass
    
    @abstractmethod
    def remove_user(self, user_id: int) -> None:
        pass
