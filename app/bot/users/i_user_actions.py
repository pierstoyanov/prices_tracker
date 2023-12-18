from abc import ABC, abstractmethod
from typing import List


class UserAction(ABC):
    @abstractmethod
    def get_all_user_id(self):
        # returntype tbd
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int):
        # returntype tbd
        pass
    
    @abstractmethod
    def add_new_user(self, user: dict) -> None:
        pass

    @abstractmethod
    def update_user(self, user: dict) -> None:
        pass
    
    @abstractmethod
    def remove_user(self, user_id: int) -> None:
        pass
