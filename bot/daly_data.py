import os

from bot.bot import sheets_service
from g_sheets.google_api_operations import get_multiple_named_ranges


def test_date(c, cw, au, ag):
    if c['Date'] == cw['Date'] and cw['Date'] == au['Date'] and au['Date'] == ag['Date']:
        return '\u2705'
    else:
        return '\u274C'


def get_daly():
    spreadsheet_id = os.environ['SPREADSHEET_DATA']
    ranges = ['cudaly', 'cuwmdaly', 'audaly', 'agdaly']
    result = get_multiple_named_ranges(service=sheets_service, spreadsheet_id=spreadsheet_id,
                                       named_ranges=ranges,
                                       value_render_option='UNFORMATTED_VALUE',
                                       date_time_render_option='FORMATTED_STRING'
                                       ).get('valueRanges')

    return result


def build_daly_info():
    c, cw, au, ag = [dict(zip(x['values'][0], x['values'][1])) for x in get_daly()]
    date_status = test_date(c, cw, au, ag)
    chart, dollar, callendar = '\U0001F4C8', '\U0001F4B2', '\U0001F4C5'
    date = c['Date']
    text = f'{date_status}{callendar} Date: {date} \n'
    text += f'{chart}Cu\nBid: *{c["Bid"]:,.2f}{dollar}*\nOffer: *{c["Offer"]:,.2f}{dollar}*\nStock: *{c["Stock"]:,}*\n'
    text += f'{chart}Au\nAM: *{au["Gold AM"]:,.3F}{dollar}*\nPM *{au["Gold PM"]:,.3F}{dollar}*\n' \
            f'Average: *{au["Average"]:,.3F}{dollar}*\n'
    text += f'{chart}Ag\n*{ag["Silver"]:.4F}{dollar}*'

    # for i in daly_data:
    #     v = i.get('values')
    #     # values = dict(zip(v[0], v[1]))
    #     text += '\n'.join(f'{k}: {v:.3F}' for k, v in dict(zip(v[0], v[1])).items()) + '\n'
    return text
