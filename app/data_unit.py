import os
from logger.logger import logging
from firebase_admin import db
from google_sheets.google_sheets_api_operations import get_multiple_named_ranges
from storage.storage_manager import storage_manager as sm
from firebase_rt_db.firebase_api_operations import get_latest_entry

class DataUnit:
    logger = logging.getLogger(__name__)
    def __init__(self):
        """
            Collections: metals, rates, power;

            Metals keys: 'cu-d', 'cu', 'cu-3m', 'cu-st', 'ag-d', \
                        ag', 'au-d', 'au-am', 'au-pm'
            Rates keys: 'd','USD', 'GBP', 'CHF'
            Power keys: 'd', 'BGN', 'EUR', 'VOL'
        """
        
        self.metals = dict.fromkeys(['cu-d', 'cu', 'cu-3m', 'cu-st', 'ag-d', \
            'ag', 'au-d', 'au-am', 'au-pm'], None)
        self.rates = dict.fromkeys(['d','USD', 'GBP', 'CHF'], None)
        self.power = dict.fromkeys([ 'd', 'BGN', 'EUR', 'VOL'], None)
        # self.logger = logging.getLogger(__name__)
    
    def _fill_attribute_dict(self, data_dict, collection_name):
        """Fills a unit attribute/colelction with data from the provided dict.
        Provided dict has all, or some of the attr keys.  
        """
        current_dict = getattr(self, collection_name, None)

        for k,v in data_dict.items():
            if k in current_dict:
                current_dict[k] = v


    def fill_last_from_firebase(self, last) -> None:
        """Fill DataUnit with the last data from start object. 
        If not available, build it from data object."""
        
        # get last from start object if not passed as arg
        if not last:
            last = db.reference('start/last').get()

        # if last object is still empty, try to biild it again from data
        if not last:
            self._fill_last_from_firebase_data()
            return
        
        last_metals = last.get('metals')
        if last_metals:
            self._fill_attribute_dict(last_metals, 'metals')

        last_rates = last.get('rates')
        if last_rates:
            self._fill_attribute_dict(last_rates, 'rates')
        
        last_power = last.get('power')
        if last_power:
            self._fill_attribute_dict(last_power, 'power')
    
    def _fill_last_from_firebase_data(self) -> None:
        """Fill DataUnit with the last data from the main data object.
        This is used the the quickaccess object start fails."""
        try:
            failed_data_fills_counter = 0

            m = get_latest_entry(db.reference('data/metals'))
            if m:
                self.metals.update(m)
            else:
                failed_data_fills_counter+=1

            p = get_latest_entry(db.reference('data/power'))
            if p:
                self.power.update(p)
            else:
                failed_data_fills_counter+=1

            r = get_latest_entry(db.reference('data/rates'))
            if r:
                self.rates.update(r)
            else:
                failed_data_fills_counter+=1
            
            if failed_data_fills_counter != 0: # check all 3 were filled 
                self.fill_last_data_from_gsheets()

        except Exception as e:
            self.logger.exception('%s', e)

    def _get_daily_data_gsheets(self, service=sm.get_sheets_service()) -> list:
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

    def fill_last_data_from_gsheets(self) -> None:
        #TODO Convert day format to ISO format
        c, cw, au, ag, rates, power = self._get_daily_data_gsheets()

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
        self.metals.update(m_mapping)
        
        r_mapping = {
            'd': rates.get('Date'),
            'USD': rates.get('USD'),
            'GBP': rates.get('BGN'),
            'CHF': rates.get('CHF')
        }
        self.rates.update(r_mapping)

        p_mapping = {
            'd': power.get('Date'),
            'BGN': power.get('BGN'),
            'EUR': power.get('EUR'),
            'VOL': power.get('Volume')
        }
        self.power.update(p_mapping)
    
    def test_unit_is_filled(self):
        """
        check if m collection is filled
        :returns: bool
        """
        #TODO change to test all 3 collections
        if not any(self.metals.values()):
            self.fill_last_data_from_gsheets()
            if not any(self.metals.values()):
                return False
            return True
        else: 
            return True
    

