import os

from pytz import NonExistentTimeError
from logger.logger import logging
from firebase_admin import db
from google_sheets.google_sheets_api_operations import get_multiple_named_ranges
from storage.storage_manager import storage_manager as sm

class DataUnit:
    def __init__(self):
        """
            Collections: metals, rates, power;

            Metals keys: 'cu-d', 'cu', 'cu-3m', 'cu-st', 'ag-d', \
                ag', 'au-d', 'au-am', 'au-pm'
            Rates keys: 'd','USD', 'GBP', 'CHF'
            Power keys: 'd', 'BGN', 'EUR', 'VOL'
        """
        
        self.m = dict.fromkeys(['cu-d', 'cu', 'cu-3m', 'cu-st', 'ag-d', \
            'ag', 'au-d', 'au-am', 'au-pm'], None)
        self.r = dict.fromkeys(['d','USD', 'GBP', 'CHF'], None)
        self.p = dict.fromkeys([ 'd', 'BGN', 'EUR', 'VOL'], None)
        self.logger = logging.getLogger(__name__)
    
    def fill_data_from_firebase(self) -> None:
        ref = db.reference('data/last')
        try:
            data = ref.get()

            m = data.get("metals", {}).values()[0] # type: ignore
            r = data.get("rates", {}).values()[0] # type: ignore
            p = data.get("power", {}).values()[0] # type: ignore

            for key in self.m.keys():
                self.m[key] = m[key]
            for key in self.r.keys():
                self.r[key] = r[key]
            for key in self.p.keys():
                self.p[key] = p[key]
                
        except Exception as e:
            self.logger.error(e)

    def get_daily_data_gsheets(self, service=sm.get_sheets_service()) -> list:
        """ Returns raw daly info. Param: google sheets service"""
        spreadsheet_id = os.environ.get('SPREADSHEET_DATA')
        ranges = ['cudaly', 'cuwmdaly', 'audaly', 'agdaly', 'rates', 'power']
        result = get_multiple_named_ranges(
            service=service,
            spreadsheet_id=spreadsheet_id,
            named_ranges=ranges,
            value_render_option='UNFORMATTED_VALUE',
            date_time_render_option='FORMATTED_STRING'
        ).get('valueRanges')
        
        return [dict(zip(x['values'][0], x['values'][1])) for x in result]

    def fill_data_from_gsheets(self) -> None:
        c, cw, au, ag, rates, power = self.get_daily_data_gsheets()

        m_mapping = {
            'cu-d': cw.get('Date'),
            'cu': cw.get('Offer'),
            'cu-3m': cw.get('3mo'),
            'cu-st': cw.get('Stock'),
            'ag-d': ag.get('Date'),
            'ag': ag.get('Silver'),
            'au-d': au.get('Date'),
            'au-am': au.get('Gold AM'),
            'au-pm': au.get('Gold PM')
        }
        self.m.update(m_mapping)
        
        r_mapping = {
            'd': rates.get('Date'),
            'USD': rates.get('USD'),
            'GBP': rates.get('BGN'),
            'CHF': rates.get('CHF')
        }
        self.r.update(r_mapping)

        p_mapping = {
            'd': power.get('Date'),
            'BGN': power.get('BGN'),
            'EUR': power.get('EUR'),
            'VOL': power.get('VOL')
        }
        self.p.update(p_mapping)
                
