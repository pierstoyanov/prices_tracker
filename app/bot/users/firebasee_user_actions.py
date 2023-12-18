from typing import List
from firebase_admin import credentials, db

class FirebaseUserAction():
    def __init__(self):
        self.ref = db.reference('users')
    

    def get_all_user_id(self):
        # returntype tbd
        pass


    def get_user_by_id(self, user_id: int):
        # returntype tbd
        pass
    

    def add_new_user(self, user: dict) -> None:
        pass


    def update_user(self, user: dict) -> None:
        pass
    

    def remove_user(self, user_id: int) -> None:
        pass
    