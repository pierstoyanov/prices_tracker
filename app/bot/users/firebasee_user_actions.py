from firebase_admin import db
from logger.logger import logging
from bot.users.i_user_actions import UserActions
from firebase_rt_db.firebase_api_operations import push_data, add_key, \
    find_key_by_value, get_all_keys, get_all_values, get_key, remove_key, update_key


class FirebaseUserActions(UserActions):
    frb_logger = logging.getLogger(__name__)    

    def __init__(self):
        self.users = db.reference('users')
        self.id_map = db.reference('start/user_map')
        self.rev_id_map = {v: k for k, v in self.id_map.get().items()} \
            if self.id_map.get() is not None else {}

    def update_mapping(self):
        self.rev_id_map = {v: k for k, v in self.id_map.get().items()} \
            if self.id_map.get() is not None else {}

    def get_all_user_ids(self) -> list[str]:
        return get_all_values(self.id_map)

    def get_all_users(self) -> dict | None:
        return get_all_keys(self.users)

    def get_user_by_id(self, user_id: str) -> dict | None:
        if user_id not in self.rev_id_map.keys():
            raise Exception("User not found")
        
        frb_id = self.rev_id_map.get(user_id)
        return get_key(self.users, frb_id)

    def add_new_user(self, user) -> bool:
        if user.id in self.rev_id_map.keys():
            raise Exception("User already exists")
        
        key_data = {"api_version": user.api_version,
                    "avatar": user.avatar,
                    "id": user.id,
                    "name": user.name,
                    "language": user.language,
                    "country": user.country,
                    "lastSeen":"",
                    "lastDelivered": ""}

        try: 
            frb_id = push_data(self.id_map, user.id).key
            add_key(self.users, frb_id, key_data)
            self.update_mapping()
        except Exception as e:
            self.frb_logger.error(e)
        return True

    def update_user(self, user_id: str, update_data: dict) -> bool:
        frb_id = self.rev_id_map.get(user_id)
    
        if frb_id is None:
            raise Exception("User not found")

        try:    
            update_key(self.users, frb_id, update_data)
            return True
        except: 
            return False

    def remove_user(self, user_id: str) -> bool:
        frb_id = self.rev_id_map.get(user_id)

        if frb_id is None:
            raise Exception("User not found")

        try:
            remove_key(self.id_map, frb_id)
            remove_key(self.users, frb_id)
            self.update_mapping()
            return True
        except:
            return False