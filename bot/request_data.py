import os
from datetime import datetime

from bot.bot import sheets_service, bot_logger
from g_sheets.google_api_operations import get_multiple_named_ranges, update_values_in_sheet


def test_date(c, cw, au, ag):
    if c['Date'] == cw['Date'] and cw['Date'] == au['Date'] and au['Date'] == ag['Date']:
        return '\u2705'
    else:
        return '\u274C'


def query_day(service, rq_date):
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

    ranges = ['rqwmcu', 'rqau', 'rqag', 'rqrates', 'rqpower']

    result = get_multiple_named_ranges(service=service,
                                       spreadsheet_id=spreadsheet_id,
                                       named_ranges=ranges,
                                       value_render_option='UNFORMATTED_VALUE',
                                       date_time_render_option='FORMATTED_STRING'
                                       ).get('valueRanges')

    return result


def build_requested_day_info(rq_day: str):
    try:
        rq_date = datetime.strptime(rq_day.strip(), '%d-%m-%Y').strftime('%d.%m.%Y')

        cw, au, ag, rates, pow = [dict(zip(x['values'][0], x['values'][1]))
                                  for x in query_day(sheets_service, rq_date)]

        s_chart, s_dollar, s_calendar, s_usd, s_pound, s_hv = \
            '\U0001F4C8', '\U0001F4B2', '\U0001F4C5', '\U0001F4B5', '\U0001F4B7', '\U000026A1'

        text = f'' \
               f'{s_calendar} Данни за дата: \n' \
               f'{s_chart} {cw["Date"]} Мед\n' \
               f'Offer: *{cw["Offer"]:,.2f}{s_dollar}*\n' \
               f'3 month: *{cw["3mo"]:,.2f}{s_dollar}*\n' \
               f'Stock: *{cw["Stock"]:}*\n' \
               f'{s_chart} {au["Date"]} Злато\n' \
               f'AM: *{au["Gold AM"]:,.3F}{s_dollar}*\n' \
               f'PM *{au["Gold PM"]:,.3F}{s_dollar}*\n' \
               f'Average: *{au["Average"]:.3F}{s_dollar}*\n' \
               f'{s_chart} {ag["Date"]} Сребро \n *{ag["Silver"]:.4F}{s_dollar}*\n' \
               f'{s_usd} {rates["Date"]} BGN/USD: *{rates["USD"]}*\n' \
               f'{s_pound} {rates["Date"]} BGN/GBP: *{rates["GBP"]}*\n' \
               f'{s_usd} {rates["Date"]} BGN/CHF: *{rates["CHF"]}*\n' \
               f'{s_hv} {rates["Date"]}  Ел. енергия \n' \
               f'BGN: *{pow["BGN"]:.2F}*\n' \
               f'EUR: *{pow["EUR"]:.2F}*\n' \
               f'Volume *{pow["Volume"]:.2F}*'

        return text
    except KeyError as e:
        bot_logger.info("Failed to build request msg.")
        return e
