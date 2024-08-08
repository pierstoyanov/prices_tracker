
import os
from datetime import datetime
from numpy import average

from data_unit import DataUnit
from bot.messages.symbols import symbols
from logger.logger import logging
from google_sheets.google_sheets_api_operations import get_multiple_named_ranges
from bot.messages.symbols import symbols as s

class MessageManager():
    messages_logger = logging.getLogger(__name__)
    
    def __init__(self, storage_strategy=0, sheets_service=None):
        self.storage_strategy = storage_strategy
        self.sheets_service = sheets_service
        self.du = DataUnit()

    def populate_daily_data(self):
        if self.storage_strategy in (0, 2):
            self.du.fill_data_from_firebase()

    def build_text(self):
        """ This method adds the retrieved data to a text string. """
        m = self.du.m
        r = self.du.r
        p = self.du.p

        avrg = (m["au-am"] + m["au-pm"]) / 2 # type: ignore

        text = f'' \
        f'{s["calendar"]} Дата: {m["cu-d"]}\n' \
        f'{s["chart"]}Мед\n' \
        f'Offer: *{m["cu"]:,.2f}{s["dollar"]}*\n' \
        f'3 month: *{m["cu-3m"]:,.2f}{s["dollar"]}*\n' \
        f'Stock: *{m["cu-st"]:}*\n' \
        f'{s["chart"]} Злато\n' \
        f'AM: *{m["au-am"]:,.3F}{s["dollar"]}*\n' \
        f'PM *{m["au-pm"]:,.3F}{s["dollar"]}*\n' \
        f'Average: *{avrg:.3F}{s["dollar"]}*\n' \
        f'{s["chart"]} Сребро *{m["ag"]:.4F}{s["dollar"]}*\n' \
        f'<hr>'
        f'{s["calendar"]} Дата: {r["d"]}\n'
        f'{s["USD"]} BGN/USD: *{r["USD"]}*\n' \
        f'{s["GBP"]} BGN/GBP: *{r["GBP"]}*\n' \
        f'{s["USD"]} BGN/CHF: *{r["CHF"]}*\n' \
        f'{s["highVolt"]} Ел. енергия: {p["Date"]}\n' \
        f'BGN: *{p["BGN"]:.2F}*\n' \
        f'EUR: *{p["EUR"]:.2F}*\n' \
        f'Volume *{p["Volume"]:.2F}*'

        return text
    

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

        if return_dict:
            #TODO convert to unified data format
            data = {"m": None, "r": None, "p": None}

            


            return dict(zip(ranges,
                            [dict(zip(x['values'][0], x['values'][1])) for x in result]))
        return result


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