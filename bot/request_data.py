import os
from datetime import datetime

from bot.bot import sheets_service, bot_logger
from bot.messages import wrong_day, wrong_month, wrong_year, wrong
from google_sheets.google_sheets_api_operations import get_multiple_named_ranges, update_values_in_sheet


def test_date(c, cw, au, ag):
    if c['Date'] == cw['Date'] and cw['Date'] == au['Date'] and au['Date'] == ag['Date']:
        return '\u2705'
    return '\u274C'


def check_valid_date(message: str):
    day, month, year = [int(_) for _ in message.split('/')]
    result = ''
    if day > 31 or month == 2 and day > 28:
        result += wrong_day
    if month > 12:
        result += wrong_month
    if 1951 < year > 2050:
        result += wrong_year
    if result:
        return wrong + result
    return result


def query_day(service, rq_date: str, ranges: list):
    """ Returns raw info for specific day. Param: google sheets service, date string in format"""
    spreadsheet_id = os.environ['SPREADSHEET_DATA']

    # set query date
    update_rq = update_values_in_sheet(
        service=service,
        spreadsheet_id=spreadsheet_id,
        range_name='request!A1',
        values=[rq_date],
        value_input_option='USER_ENTERED'
    )
    bot_logger.info("Query date set!")
    
    # get result
    result = get_multiple_named_ranges(service=service,
                                       spreadsheet_id=spreadsheet_id,
                                       named_ranges=ranges,
                                       value_render_option='UNFORMATTED_VALUE',
                                       date_time_render_option='FORMATTED_STRING'
                                       ).get('valueRanges')

    return result


def build_requested_day_info(rq_day: str):
    s_chart, s_dollar, s_calendar, s_usd, s_pound, s_hv = \
        '\U0001F4C8', '\U0001F4B2', '\U0001F4C5', '\U0001F4B5', '\U0001F4B7', '\U000026A1'
    try:
        r = datetime.strptime(rq_day.strip(), '%d/%m/%Y')
        day_num = r.weekday()
        days = {5: 'събота', 6: 'неделя'}
        rq_date = r.strftime('%d.%m.%Y')

        if day_num < 5:
            ranges = ['rqwmcu', 'rqau', 'rqag', 'rqrates', 'rqpower']
            cw, au, ag, rates, power = [dict(zip(x['values'][0], x['values'][1]))
                                        for x in query_day(sheets_service, rq_date, ranges)]
            text = f'' \
                   f'{s_calendar} Данни за дата \n' \
                   f'{s_chart} Мед {cw["Date"]}: \n' \
                   f'Offer: *{cw["Offer"]:,.2f}{s_dollar}*\n' \
                   f'3 month: *{cw["3mo"]:,.2f}{s_dollar}*\n' \
                   f'Stock: *{cw["Stock"]:}*\n' \
                   f'{s_chart} Злато {au["Date"]}: \n' \
                   f'AM: *{au["Gold AM"]:,.3F}{s_dollar}*\n' \
                   f'PM *{au["Gold PM"]:,.3F}{s_dollar}*\n' \
                   f'Average: *{au["Average"]:.3F}{s_dollar}*\n' \
                   f'{s_chart} Сребро {ag["Date"]}: \n *{ag["Silver"]:.4F}{s_dollar}*\n' \
                   f'{s_usd} BGN/USD {rates["Date"]}: *{rates["USD"]}*\n' \
                   f'{s_pound} BGN/GBP {rates["Date"]}: *{rates["GBP"]}*\n' \
                   f'{s_usd} BGN/CHF {rates["Date"]}: *{rates["CHF"]}*\n' \
                   f'{s_hv} Ел. енергия {power["Date"]}:\n' \
                   f'BGN: *{power["BGN"]:.2F}*\n' \
                   f'EUR: *{power["EUR"]:.2F}*\n' \
                   f'Volume *{power["Volume"]:.2F}*'
            return text
        else:
            ranges = ['rqpower']
            x = query_day(sheets_service, rq_date, ranges)[0].get('values')
            power = dict(zip(x[0], x[1]))
            text = f'' \
                   f'{s_calendar} Данни за ({days[day_num]}) \n' \
                   f'{s_hv} Ел. енергия {power["Date"]}:\n' \
                   f'BGN: *{power["BGN"]:.2F}*\n' \
                   f'EUR: *{power["EUR"]:.2F}*\n' \
                   f'Volume *{power["Volume"]:.2F}*'
            return text
    except KeyError as e:
        bot_logger.info("Failed to build request msg.")
        return e
