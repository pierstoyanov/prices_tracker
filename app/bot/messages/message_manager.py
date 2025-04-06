from bot.messages.daily_builder import DailyBuilder
from google_sheets.google_sheets_api_operations import get_multiple_named_ranges
from logger.logger import logging
from storage.storage_manager import storage_manager as sm
import os


class MessageManager():
    messages_logger = logging.getLogger(__name__)
    
    def __init__(self, last_data, storage_strategy=0):
        self.storage_strategy = storage_strategy
        self.daily_builder = self.set_daily_builder(last_data)
        self.daily = self.populate_daily_text()
        self.sheets_service = sm.get_sheets_service()

    def populate_daily_text(self) -> str:
       return self.daily_builder.build_text()

    def set_daily_builder(self, last_data):
        daily_builder = DailyBuilder(last_data)
        return daily_builder

    def request_data(self, rq_data):
        #TODO
        return ""
    
    def get_daily_data_gsheets(self, return_dict=False) -> dict:
        """ Returns raw daly info. Param: google sheets service"""
        spreadsheet_id = os.environ.get('SPREADSHEET_DATA')
        ranges = ['cudaly', 'cuwmdaly', 'audaly', 'agdaly', 'rates', 'power']
        result = get_multiple_named_ranges(
            service=self.sheets_service,
            spreadsheet_id=spreadsheet_id,
            named_ranges=ranges,
            value_render_option='UNFORMATTED_VALUE',
            date_time_render_option='FORMATTED_STRING'
        )
        try:
            result = result.get('valueRanges')
        except AttributeError:
            self.messages_logger.error("Failed to access sheets")

        if return_dict:
            return dict(zip(ranges,
                            [dict(zip(x['values'][0], x['values'][1])) for x in result]))
        return result