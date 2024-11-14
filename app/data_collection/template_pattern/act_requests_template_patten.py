from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from data_collection.exceptions import EmptyDataException, SameDayDataException
from data_collection.headers import lmba_headers, lme_headers, ua_header
from data_collection.to_input_converters.json_to_input import \
    cu_jsons_to_input, au_json_to_input, ag_json_to_input
from data_collection.to_input_converters.pandas_to_input import \
    PowerSoupToPandasToData,  power_soup_to_data
from data_collection.to_input_converters.soup_to_input import \
    bnb_soup_to_data, wm_soup_to_data_no_query
from data_unit import DataUnit
from firebase_rt_db.firebase_api_operations import get_latest_entry
from google_sheets.google_sheets_api_operations import append_values
from firebase_admin import db
from logger.logger import logging
from storage.storage_manager import storage_manager
from instances import bot, start_data


# create local log
data_logger = logging.getLogger(__name__)


#### Helper functions
def log_data(data, url):
    if data == 200:
        data_logger.info('Gathered api data from %s', url)
    else:
        raise ValueError('No data')

def verify_collected_data(input_data: list, last_data: dict):
    """Test collected data against last data in table"""
    # check data not empty
    if len(input_data) <= 0:
        raise EmptyDataException
    # check data not same as last day
    for i in input_data:
        if last_data.get('Date') == i[0]:
            raise SameDayDataException

def average_cols_formula(last_full_row: int, average_cols: str) -> str:
    """":return: Formula for average between cols of n-th row"""
    start_col, end_col = average_cols.split(':')
    return f'=AVERAGE({start_col}{last_full_row + 1}:{end_col}{last_full_row + 1})'


def convert_date(date: str):
        # convert a single date from DD.MM.YYYY to YYYY-MM-DD format
        parsed_date = datetime.strptime(date, "%d.%m.%Y")
        return parsed_date.strftime("%Y-%m-%d")
#### /Helper functions


# Init new DataUnit
new_data = DataUnit()

class DataFirebaseStore:
    """ Singleton for managing writing collected data to firebase realtime database.
    :return: void
    """
    def __init__(self, last : DataUnit):
        self.ref_data = db.reference('data')
        self.ref_last = db.reference('start/last')
        self.data: DataUnit
        self.last = last

    def get_last_pow_date(self):
        return self.last.power.get("d")

    def get_last_rate_date(self) -> int:
        return self.last.rates.get('d')
    
    def get_m_date(self):
        for key in self.data.metals:
            # return first key ending with "-d" that is not None or -1
            if "-d" in key and self.data.metals[key] is not None \
                and self.data.metals[key] != -1:
                return self.data.metals[key]
        raise Exception("No valid date for m stored.")

    def store_data(self):
        """ Store data to firebase nodes.
        :return: void
        """
        try: # store m 
            m_date = self.get_m_date()

            self.ref_data.child('metals').update({m_date: self.data.metals})
            self.last.metals.update({m_date: self.data.metals})
        except Exception as e:
            data_logger.error('%s', e)

        try: # store r
            r_date = self.get_last_rate_date()
            self.ref_data.child('rates').update({r_date: self.data.rates})
            self.last.rates.update({r_date: self.data.rates})
        except Exception as e:
            data_logger.error(e)
        
        if any(self.data.power): # store p
            self.ref_data.child('power').update(self.data.power)
            lp_k, lp_v = self.data.power.popitem()
            self.last.power.update({lp_k: lp_v})

        try:
            self.ref_last.update(self.last.__dict__)
        except ValueError as e:
            data_logger.error(e)


# init DataFirebaseStore instance
frb_mngr = DataFirebaseStore(start_data.last_data)

# Template for retreiving data and storing it in gsheets
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
        """Process data from raw_response and store it 
        in instance variable self.input_data.
        Implemented in child classes"""
        raise NotImplementedError

    def store_data(self):
        """ Stores collected data to google sheets
        :return: void
        """
        try:
            # verify for g_sheets 
            verify_collected_data(self.input_data, self.last_data)

            append_values(service=self.service,
                          spreadsheet_id=self.sh_id,
                          range_name=f'{self.store_to_page}!{self.store_range}',
                          values=self.input_data,
                          value_input_option='USER_ENTERED')
        except Exception as e:
            data_logger.exception('%s', e)

    def get_last_date(self):        
        return self.last_data.get('Date') if self.last_data else None


class CuDataRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        data = []
        self.request_data(self.url_headers)

        for response in self.raw_response:

            data.append(response.json())

        # add to frb not yet impl.

        self.input_data.append(cu_jsons_to_input(data))
        self.store_data()
        self.raw_response = []  # clear raw response


class WmDataRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        self.request_data(self.url_headers)
        soup = BeautifulSoup(self.raw_response[0].content, 'html.parser')
        
        input_data = wm_soup_to_data_no_query(soup)

        # export data to data unit object
        new_data.metals['cu-d'] = convert_date(input_data[0])
        new_data.metals['cu'], new_data.metals['cu-3m'], 
        new_data.metals['cu-st'] = input_data[1:]

        self.input_data.append(input_data)
        self.store_data()
        self.raw_response = []  # clear raw response


class AuDataRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        data = []
        self.request_data(self.url_headers)

        for response in self.raw_response:
            data.append(response.json())

        input_data: list = au_json_to_input(data)

        # export data to data unit object
        new_data.metals['au-d'] = convert_date(input_data[0])
        new_data.metals['au-am'], new_data.metals['au-pm'] = input_data[1:]

        # add average cols formula to input data if needed
        if self.average_cols:
            input_data.append(average_cols_formula(
                self.last_data.get('_rownum'),
                self.average_cols)
            )

        self.input_data.append(input_data)
        self.store_data()
        self.raw_response = []  # clear raw response


class AgDataRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        self.request_data(self.url_headers)
        input_data = ag_json_to_input([self.raw_response[0].json()])

        # export data to data unit object
        new_data.metals['ag-d'] = convert_date(input_data[0])
        new_data.metals['ag'] = input_data[1]

        self.input_data.append(input_data)
        self.store_data()
        self.raw_response = []  # clear raw response


class ExchangeRatesRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        self.request_data(self.url_headers)
        soup = BeautifulSoup(self.raw_response[0].content, 'html.parser')
        input_data = bnb_soup_to_data(soup)
        
        # export data to data unit object
        new_data.rates['d'] = convert_date(input_data[0])
        new_data.rates['USD'], new_data.rates['GBP'], 
        new_data.rates['CHF'] = input_data[1:]
        
        self.input_data.append(input_data)
        self.store_data()
        self.raw_response = []  # clear raw response


class PowerRequest(DataRequestStoreTemplate):
    """ inherits from DataRequestStoreTemplate """

    def process_data(self):
        self.request_data(self.url_headers)

        converter = PowerSoupToPandasToData(
            response=self.raw_response[0], last_date_gsheet=
            self.last_data.get('Date'), last_date_fb=frb_mngr.get_last_pow_date()
        )

        # export data to data unit object
        new_data.power = converter.convert_for_fb()

        self.input_data = converter.convert_for_gsheets()
        self.store_data()
        self.raw_response = []  # clear raw response


class DataManagementWithRequests:
    """Singleton class to arrange staging and 
    executing data collection and storage
    """
    def __init__(self):
        self.sheets_service = storage_manager.get_sheets_service()
        self.session = requests.Session()
        self.spreadsheet_id: str = os.environ.get('SPREADSHEET_DATA')
        self.data_requests: list[DataRequestStoreTemplate] = []
        self.last_data: dict = self.get_last_data()

    def get_last_data(self):# -> dict[Any, Any]:
        """ Get the last data from gsheets."""
        combined_dict = bot.get_last_data(return_dict=True)
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
        # # # copper
        # self.add_data_management(CuDataRequest(
        #     service=self.sheets_service,
        #     session=self.session,
        #     sh_id=self.spreadsheet_id,
        #     last_data=self.last_data["cudaly"],
        #     store_to_page='copper',
        #     store_range='A2:D',
        #     url_headers=((os.environ.get('CU_JSON_URL'), lme_headers),
        #                  (os.environ.get('CU_JSON_STOCK'), lme_headers))
        # ))
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
        
        frb_mngr.data = new_data
        frb_mngr.store_data()

        return err_count


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    DataManagementWithRequests().run()
