import os
from typing import Callable

import requests
from gspread import Client

from data_collection.headers import lmba_headers, lme_headers
from data_collection.json_to_input import cu_jsons_to_input, au_json_to_input, \
    ag_json_to_input
from g_sheets.gspread import get_client, add_row_to_page
from logger.logger import logging

# create local log
data_logger = logging.getLogger('data_collection.act_requests')


def log_data(data, url):
    if data:
        data_logger.info(f'Gathered api data from {url}')
    else:
        data_logger.warning('No data')


def log_result(res):
    if res:
        data_logger.info(f'Added row: {res}')


def request_json_and_store(client: Client, urls: list, headers: dict, json_to_input_fn: Callable,
                           store_to_page: str, average_cols: str = None, ):
    """ Function to call requests to listed urls, execute data gathering fn on response
     and send the data to the store"""
    try:
        data = []
        for i in urls:
            response = requests.get(url=i, headers=headers)
            log_data(response, i)
            data.append(response.json())

        input_data = json_to_input_fn(data)

        result = add_row_to_page(client=client, page=store_to_page, data=input_data, average_cols=average_cols)
        log_result(result)

    except Exception as e:
        data_logger.info(f"Error occurred! {e}")
        return e


def data_management_with_requests():
    """Main fn that executes all data gather with requests"""
    # gspread client for data sheet
    client = get_client(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])

    # Cu
    request_json_and_store(
        client=client,
        urls=[os.environ.get('CU_JSON_URL'), os.environ.get('CU_JSON_STOCK')],
        headers=lme_headers,
        json_to_input_fn=cu_jsons_to_input,
        store_to_page='copper',
    )
    # TODO
    # Westmetal
    # request_json_and_store(
    #     client=client,
    #     urls=[os.environ.get('CU_JSON_URL'), os.environ.get('CU_JSON_STOCK')],
    #     headers=lme_headers,
    #     json_to_input_fn=cu_jsons_to_input,
    #     store_to_page='copperwm',
    # )

    # Au
    request_json_and_store(
        client=client,
        urls=[os.environ.get('AU_AM_JSON'), os.environ.get('AU_PM_JSON')],
        headers=lmba_headers,
        json_to_input_fn=au_json_to_input,
        store_to_page='gold',
        average_cols='B:C'
    )

    # Ag
    request_json_and_store(
        client=client,
        urls=[os.environ.get('AG_JSON')],
        headers=lmba_headers,
        json_to_input_fn=ag_json_to_input,
        store_to_page='silver'
    )


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data_management_with_requests()
