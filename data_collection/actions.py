import os
from datetime import datetime
from typing import Callable

import requests
from gspread import Client

from data_collection.data_gather import get_url_contents, get_click_url_contents,\
    cu_soup_to_data, au_soup_to_data, ag_soup_to_data, wm_soup_to_data
from data_collection.headers import lmba_headers, lme_headers
from data_collection.request_gather import cu_jsons_to_input, au_json_to_input, \
    ag_json_to_input
from g_sheets.gspread import get_client, add_row_to_page
from logger.logger import logging

# playwright load states
load_states = ['load', 'domcontentloaded', 'networkidle']

# create local log
data_logger = logging.getLogger('data_collection.actions')


def log_data(data, url):
    if data:
        data_logger.info(f'Gathered soup data from {url}')
    else:
        data_logger.warning('No data')


def log_result(res):
    if res:
        data_logger.info(f'Added row: {res}')


def playwright_scrape_and_store(client: Client, url: str, soup_to_data: Callable,
                                store_to_page: str, average_cols: str = None,
                                click: list = None, wait: str = None, load_state: str = None):
    """ Function to open url with playwright, execute actions on the page, use data gathering fn
     and send the result to the store"""
    try:
        if click:
            item_soup = get_click_url_contents(
                url=url, wait_selector=wait, load_state=load_state, click_locators=click)
        else:
            item_soup = get_url_contents(url, load_state=load_state, wait_selector=wait)

        item_data = soup_to_data(item_soup)
        log_data(item_soup, url)

        result = add_row_to_page(client=client, page=store_to_page, data=item_data, average_cols=average_cols)
        log_result(result)

    except Exception as e:
        data_logger.info(f"Error occurred! {e}")
        return e


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


def data_management():
    """Main fn that executes all data collection with playwright"""
    # gspread client for data sheet
    client = get_client(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])

    # cu
    # cu_wait = 'td[class=data-set-table__main]'
    playwright_scrape_and_store(client=client, url=os.environ["URL_ONE"], load_state=load_states[2],
                                soup_to_data=cu_soup_to_data, store_to_page='copper')

    # wm
    # wm_wait = "div[class=year]"
    playwright_scrape_and_store(client=client, url=os.environ["URL_THREE"], load_state=load_states[2],
                                soup_to_data=wm_soup_to_data, store_to_page='copperwm')

    # au
    au_wait = "td[class=-index0]"
    playwright_scrape_and_store(client=client, url=os.environ["URL_TWO"], wait=au_wait, load_state=load_states[2],
                                soup_to_data=au_soup_to_data, store_to_page='gold', average_cols='B:C')

    # ag
    # ag_wait = "td[class=-index0]"
    ag_click = ['div.metals-dropdown li', 'ul.dropdown-menu >> text=Silver']
    playwright_scrape_and_store(client=client, url=os.environ["URL_TWO"],
                                load_state=load_states[2], click=ag_click,
                                soup_to_data=ag_soup_to_data, store_to_page='silver')

    # # power
    # scrape_data_and_store(client=client, url=os.environ["URL_FOUR"],
    #                       load_state=load_states[2], soup_to_data=power_soup_to_data,
    #                       store_to_page='power')


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
        store_to_page='copper'
    )

    # Au
    request_json_and_store(
        client=client,
        urls=[os.environ.get('AU_AM_JSON'), os.environ.get('AU_PM_JSON')],
        headers=lmba_headers,
        json_to_input_fn=au_json_to_input,
        store_to_page='gold'
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
    # data_management()
    data_management_with_requests()
