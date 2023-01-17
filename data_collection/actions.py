import os
from typing import Callable

from gspread import Client

from data_collection.data_gather import get_url_contents, get_click_url_contents,\
    cu_soup_to_data, au_soup_to_data, ag_soup_to_data, wm_soup_to_data
from data_collection.headers import lbma_headers, copper_headers
from data_collection.request_gather import get_url_request_with_headers
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


def scrape_data_and_store(client: Client, url: str, soup_to_data: Callable, store_to_page: str,
                          average_cols: str = None, click: list = None, wait: str = None, load_state: str = None):
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


def data_management():
    # gspread client for data sheet
    client = get_client(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])

    # cu
    # cu_wait = 'td[class=data-set-table__main]'
    scrape_data_and_store(client=client, url=os.environ["URL_ONE"], load_state=load_states[2],
                          soup_to_data=cu_soup_to_data, store_to_page='copper')

    # wm
    # wm_wait = "div[class=year]"
    scrape_data_and_store(client=client, url=os.environ["URL_THREE"], load_state=load_states[2],
                          soup_to_data=wm_soup_to_data, store_to_page='copperwm')

    # au
    au_wait = "td[class=-index0]"
    scrape_data_and_store(client=client, url=os.environ["URL_TWO"], wait=au_wait, load_state=load_states[2],
                          soup_to_data=au_soup_to_data, store_to_page='gold', average_cols='B:C')

    # ag
    # ag_wait = "td[class=-index0]"
    ag_click = ['div.metals-dropdown li', 'ul.dropdown-menu >> text=Silver']
    scrape_data_and_store(client=client, url=os.environ["URL_TWO"],
                          load_state=load_states[2], click=ag_click,
                          soup_to_data=ag_soup_to_data, store_to_page='silver')

    # # power
    # scrape_data_and_store(client=client, url=os.environ["URL_FOUR"],
    #                       load_state=load_states[2], soup_to_data=power_soup_to_data,
    #                       store_to_page='power')


def data_management_with_requests():
    # gold_am_url = 'https://prices.lbma.org.uk/json/gold_am.json'
    # gold_am = get_url_request_with_headers(gold_am_url, lbma_headers)

    # gold_pm_url = 'https://prices.lbma.org.uk/json/gold_pm.json'
    # gold_pm = get_url_request_with_headers(gold_pm_url, lbma_headers)

    # silver_url = 'https://prices.lbma.org.uk/json/silver.json'
    # silver = get_url_request_with_headers(silver_url, lbma_headers)

    copper_url = 'https://www.lme.com/api/trading-data/day-delayed?datasourceId=762a3883-b0e1-4c18-b34b-fe97a1f2d3a5'


    # print(gold_am)

    # print(max(silver.json(), key=lambda k: k['d']))

    copper = get_url_request_with_headers(copper_url, copper_headers)
    cu_cash = copper.json().get('Rows')[0]
    print(copper.json())


# data_management_with_requests()
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # data_management()
    data_management_with_requests()
