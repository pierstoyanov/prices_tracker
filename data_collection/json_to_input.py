from datetime import datetime


def cu_jsons_to_input(jsons: list):
    prices, three_mo = jsons[0].get('Rows')[0], jsons[0].get('Rows')[1],
    raw_date = prices.get('BusinessDateTime').split('T')[0]
    date = datetime.strptime(raw_date, "%Y-%m-%d").strftime('%d.%m.%Y')
    offer, offer_tmo = prices.get('Values')[1], three_mo.get('Values')[1]

    stocks = jsons[1].get('Rows')[0]
    stocks_date = stocks.get('BusinessDateTime').split('T')[0]
    stock_value = stocks.get('Values')[0]

    if raw_date != stocks_date:
        raise AttributeError('Date match error')
    return [date, offer.replace('.', ','), offer_tmo.replace('.', ','), stock_value]


def au_json_to_input(jsons: list):
    am, pm = jsons[0][-1], jsons[1][-1]
    am_date, pm_date = am.get('d'), pm.get('d')

    if am_date != pm_date:
        raise AttributeError('Date match error')

    date = datetime.strptime(am_date, "%Y-%m-%d").strftime('%d.%m.%Y')
    am_val, pm_val = am.get('v')[0], pm.get('v')[0]

    return [date, am_val, pm_val]


def ag_json_to_input(jsons: list):
    ag = jsons[0][-1]
    date = datetime.strptime(ag.get('d'), "%Y-%m-%d").strftime('%d.%m.%Y')
    ag_val = ag.get('v')[0]

    return [date, ag_val]
