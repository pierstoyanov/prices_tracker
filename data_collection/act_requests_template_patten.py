import os
from typing import Callable

import requests
from bs4 import BeautifulSoup
# from memory_profiler import profile

from bot.daly_data import get_daly
from data_collection.exceptions import EmptyDataException, SameDayDataException
from data_collection.headers import lmba_headers, lme_headers, ua_header
from data_collection.json_to_input import cu_jsons_to_input, au_json_to_input, \
    ag_json_to_input
from data_collection.pandas_to_input import power_soup_to_data
from data_collection.soup_to_input import wm_soup_to_data, bnb_soup_to_data, wm_soup_to_data_no_query
from google_sheets.google_sheets_api_operations import append_values
from google_sheets.google_service import build_google_service
from logger.logger import logging

# create local log
data_logger = logging.getLogger('data_collection.act_requests')


def log_data(data, url):
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


class DataRequestStoreTemplate:
    def __init__(self, service, session, sh_id: str, last_data: dict,
                 store_to_page: str, store_range: str, average_cols=None):
        self.service = service
        self.session = session
        self.sh_id = sh_id
        self.last_data = last_data
        self.store_to_page = store_to_page
        self.store_range = store_range
        self.average_cols = average_cols
        self.raw_response = []
        self.input_data = []

    def request_data(self, url_headers_tuples: list):
        """
        Fetch data from url and store it in instance variable self.raw_response
        :return: void, updates var self.raw_response
        :param url_headers_tuples: list of url and header tuples
        """
        for url, headers in url_headers_tuples:
            try:
                self.session.headers.update(headers)
                response = self.session.get(url, timeout=10)
                log_data(response.status_code, url)
                if response.status_code != 200:
                    raise Exception("Bad request")

                self.raw_response.append(response)
            except Exception as e:
                data_logger.exception('%s', e)

    def process_data(self):
        """Process data from raw_response and store it
        in instance variable self.input_data"""
        raise NotImplementedError

    def store_data(self):
        """
        Stores collected data to google sheets
        :return: void
        """
        try:
            verify_collected_data(self.input_data, self.last_data)
            # add average cols formula to input data if needed
            if self.average_cols:
                self.input_data.append(average_cols_formula(
                    self.last_data.get('_rownum'),
                    self.average_cols))

            append_values(service=self.service,
                          spreadsheet_id=self.sh_id,
                          range_name=f'{self.store_to_page}!{self.store_range}',
                          values=[self.input_data],
                          value_input_option='USER_ENTERED')
        except Exception as e:
            data_logger.exception('%s', e)


class CuDataManagement(DataRequestStoreTemplate):
    def __init__(self, list_url_headers_tuples: list):
        super().__init__(list_url_headers_tuples)

    def process_data(self):
        data = []
        self.request_data(self.list_url_headers_tuples)

        for response in self.raw_response:
            data.append(response.json())

        self.input_data = cu_jsons_to_input(data)
        self.store_data()
        self.raw_response = []  # clear raw response


class WmDataManagement(DataRequestStoreTemplate):
    def __init__(self, url_header_tuple: tuple):
        super().__init__(url_header_tuple)

    def process_data(self):
        self.request_data([self.url_header_tuple])
        soup = BeautifulSoup(self.raw_response.content, 'html.parser')
        self.input_data = wm_soup_to_data_no_query(soup)
        self.store_data()
        self.raw_response = []  # clear raw response


class AuDataManagement(DataRequestStoreTemplate):
    def __init__(self, list_url_header_tuples: list):
        super.__init__(list_url_header_tuples)

    def process_data(self):
        data = []
        self.request_data(self.list_url_header_tuples)

        for response in self.raw_response:
            data.append(response.json())

        self.input_data = au_json_to_input(data)
        self.store_data()
        self.raw_response = []  # clear raw response


class AgDataManagement(DataRequestStoreTemplate):
    def __init__(self, url_header_tuple: tuple):
        super().__init__(url_header_tuple)

    def process_data(self):
        self.request_data([self.url_header_tuple])
        self.input_data = ag_json_to_input(self.raw_response.json())
        self.store_data()
        self.raw_response = []  # clear raw response


class ExchangeRatesManagement(DataRequestStoreTemplate):
    def __init__(self, url_header_tuple: tuple):
        super().__init__(url_header_tuple)

    def process_data(self):
        self.request_data([self.url_header_tuple])
        soup = BeautifulSoup(self.raw_response.content, 'html.parser')
        self.input_data = bnb_soup_to_data(soup)
        self.store_data()
        self.raw_response = []  # clear raw response


class PowerManagement(DataRequestStoreTemplate):
    def __init__(self, url_header_tuple: tuple):
        super().__init__(url_header_tuple)

    def process_data(self):
        self.request_data([self.url_header_tuple])
        soup = BeautifulSoup(self.raw_response.content, 'html.parser')
        self.input_data = power_soup_to_data(soup)
        self.store_data()
        self.raw_response = []  # clear raw response


class DataManagementWithRequests:
    def __init__(self):
        self.sheets_service = build_google_service(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
        self.spreadsheet_id = os.environ['SPREADSHEET_DATA']
        self.session = requests.Session()
        self.data_requests = [],
        self.last_data: dict = self.get_last_data()

    def get_last_data(self):
        combined_dict = {k: v for x in get_daly(self.sheets_service) for k, v in zip(x['values'][0], x['values'][1])}
        return combined_dict

    def add_data_management(self, request: DataRequestStoreTemplate):
        self.data_requests.append(request)

    def execute_data_requests(self):
        for request in self.data_requests:
            request.process_data()

    def stage_data_requests(self):
        self.add_data_management(CuDataManagement(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["cu"],
            store_to_page='copper',
            store_range='A2:D',
            list_url_headers_tuples= [(os.environ.get('CU_JSON_URL'), lme_headers)
                                      (os.environ.get('CU_JSON_STOCK'), lme_headers)]
        ))

        self.add_data_management(WmDataManagement(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["cw"],
            store_to_page='copperwm',
            store_range='A2:D',
            url_header_tuple=(os.environ.get('URL_THREE_NQ'), {})
        ))

        self.add_data_management(AuDataManagement(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["au"],
            store_to_page='gold',
            store_range='A2:D',
            average_cols='B:C',
            list_url_header_tuples=[(os.environ.get('AU_AM_JSON'), lmba_headers),
                               (os.environ.get('AU_PM_JSON'), lmba_headers)]
        ))

        self.add_data_management(AgDataManagement(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["ag"],
            store_to_page='silver',
            store_range='A2:B',
            url_header_tuple=(os.environ.get('AG_JSON'), lmba_headers)
        ))

        self.add_data_management(ExchangeRatesManagement(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["ex"],
            store_to_page='rates',
            store_range='A2:D',
            url_header_tuple=(os.environ.get('URL_FOUR'), {})
        ))

        self.add_data_management(PowerManagement(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["pw"],
            store_to_page='power',
            store_range='A2:D',
            url_header_tuple=(os.environ.get('URL_SIX'), ua_header)
        ))

    def run(self):
        self.stage_data_requests()
        self.execute_data_requests()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # data_management_with_requests()
    pass
