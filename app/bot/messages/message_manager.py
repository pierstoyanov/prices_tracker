
from logger.logger import logging
from google_sheets.google_sheets_api_operations import get_multiple_named_ranges
from firebase_admin import db

class MessageManager():
    def __init__(self, storage_service=0, sheets_service=None):
        self.messages_logger = logging.getLogger('messages')
        self.storage_service = storage_service
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


    
    def get_data(self):
        pass


    def build_daily_info(self, service):
        try:
            c, cw, au, ag, rates, power = [dict(zip(x['values'][0], x['values'][1])) for x in get_daily_data_gsheets(service)]
            date_status = test_date(c, cw, au, ag)
            s_chart, s_dollar, s_calendar, s_usd, s_pound, s_hv \
                = '\U0001F4C8', '\U0001F4B2', '\U0001F4C5', '\U0001F4B5', '\U0001F4B7', '\U000026A1'

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

            text = f'' \
                f'{s_calendar} Дата: {c["Date"]}\n {date_status}\n' \
                f'{s_chart}Мед {symbol}\n' \
                f'Offer: *{c["Offer"]:,.2f}{s_dollar}*\n' \
                f'3 month: *{c["3mo"]:,.2f}{s_dollar}*\n' \
                f'Stock: *{c["Stock"]:}*\n' \
                f'{s_chart} Злато\n' \
                f'AM: *{au["Gold AM"]:,.3F}{s_dollar}*\n' \
                f'PM *{au["Gold PM"]:,.3F}{s_dollar}*\n' \
                f'Average: *{au["Average"]:.3F}{s_dollar}*\n' \
                f'{s_chart} Сребро *{ag["Silver"]:.4F}{s_dollar}*\n' \
                f'{s_usd} BGN/USD: *{rates["USD"]}*\n' \
                f'{s_pound} BGN/GBP: *{rates["GBP"]}*\n' \
                f'{s_usd} BGN/CHF: *{rates["CHF"]}*\n' \
                f'{s_hv} Ел. енергия: {power["Date"]}\n' \
                f'BGN: *{power["BGN"]:.2F}*\n' \
                f'EUR: *{power["EUR"]:.2F}*\n' \
                f'Volume *{power["Volume"]:.2F}*'

            return text
        except KeyError as e:
            self.messages_logger.info("Failed to build daly msg.")
            return e