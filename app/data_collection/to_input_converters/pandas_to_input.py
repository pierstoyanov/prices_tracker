import pandas as pd
from datetime import datetime
from io import BytesIO


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
        bgn = round(dfi.get("Price (BGN)").mean(), 5)
        eur = round(dfi.get("Price (EUR)").mean(), 5)
        vol = round(dfi.get("Volume").sum(), 5)
        result.append([day.strftime('%d.%m.%Y'), bgn, eur, vol])

    return result



class PowerSoupToPandasToData:
    def __init__(self, response, last_date_gsheet=None, last_date_fb=None):
        self.df_grouped = self.create_groups(response)
        self.last_date_gsheets = self.get_last_date(last_date_gsheet, "%d.%m.%Y")
        self.last_date_fb = self.get_last_date(last_date_fb, "%Y-%m-%d")

    def create_groups(self, response):

        html_bytes = BytesIO(response.content)

        df = pd.read_html(html_bytes, \
                            decimal=",",
                            thousands=" ", 
                            parse_dates=["Date"])[0]
        
        return df.groupby(df.Date)
    
    def get_last_date(self, date, format):
        return datetime.strptime(date, format) if date is not None else None

    def convert_for_gsheets(self):
        """ Convert the dataframe to a list of lists for input to gsheets """
        result = []

        for day in sorted(self.df_grouped.groups.keys()):
            if self.last_date_gsheets and day <= self.last_date_gsheets:
                continue

            dfi = self.df_grouped.get_group(day)
            bgn = round(dfi.get("Price (BGN)").mean(), 5)
            eur = round(dfi.get("Price (EUR)").mean(), 5)
            vol = round(dfi.get("Volume").sum(), 5) 
            result.append([day.strftime('%d.%m.%Y'), bgn, eur, vol])

        return result

    def convert_for_fb(self):
        """ Convert the dataframe to dict for firebase """
        result = {}

        for day in sorted(self.df_grouped.groups.keys()):
            if self.last_date_fb and day <= self.last_date_fb:
                continue

            dfi = self.df_grouped.get_group(day)
            bgn = round(dfi.get("Price (BGN)").mean(), 5)
            eur = round(dfi.get("Price (EUR)").mean(), 5)
            vol = round(dfi.get("Volume").sum(), 5)
            result.update({
            day.strftime("%Y-%m-%d"): {
                'd': day.strftime("%Y-%m-%d"), 
                'BGN': bgn, 
                'EUR': eur, 
                'VOL': vol
            }})
        
        return result
