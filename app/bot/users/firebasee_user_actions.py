from typing import List
from firebase_admin import db
from app.firebase_rt_db.firebase_api_operations import add_key, get_all_keys,\
    get_all_keys_no_data, get_key, remove_key, update_key

class FirebaseUserActions():
    def __init__(self):
        self.ref = db.reference('users')

    def get_all_user_ids(self) -> dict | None:
        return get_all_keys_no_data(self.ref)

    def get_all_users(self) -> dict | None:
        return get_all_keys(self.ref)
    
    def get_user_by_id(self, user_id: str) -> dict | None:
        return get_key(self.ref, user_id)

    def add_new_user(self, key:str, user: dict) -> None:
        add_key(self.ref, key, user)

    def update_user(self, key: str, update_data: dict) -> None:
        update_key(self.ref, key, update_data)    

    def remove_user(self, user_id: int) -> None:
        remove_key(self.ref, user_id)
    