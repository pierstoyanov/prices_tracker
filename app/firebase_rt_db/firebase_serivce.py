import json
import os
import firebase_admin
from firebase_admin import credentials, db

# logger
from logger.logger import logging
firebase_logger = logging.getLogger(__name__)

def start_firebase():
    """ launches firebase connection """
    try: 
        key = json.loads(os.environ.get('FIREBASE'))
        creds = credentials.Certificate(key)
        firebase_admin.initialize_app(creds, {
            'databaseURL': os.environ.get('FIREBASE_URL')
        })
    except Exception as e:
        firebase_logger.error(f"Error: {e}")