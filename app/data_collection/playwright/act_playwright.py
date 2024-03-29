# import os
# from typing import Callable
#
# from google.oauth2.sts import Client
#
# from data_collection.data_gather import get_url_contents, get_click_url_contents
# from data_collection.soup_to_input import cu_soup_to_data, au_soup_to_data,\
#     ag_soup_to_data, wm_soup_to_data
# from google_sheets.gspread import get_client, add_row_to_page
# from logger.logger import logging
#
# # playwright load states
# load_states = ['load', 'domcontentloaded', 'networkidle']
#
# # create local log
# data_logger = logging.getLogger('data_collection.act_playwright')
#
#
# def log_data(data, url):
#     if data:
#         data_logger.info('Gathered soup data from %s', url)
#     else:
#         data_logger.warning('No data')
#
#
# def log_result(res):
#     if res.status_code == 200:
#         data_logger.info('Added row: %s}', res.get("updatedRange"))
#     else:
#         data_logger.info('Failed to add rows %s', res.status_code)
#
#
# def playwright_scrape_and_store(client: Client, url: str, soup_to_data: Callable,
#                                 store_to_page: str, average_cols: str = None,
#                                 click: list = None, wait: str = None, load_state: str = None):
#     """ Function to open url with playwright, execute actions on the page, use data gathering fn
#      and send the result to the store"""
#     try:
#         if click:
#             item_soup = get_click_url_contents(
#                 url=url, wait_selector=wait, load_state=load_state, click_locators=click)
#         else:
#             item_soup = get_url_contents(url, load_state=load_state, wait_selector=wait)
#
#         item_data = soup_to_data(item_soup)
#         log_data(item_soup, url)
#
#         result = add_row_to_page(client=client, page=store_to_page, data=item_data, average_cols=average_cols)
#         log_result(result)
#
#     except Exception as e:
#         data_logger.info("Error occurred! %s", e)
#         return e
#
#
# def data_management():
#     """Main fn that executes all data collection with playwright"""
#     # gspread client for data sheet
#     client = get_client(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
#
#     # cu
#     # cu_wait = 'td[class=data-set-table__main]'
#     playwright_scrape_and_store(client=client, url=os.environ["URL_ONE"], load_state=load_states[2],
#                                 soup_to_data=cu_soup_to_data, store_to_page='copper')
#
#     # wm
#     # wm_wait = "div[class=year]"
#     playwright_scrape_and_store(client=client, url=os.environ["URL_THREE"], load_state=load_states[2],
#                                 soup_to_data=wm_soup_to_data, store_to_page='copperwm')
#
#     # au
#     au_wait = "td[class=-index0]"
#     playwright_scrape_and_store(client=client, url=os.environ["URL_TWO"], wait=au_wait, load_state=load_states[2],
#                                 soup_to_data=au_soup_to_data, store_to_page='gold', average_cols='B:C')
#
#     # ag
#     # ag_wait = "td[class=-index0]"
#     ag_click = ['div.metals-dropdown li', 'ul.dropdown-menu >> text=Silver']
#     playwright_scrape_and_store(client=client, url=os.environ["URL_TWO"],
#                                 load_state=load_states[2], click=ag_click,
#                                 soup_to_data=ag_soup_to_data, store_to_page='silver')
#
#     # # power
#     # scrape_data_and_store(client=client, url=os.environ["URL_FOUR"],
#     #                       load_state=load_states[2], soup_to_data=power_soup_to_data,
#     #                       store_to_page='power')
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     data_management()
