import os
from typing import Callable

import requests
from bs4 import BeautifulSoup
from gspread import Client

from data_collection.headers import lmba_headers, lme_headers, ua_header
from data_collection.json_to_input import cu_jsons_to_input, au_json_to_input, \
    ag_json_to_input
from data_collection.pandas_to_input import power_soup_to_data
from data_collection.soup_to_input import wm_soup_to_data, bnb_soup_to_data
from g_sheets.google_api_operations import append_values
from g_sheets.google_service import build_google_service
from g_sheets.gspread import get_client, add_row_to_page
from logger.logger import logging

# create local log
data_logger = logging.getLogger('data_collection.act_requests')


def log_data(data, url):
    if data:
        data_logger.info(f'Gathered api data from {url}')
    else:
        data_logger.warning('No data')


def request_to_pandas_store(service, sh_id: str, url: str, headers: dict,
                            to_data_fn: Callable, store_to_page: str, average_cols: str = None):
    """ Call requests url, send content to pandas df, store with store_fn and google sheets api"""
    try:
        response = requests.get(url, headers=headers)
        log_data(response.status_code, url)

        if response.status_code != 200:
            raise Exception("Bad request")

        input_data = to_data_fn(response, service, sh_id)

        if len(input_data) <= 0:
            raise Exception('No data collected')

        result = append_values(
            service=service,
            range_name='power!A2:D',
            spreadsheet_id=sh_id,
            values=input_data,
            value_input_option='USER_ENTERED',
        )
        data_logger.info(result)

    except Exception as e:
        data_logger.info(f"Error occurred! {e}")
        return e


def request_to_soup_store(client: Client, urls: list, headers: dict,
                          to_data_fn: Callable, store_to_page: str, average_cols: str = None):
    """ Call requests url, convert body to soup, use store_fn"""
    try:
        response = requests.get(urls[0], headers=headers)
        log_data(response.status_code, urls[0])

        soup = BeautifulSoup(response.content, 'html.parser')
        input_data = to_data_fn(soup)

        result = add_row_to_page(client=client, page=store_to_page, data=input_data, average_cols=average_cols)
        data_logger.info(result)

    except Exception as e:
        data_logger.info(f"Error occurred! {e}")
        return e


def request_json_and_store(client: Client, urls: list, headers: dict, json_to_input_fn: Callable,
                           store_to_page: str, average_cols: str = None, ):
    """ Call requests to listed urls, execute data gathering fn on response
     and send the data to the store"""
    try:
        data = []
        for i in urls:
            response = requests.get(url=i, headers=headers)
            log_data(response.status_code, i)
            data.append(response.json())

        input_data = json_to_input_fn(data)

        result = add_row_to_page(client=client, page=store_to_page, data=input_data, average_cols=average_cols)
        data_logger.info(result)

    except Exception as e:
        data_logger.info(f"Error occurred! {e}")
        return e


def data_management_with_requests():
    """Main fn that executes all data gather with requests"""
    # gspread client for data sheet
    client = get_client(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    sheets_service = build_google_service(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    spreadsheet_id = os.environ['SPREADSHEET_DATA']

    # Cu
    request_json_and_store(
        client=client,
        urls=[os.environ.get('CU_JSON_URL'), os.environ.get('CU_JSON_STOCK')],
        headers=lme_headers,
        json_to_input_fn=cu_jsons_to_input,
        store_to_page='copper',
    )

    # Westmetal
    request_to_soup_store(
        client=client,
        urls=[os.environ.get('URL_THREE')],
        headers={},
        to_data_fn=wm_soup_to_data,
        store_to_page='copperwm',
    )

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

    # Exchange rates
    request_to_soup_store(
        client=client,
        urls=[os.environ.get('URL_FOUR')],
        headers={},
        to_data_fn=bnb_soup_to_data,
        store_to_page='rates',
    )

    # Power
    request_to_pandas_store(
        service=sheets_service,
        sh_id=spreadsheet_id,
        url=os.environ.get('URL_SIX'),
        headers=ua_header,
        to_data_fn=power_soup_to_data,
        store_to_page='power',
    )


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data_management_with_requests()
