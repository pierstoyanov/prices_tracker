import os

from g_sheets.g_api import get_google_client, get_values, append_values

creds = get_google_client(os.environ['LOG_KEYF_NAME'])
sheet = os.environ['SPREADSHEET_USERS']

# TODO
def get_users():
    # users = get_values(creds, sheet).get('values', range_name='A:A')
    # return users

    pass

def add_new_user(values):
    append_values(creds, sheet, values=values)
