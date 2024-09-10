from viberbot.api.user_profile import UserProfile
from abc import ABC, abstractmethod
from typing import List, Optional


class UserActions(ABC):
    """Strategy interface for user actions."""	
    @abstractmethod
    def get_all_user_ids(self) -> List:
        pass

    @abstractmethod
    def get_all_users(self) -> dict | None:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> dict | None:
        pass
    
    @abstractmethod
    def add_new_user(self, user: UserProfile) -> bool:
        pass

    @abstractmethod
    def update_user(self, user_id:str, update_data: dict) -> bool:
        pass
    
    @abstractmethod
    def remove_user(self, user_id: str) -> bool:
        pass
