import os

from bot.bot import sheets_service, bot_logger
from g_sheets.google_api_operations import get_multiple_named_ranges


def test_date(c, cw, au, ag):
    if c['Date'] == cw['Date'] and cw['Date'] == au['Date'] and au['Date'] == ag['Date']:
        return '\u2705'
    else:
        return '\u274C'


def get_daly():
    spreadsheet_id = os.environ['SPREADSHEET_DATA']
    ranges = ['cudaly', 'cuwmdaly', 'audaly', 'agdaly', 'rates', 'power']
    result = get_multiple_named_ranges(service=sheets_service, spreadsheet_id=spreadsheet_id,
                                       named_ranges=ranges,
                                       value_render_option='UNFORMATTED_VALUE',
                                       date_time_render_option='FORMATTED_STRING'
                                       ).get('valueRanges')

    return result


def build_daly_info():
    try:
        c, cw, au, ag, rates, pow = [dict(zip(x['values'][0], x['values'][1])) for x in get_daly()]
        date_status = test_date(c, cw, au, ag)
        s_chart, s_dollar, s_calendar, s_usd, s_pound, s_hv \
            = '\U0001F4C8', '\U0001F4B2', '\U0001F4C5', '\U0001F4B5', '\U0001F4B7', '\U000026A1'

        text = f'' \
               f'{s_calendar} Дата: {c["Date"]}\n {date_status}\n' \
               f'{s_chart}Мед\n' \
               f'Offer: *{c["Offer"]:,.2f}{s_dollar}*\n' \
               f'3 month: *{c["3mo"]:,.2f}{s_dollar}*\n' \
               f'Stock: *{c["Stock"]:}*\n'\
               f'{s_chart} Злато\n' \
               f'AM: *{au["Gold AM"]:,.3F}{s_dollar}*\n' \
               f'PM *{au["Gold PM"]:,.3F}{s_dollar}*\n' \
               f'Average: *{au["Average"]:.3F}{s_dollar}*\n' \
               f'{s_chart} Сребро *{ag["Silver"]:.4F}{s_dollar}*\n' \
               f'{s_usd} BGN/USD: *{rates["USD"]}*\n' \
               f'{s_pound} BGN/GBP: *{rates["GBP"]}*\n' \
               f'{s_usd} BGN/CHF: *{rates["CHF"]}\n*' \
               f'{s_hv} Ел. енергия\n' \
               f'BGN: {pow["BGN"]}\n' \
               f'EUR: {pow["EUR"]}\n' \
               f'Volume {pow["Volume"]}'

        return text
    except KeyError as e:
        bot_logger.info("Failed to build daly msg.")
        return e
