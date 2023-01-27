import pandas as pd
from datetime import datetime
from g_sheets.google_api_operations import get_multiple_named_ranges


def power_soup_to_data(response, service, sh_id):
    df = pd.read_html(response.content)[0]
    groups = df.groupby(df.Date)

    last = get_multiple_named_ranges(
        service=service,
        spreadsheet_id=sh_id,
        named_ranges=['power'],
        value_render_option='UNFORMATTED_VALUE',
        date_time_render_option='FORMATTED_STRING'
    ).get('valueRanges')[0].get('values')

    last_data = dict(zip(last[0], last[1]))
    last_date = datetime.strptime(last_data.get('Date'), "%d.%m.%Y")

    result = []
    for key in sorted(groups.groups.keys()):
        day = datetime.strptime(key, "%Y-%m-%d")
        if day <= last_date:
            continue

        dfi = groups.get_group(key)
        bgn = dfi.get("Price (BGN)").mean() / 100
        eur = dfi.get("Price (EUR)").mean() / 100
        vol = dfi.get("Volume").sum() / 10
        result.append([day.strftime('%d.%m.%Y'), bgn, eur, vol])

    return result
