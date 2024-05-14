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


class PowerSoupToPandasToData:
    def __init__(self, response, last_date_gsheet=None, last_date_fb=None):
        self.groups = self.create_groups(response)
        self.last_date_gsheets = self.convert_gsheet_date(last_date_gsheet)
        self.last_date_fb = last_date_fb

    def create_groups(self, response):
        df = pd.read_html(response.content)[0]
        return df.groupby(df.Date)
    
    def convert_gsheet_date(self, date):
        return datetime.strptime(date, "%d.%m.%Y")

    def convert_for_gsheets(self):
        """ Convert the dataframe to a list of lists for input to gsheets """
        result = []

        for key in sorted(self.groups.groups.keys()):
            day = datetime.strptime(key, "%Y-%m-%d")
            if self.last_date_gsheets and day <= self.last_date_gsheets:
                continue

            dfi = self.groups.get_group(key)
            bgn = dfi.get("Price (BGN)").mean() / 100
            eur = dfi.get("Price (EUR)").mean() / 100
            vol = dfi.get("Volume").sum() / 10
            result.append([day.strftime('%d.%m.%Y'), bgn, eur, vol])

        return result

    def convert_for_fb(self):
        """ Convert the dataframe to dict for firebase """
        result = {}

        for key in sorted(self.groups.groups.keys()):
            day = datetime.strptime(key, "%Y-%m-%d")
            if self.last_date_fb and day <= self.last_date_fb:
                continue

            dfi = self.groups.get_group(key)
            bgn = dfi.get("Price (BGN)").mean() / 100
            eur = dfi.get("Price (EUR)").mean() / 100
            vol = dfi.get("Volume").sum() / 10
            result.update({
            day.strftime("%Y-%m-%d"): {
                'd': day.strftime("%Y-%m-%d"), 
                'BGN': bgn, 
                'EUR': eur, 
                'VOL': vol
            }})
        
        return result
