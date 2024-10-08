import os
from bot.messages.symbols import symbols as s
from datetime import datetime
from logger.logger import logging
from bot.messages.static_messages import wrong_day, wrong_month, wrong_year, wrong
from google_sheets.google_sheets_api_operations import \
    get_multiple_named_ranges, update_values_in_sheet


messagelogger = logging.getLogger(__name__)


def test_date(c, cw, au, ag):
    if c['Date'] == cw['Date'] \
            and cw['Date'] == au['Date'] \
            and au['Date'] == ag['Date']:
        return '\u2705'
    return '\u274C'


def check_valid_date(message: str):
    """ Checks if date is valid for query.
        Param: date string in format 'dd/mm/yyyy'
        Returns: empty string if date is valid or string with error message."""
    day, month, year = [int(_) for _ in message.split('/')]
    result = ''
    if day > 31 or month == 2 and day > 28:
        result += wrong_day
    if month > 12:
        result += wrong_month
    if 1951 > year or year > 2050:
        result += wrong_year
    if result:
        return wrong + result
    return result


def query_day(service, rq_date: str, ranges: list):
    """ Returns raw info for specific day. Param: google sheets service, date string in format"""
    spreadsheet_id = os.environ.get('SPREADSHEET_DATA')

    # set query date
    update_rq = update_values_in_sheet(
        service=service,
        spreadsheet_id=spreadsheet_id,
        range_name='request!A1',
        values=[rq_date],
        value_input_option='USER_ENTERED'
    )
    messagelogger.info("Query date set!")
    
    # get result
    result = get_multiple_named_ranges(service=service,
                                       spreadsheet_id=spreadsheet_id,
                                       named_ranges=ranges,
                                       value_render_option='UNFORMATTED_VALUE',
                                       date_time_render_option='FORMATTED_STRING'
                                       ).get('valueRanges')

    return result


def build_requested_day_info(sheetservice, rq_day: str):
    try:
        r = datetime.strptime(rq_day.strip(), '%d/%m/%Y')
        day_num = r.weekday()
        days = {5: 'събота', 6: 'неделя'}
        rq_date = r.strftime('%d.%m.%Y')

        if day_num < 5:
            ranges = ['rqwmcu', 'rqau', 'rqag', 'rqrates', 'rqpower']
            cw, au, ag, rates, power = [dict(zip(x['values'][0], x['values'][1]))
                                        for x in query_day(sheetservice, rq_date, ranges)]
            text = f'' \
                   f'{s["calendar"]} Данни за дата \n' \
                   f'{s["chart"]} Мед {cw["Date"]}: \n' \
                   f'Offer: *{cw["Offer"]:,.2f}{s["dollar"]}*\n' \
                   f'3 month: *{cw["3mo"]:,.2f}{s["dollar"]}*\n' \
                   f'Stock: *{cw["Stock"]:}*\n' \
                   f'{s.chart} Злато {au["Date"]}: \n' \
                   f'AM: *{au["Gold AM"]:,.3F}{s["dollar"]}*\n' \
                   f'PM *{au["Gold PM"]:,.3F}{s["dollar"]}*\n' \
                   f'Average: *{au["Average"]:.3F}{s["dollar"]}*\n' \
                   f'{s["chart"]} Сребро {ag["Date"]}: \n *{ag["Silver"]:.4F}{s["dollar"]}*\n' \
                   f'{s["USD"]} BGN/USD {rates["Date"]}: *{rates["USD"]}*\n' \
                   f'{s["GBP"]} BGN/GBP {rates["Date"]}: *{rates["GBP"]}*\n' \
                   f'{s["USD"]} BGN/CHF {rates["Date"]}: *{rates["CHF"]}*\n' \
                   f'{s["highVolt"]} Ел. енергия {power["Date"]}:\n' \
                   f'BGN: *{power["BGN"]:.2F}*\n' \
                   f'EUR: *{power["EUR"]:.2F}*\n' \
                   f'Volume *{power["Volume"]:.2F}*'
            return text
        else:
            ranges = ['rqpower']
            x = query_day(sheetservice, rq_date, ranges)[0].get('values')
            power = dict(zip(x[0], x[1]))
            text = f'' \
                   f'{s["calendar"]} Данни за ({days[day_num]}) \n' \
                   f'{s["highVolt"]} Ел. енергия {power["Date"]}:\n' \
                   f'BGN: *{power["BGN"]:.2F}*\n' \
                   f'EUR: *{power["EUR"]:.2F}*\n' \
                   f'Volume *{power["Volume"]:.2F}*'
            return text
    except KeyError as e:
        messagelogger.info("Failed to build request msg.")
        return e
