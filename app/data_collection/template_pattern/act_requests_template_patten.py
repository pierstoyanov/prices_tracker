import os
import requests
from bs4 import BeautifulSoup
# from memory_profiler import profile

from app.bot.daly_data import get_daly
from app.data_collection.exceptions import EmptyDataException, SameDayDataException
from app.data_collection.headers import lmba_headers, lme_headers, ua_header
from app.data_collection.to_input_converters.json_to_input import cu_jsons_to_input, au_json_to_input, \
    ag_json_to_input
from app.data_collection.to_input_converters.pandas_to_input import power_soup_to_data
from app.data_collection.to_input_converters.soup_to_input import bnb_soup_to_data, wm_soup_to_data_no_query
from app.google_sheets.google_sheets_api_operations import append_values
from app.google_sheets.google_service import build_google_service
from app.logger.logger import logging

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
    """Template for data request and store to google sheets"""

    def __init__(self, service, session, sh_id: str, last_data: dict,
                 store_to_page: str, store_range: str, url_headers: tuple,
                 average_cols=None):
        self.service = service
        self.session = session
        self.sh_id = sh_id
        self.url_headers = url_headers
        self.last_data = last_data
        self.store_to_page = store_to_page
        self.store_range, self.average_cols = store_range, average_cols
        self.raw_response = []
        self.input_data: list = []

    def request_data(self, url_headers_tuples: tuple):
        """Fetch data from url and store it in instance variable self.raw_response
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
        """Process data from raw_response and store it in instance variable self.input_data.
        Implemented in child classes"""
        raise NotImplementedError

    def store_data(self):
        """ Stores collected data to google sheets
        :return: void
        """
        try:
            verify_collected_data(self.input_data, self.last_data)

            append_values(service=self.service,
                          spreadsheet_id=self.sh_id,
                          range_name=f'{self.store_to_page}!{self.store_range}',
                          values=self.input_data,
                          value_input_option='USER_ENTERED')
        except Exception as e:
            data_logger.exception('%s', e)


class CuDataRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        data = []
        self.request_data(self.url_headers)

        for response in self.raw_response:
            data.append(response.json())

        self.input_data.append(cu_jsons_to_input(data))
        self.store_data()
        self.raw_response = []  # clear raw response


class WmDataRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        self.request_data(self.url_headers)
        soup = BeautifulSoup(self.raw_response[0].content, 'html.parser')
        self.input_data.append(wm_soup_to_data_no_query(soup))
        self.store_data()
        self.raw_response = []  # clear raw response


class AuDataRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        data = []
        self.request_data(self.url_headers)

        for response in self.raw_response:
            data.append(response.json())

        edited_input: list = au_json_to_input(data)
        # add average cols formula to input data if needed
        if self.average_cols:
            edited_input.append(average_cols_formula(
                self.last_data.get('_rownum'),
                self.average_cols)
            )

        self.input_data.append(edited_input)
        self.store_data()
        self.raw_response = []  # clear raw response


class AgDataRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        self.request_data(self.url_headers)
        self.input_data.append(ag_json_to_input([self.raw_response[0].json()]))
        self.store_data()
        self.raw_response = []  # clear raw response


class ExchangeRatesRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        self.request_data(self.url_headers)
        soup = BeautifulSoup(self.raw_response[0].content, 'html.parser')
        self.input_data.append(bnb_soup_to_data(soup))
        self.store_data()
        self.raw_response = []  # clear raw response


class PowerRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        self.request_data(self.url_headers)
        self.input_data = power_soup_to_data(
            response=self.raw_response[0],
            last_date=self.last_data.get("Date")
        )
        self.store_data()
        self.raw_response = []  # clear raw response


class DataManagementWithRequests:
    """Singleton class for arrange staging and executing data collection and storage"""

    def __init__(self):
        self.sheets_service = build_google_service(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
        self.session = requests.Session()
        self.spreadsheet_id: str = os.environ['SPREADSHEET_DATA']
        self.data_requests: list[DataRequestStoreTemplate] = []
        self.last_data: dict = self.get_last_data()

    def get_last_data(self):
        combined_dict = get_daly(self.sheets_service, return_dict=True)
        return combined_dict

    def add_data_management(self, request: DataRequestStoreTemplate):
        """Pools data request objects for processing """
        self.data_requests.append(request)

    def execute_data_requests(self):
        error_count = 0

        for request in self.data_requests:
            try:
                request.process_data()
            except Exception as e:
                data_logger.error(e)
                error_count += 1
                continue

        return error_count

    def stage_data_requests(self):
        """Hardcoded data request objects for processing"""
        # copper
        self.add_data_management(CuDataRequest(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["cudaly"],
            store_to_page='copper',
            store_range='A2:D',
            url_headers=((os.environ.get('CU_JSON_URL'), lme_headers),
                         (os.environ.get('CU_JSON_STOCK'), lme_headers))
        ))
        # copper wm
        self.add_data_management(WmDataRequest(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["cuwmdaly"],
            store_to_page='copperwm',
            store_range='A2:D',
            url_headers=((os.environ.get('URL_THREE_NQ'), {}),)
        ))
        # gold
        self.add_data_management(AuDataRequest(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["audaly"],
            store_to_page='gold',
            store_range='A2:D',
            average_cols='B:C',
            url_headers=((os.environ.get('AU_AM_JSON'), lmba_headers),
                         (os.environ.get('AU_PM_JSON'), lmba_headers))
        ))
        # silver
        self.add_data_management(AgDataRequest(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["agdaly"],
            store_to_page='silver',
            store_range='A2:B',
            url_headers=((os.environ.get('AG_JSON'), lmba_headers),)
        ))
        # exchange rates
        self.add_data_management(ExchangeRatesRequest(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["rates"],
            store_to_page='rates',
            store_range='A2:D',
            url_headers=((os.environ.get('URL_FOUR'), {}),)
        ))
        # power
        self.add_data_management(PowerRequest(
            service=self.sheets_service,
            session=self.session,
            sh_id=self.spreadsheet_id,
            last_data=self.last_data["power"],
            store_to_page='power',
            store_range='A2:D',
            url_headers=((os.environ.get('URL_SIX'), ua_header),)
        ))

    def run(self):
        """Main class execution method"""
        self.stage_data_requests()
        err_count = self.execute_data_requests()

        return err_count


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    DataManagementWithRequests().run()
