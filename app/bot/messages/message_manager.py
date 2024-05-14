
from datetime import datetime
import os
from bot.messages.symbols import symbols
from logger.logger import logging
from google_sheets.google_sheets_api_operations import get_multiple_named_ranges
from firebase_admin import db

class MessageManager():
    def __init__(self, storage=0, sheets_service=None):
        self.messages_logger = logging.getLogger('messages')
        self.storage_service = storage
        self.sheets_service = sheets_service
        self.data_metals = db.reference('data/metals')
        self.data_power = db.reference('data/power')
        self.data_rates = db.reference('data/rates')

    @staticmethod
    def test_date(c, cw, au, ag):
        if c['Date'] == cw['Date'] and cw['Date'] == au['Date'] and au['Date'] == ag['Date']:
            return '\u2705'
        else:
            return '\u274C'

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
            return

        if return_dict:
            #TODO convert to unified data format
            data = {"m": None, "r": None, "p": None}

            


            return dict(zip(ranges,
                            [dict(zip(x['values'][0], x['values'][1])) for x in result]))
        return result

    def get_daily_data_fb(self) -> tuple | None:
        ref = db.reference('data')
        # Query the data to get the latest entry
        latest_metals = self.data_metals.order_by_key().limit_to_last(1).get()
        latest_power = self.data_power.order_by_key().limit_to_last(1).get()
        latest_rates = self.data_rates.order_by_key().limit_to_last(1).get()
        


        # Check the data is not None
        if not latest_metals:
            return None
        
        key_metals, data_metals = next(iter(latest_metals.items()))
        key_power, data_power = next(iter(latest_power.items()))
        key_rates, data_rates = next(iter(latest_rates.items()))

        return key_metals, data_metals, key_power, data_power, key_rates, data_rates

    
    def build_daily_info_firebase(self):
        pass

    def populate_text(self, data):
        d = data
        s = symbols
        return f'' \
        f'{s["calendar"]} Дата: {d["m"]["Date"]}\n' \
        f'{s["chart"]} Мед\n' \
        f'Offer: *{d["m"]["Offer"]:,.2f}{s["dollar"]}*\n' \
        f'3 month: *{d["m"]["3mo"]:,.2f}{s["dollar"]}*\n' \
        f'Stock: *{d["m"]["Stock"]:}*\n' \
        f'{s["chart"]} Злато*\n' \
        f'AM: *{d["m"]["Gold AM"]:,.3F}{s["dollar"]}*\n' \
        f'PM *{d["m"]["Gold PM"]:,.3F}{s["dollar"]}*\n' \
        f'Average: *{d["m"]["Average"]:.3F}{s["dollar"]}*\n' \
        f'{s["chart"]} Сребро *{d["m"]["Silver"]:.4F}{s["dollar"]}*\n' \
        f'{s["usd"]} BGN/USD: *{d["r"]["USD"]}*\n' \
        f'{s["pound"]} BGN/GBP: *{d["r"]["GBP"]}*\n' \
        f'{s["usd"]} BGN/CHF: *{d["r"]["CHF"]}*\n' \
        f'{s["hv"]} Ел. енергия: {d["p"]["Date"]}\n' \
        f'BGN: *{d["p"]["BGN"]:.2F}*\n' \
        f'EUR: *{d["p"]["EUR"]:.2F}*\n' \
        f'Volume *{d["p"]["Volume"]:.2F}*'

    def build_daily_info_gsheets(self):
        try:
            c, cw, au, ag, rates, power = [dict(zip(x['values'][0], x['values'][1])) for x in self.get_daily_data_gsheets()]
            date_status = self.test_date(c, cw, au, ag)

            # determine newer date
            lm_date, wm_date = datetime.strptime(c["Date"], "%d.%m.%Y"), \
                        datetime.strptime(cw["Date"], "%d.%m.%Y"), 
            symbol = "LME"
            if  lm_date < wm_date:
                c["Date"] = cw["Date"]
                c["Offer"] = cw["Offer"]
                c["3mo"] = cw["3mo"]
                c["Stock"] = cw["Stock"]
                symbol = "Westmetal"

            s = symbols
            text = f'' \
                f'{s["calendar"]} Дата: {c["Date"]}\n {date_status}\n' \
                f'{s["chart"]}Мед {symbol}\n' \
                f'Offer: *{c["Offer"]:,.2f}*{s["dollar"]}\n' \
                f'3 month: *{c["3mo"]:,.2f}*{s["dollar"]}\n' \
                f'Stock: *{c["Stock"]:}*\n' \
                f'{s["chart"]} Злато\n' \
                f'AM: *{au["Gold AM"]:,.3F}{s["dollar"]}*\n' \
                f'PM *{au["Gold PM"]:,.3F}{s["dollar"]}*\n' \
                f'Average: *{au["Average"]:.3F}{s["dollar"]}*\n' \
                f'{s["chart"]} Сребро *{ag["Silver"]:.4F}{s["dollar"]}*\n' \
                f'{s["usd"]} BGN/USD: *{rates["USD"]}*\n' \
                f'{s["pound"]} BGN/GBP: *{rates["GBP"]}*\n' \
                f'{s["usd"]} BGN/CHF: *{rates["CHF"]}*\n' \
                f'{s["hv"]} Ел. енергия: {power["Date"]}\n' \
                f'BGN: *{power["BGN"]:.2F}*\n' \
                f'EUR: *{power["EUR"]:.2F}*\n' \
                f'Volume *{power["Volume"]:.2F}*'

            return text
        except KeyError as e:
            self.messages_logger.info("Failed to build daly msg.")
            return e