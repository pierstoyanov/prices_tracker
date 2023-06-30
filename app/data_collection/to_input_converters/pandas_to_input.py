import pandas as pd
from datetime import datetime


def power_soup_to_data(response, last_date):
    df = pd.read_html(response.content)[0]
    groups = df.groupby(df.Date)
    last_date = datetime.strptime(last_date, "%d.%m.%Y")

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
