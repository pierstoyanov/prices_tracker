import os

from data_collection.data_gather import get_url_contents, get_click_url_contents,\
    cu_soup_to_data, au_soup_to_data, ag_soup_to_data, wm_soup_to_data
from g_sheets.gspread import get_client, add_row_to_page
from logger.logger import logging

# playwright load states
load_states = ['load', 'domcontentloaded', 'networkidle']

# crate local log
data_logger = logging.getLogger('data_collection.actions')


def log_data(data, url):
    if data:
        data_logger.info(f'Gathered {data} from {url}')
    else:
        data_logger.warning('No data')


def log_result(res):
    if res:
        data_logger.info(f'Added row: {res}')


def data_management():
    # gspread client for data sheet
    client = get_client(os.environ["DATA_KEYF_NAME"])

    # cu
    # cu_wait = 'td[class=data-set-table__main]'
    cu_soup = get_url_contents(os.environ["URL_ONE"], load_state='networkidle')
    cu_data = cu_soup_to_data(cu_soup)
    log_data(cu_data, os.environ["URL_ONE"])

    res = add_row_to_page(client=client, page='copper', data=cu_data)
    log_result(res)

    # wm
    # wm_wait = "div[class=year]"
    wm_soup = get_url_contents(os.environ["URL_THREE"], load_state='networkidle')
    wm_data = wm_soup_to_data(wm_soup)
    log_data(wm_data, os.environ["URL_THREE"])

    res = add_row_to_page(client, 'copperwm', wm_data)
    log_result(res)

    # au
    au_wait = "td[class=-index0]"
    au_soup = get_url_contents(os.environ["URL_TWO"], wait_selector=au_wait)
    au_data = au_soup_to_data(au_soup)
    log_data(au_data, os.environ["URL_TWO"])

    res = add_row_to_page(client, 'gold', au_data, average_cols='B:C')
    log_result(res)

    # ag
    # ag_wait = "td[class=-index0]"
    ag_click = ['div.metals-dropdown li', 'ul.dropdown-menu >> text=Silver']
    ag_soup = get_click_url_contents(os.environ["URL_TWO"],
                                     load_state='networkidle',
                                     click_locators=ag_click)
    ag_data = ag_soup_to_data(ag_soup)
    log_data(au_data, os.environ["URL_TWO"])

    res = add_row_to_page(client, 'silver', ag_data)
    log_result(res)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data_management()
