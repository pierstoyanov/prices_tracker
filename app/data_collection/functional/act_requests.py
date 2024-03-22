import os
from typing import Callable

import requests
from bs4 import BeautifulSoup
# from memory_profiler import profile

from data_collection.exceptions import EmptyDataException, SameDayDataException
from data_collection.headers import lmba_headers, lme_headers, ua_header
from data_collection.to_input_converters.json_to_input import cu_jsons_to_input, au_json_to_input, \
    ag_json_to_input
from data_collection.to_input_converters.pandas_to_input import power_soup_to_data
from data_collection.to_input_converters.soup_to_input import bnb_soup_to_data, wm_soup_to_data_no_query
from google_sheets.google_sheets_api_operations import append_values
from logger.logger import logging
from storage.storage_manager import storage_manager
from instances import bot


# create local log
data_logger = logging.getLogger('data_collection.act_requests')


def log_data(data, url):
    """" Common function to log response status code result"""
    if data == 200:
        data_logger.info('Gathered api data from %s', url)
    else:
        raise ValueError('No data')


def average_cols_formula(last_full_row: int, average_cols: str) -> str:
    """":return: Formula for average between cols of n-th row"""
    start_col, end_col = average_cols.split(':')
    return f'=AVERAGE({start_col}{last_full_row + 1}:{end_col}{last_full_row + 1})'


def verify_collected_data(input_data: list, last_data: dict):
    """Test collected data against last data in table"""
    # check data not empty
    if len(input_data) <= 0:
        raise EmptyDataException
    # check data not same as last day
    if last_data.get('Date') == input_data[0]:
        raise SameDayDataException


def request_to_pandas_store(sh_id: str, url: str, headers: dict, to_data_fn: Callable,
                            to_page: str, store_range: str, last_data: dict,
                            average_cols: str = None):
    """ Call requests url, send content to pandas df, store with store_fn and google sheets api
    Average appends str formula for avrg between cols of the input data cols should be separated by ':'"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        log_data(response.status_code, url)

        if response.status_code != 200:
            raise Exception("Bad request")

        input_data = to_data_fn(response, last_data.get("Date"))

        verify_collected_data(input_data, last_data)

        if average_cols:
            input_data.append(average_cols_formula(
                last_data['_rownum'], average_cols))

        result = append_values(
            service=storage_manager.get_sheets_service(),
            spreadsheet_id=sh_id,
            range_name=f'{to_page}!{store_range}',
            values=input_data,
            value_input_option='USER_ENTERED',
        )

        data_logger.info("%s range updated, rows %s, cells %s ",
                         result.get("updatedRange"),
                         result.get("updatedRows"),
                         result.get("updatedCells")
                         )

    except Exception as e:
        data_logger.exception('%s', e)


def request_to_soup_store(service, sh_id: str, urls: list, headers: dict,
                          to_data_fn: Callable,
                          store_to_page: str, store_range: str, last_data: dict,
                          average_cols: str = None, params: list = None):
    """ Call requests url, convert body to soup, use store_fn
    Average appends str formula for avrg between cols of the input data cols should be separated by ':' """
    try:
        if params:
            response = requests.get(
                urls[0], headers=headers, params=params[0], timeout=10)
        else:
            response = requests.get(urls[0], headers=headers, timeout=10)

        log_data(response.status_code, urls[0])

        soup = BeautifulSoup(response.content, 'html.parser')
        input_data = to_data_fn(soup)

        verify_collected_data(input_data, last_data)

        if average_cols:
            input_data.append(average_cols_formula(
                last_data['_rownum'], average_cols))

        result = append_values(
            service=storage_manager.get_sheets_service(),
            spreadsheet_id=sh_id,
            range_name=f'{store_to_page}!{store_range}',
            values=[input_data],
            value_input_option='USER_ENTERED'
        )

        data_logger.info(result)

    except Exception as e:
        data_logger.info("Error occurred! %s", e)


def request_json_and_store(sh_id: str, urls: list, headers: dict,
                           json_to_input_fn: Callable,
                           store_to_page: str, store_range: str, last_data: dict,
                           average_cols: str = None):
    """ Call requests to listed urls, execute data gathering fn on response and send the data to the store.
     Average appends str formula for avrg between cols of the input data cols should be separated by ':'"""
    try:
        data = []
        for i in urls:
            response = requests.get(i, headers=headers, timeout=10)
            log_data(response.status_code, i)
            data.append(response.json())

        input_data = json_to_input_fn(data)

        verify_collected_data(input_data, last_data)

        if average_cols:
            input_data.append(average_cols_formula(
                last_data['_rownum'], average_cols))

        result = append_values(
            service=storage_manager.get_sheets_service(),
            spreadsheet_id=sh_id,
            range_name=f'{store_to_page}!{store_range}',
            values=[input_data],
            value_input_option='USER_ENTERED'
        )

        data_logger.info(result)

    except Exception as e:
        data_logger.info("Error occurred! %s", e)


# @profile
def data_management_with_requests():
    """Main fn that executes all data gather with requests"""

    # define variables from import
    get_daily = bot.daily_data()
    # define sheet
    spreadsheet_id = os.environ.get('SPREADSHEET_DATA')

    # last data
    c, cw, au, ag, rates, power = [
        dict(zip(x['values'][0], x['values'][1])) for x in get_daily()]

    # Cu
    request_json_and_store(
        sh_id=spreadsheet_id,
        urls=[os.environ.get('CU_JSON_URL'), os.environ.get('CU_JSON_STOCK')],
        headers=lme_headers,
        json_to_input_fn=cu_jsons_to_input,
        store_to_page='copper',
        store_range='A2:D',
        last_data=c
    )

    # Westmetal
    request_to_soup_store(
        sh_id=spreadsheet_id,
        urls=[os.environ.get('URL_THREE_NQ')],
        headers={},
        to_data_fn=wm_soup_to_data_no_query,
        store_to_page='copperwm',
        store_range='A2:D',
        last_data=cw
    )

    # Au
    request_json_and_store(
        sh_id=spreadsheet_id,
        urls=[os.environ.get('AU_AM_JSON'), os.environ.get('AU_PM_JSON')],
        headers=lmba_headers,
        json_to_input_fn=au_json_to_input,
        store_to_page='gold',
        store_range='A2:D',
        last_data=au,
        average_cols='B:C'
    )

    # Ag
    request_json_and_store(
        sh_id=spreadsheet_id,
        urls=[os.environ.get('AG_JSON')],
        headers=lmba_headers,
        json_to_input_fn=ag_json_to_input,
        store_to_page='silver',
        store_range='A2:B',
        last_data=ag
    )

    # Exchange rates
    request_to_soup_store(
        sh_id=spreadsheet_id,
        urls=[os.environ.get('URL_FOUR')],
        headers={},
        to_data_fn=bnb_soup_to_data,
        store_to_page='rates',
        store_range='A2:D',
        last_data=rates
    )

    # Power
    request_to_pandas_store(
        sh_id=spreadsheet_id,
        url=os.environ.get('URL_SIX'),
        headers=ua_header,
        to_data_fn=power_soup_to_data,
        to_page='power',
        store_range='A2:D',
        last_data=power
    )


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data_management_with_requests()
