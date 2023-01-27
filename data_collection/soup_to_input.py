from datetime import datetime
from functools import wraps
from bs4 import BeautifulSoup


# convert soup to data for storing
def attribute_not_found_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AttributeError:
            return 'Element not found in soup!'
    return wrapper


def repl_comma_dot(s: str):
    return s.replace(',', '').replace('.', ',')


@attribute_not_found_decorator
def cu_soup_to_data(soup: BeautifulSoup):
    date_div = 'data-set-tabs__content-top'
    text = soup.find('div', date_div).find_all('span')[2].text
    date_str = text.split('for', 1)[1].strip()
    raw_date = datetime.strptime(date_str.strip(), "%d %b %Y")
    date = raw_date.date().strftime('%d.%m.%Y')

    prices_table = soup.find('table', class_="data-set-table__table").find('tbody').find_all('tr')
    first_row = prices_table[0]
    bid = repl_comma_dot(first_row.find('td', attrs={'data-table-column-header': 'Bid'}).text.strip())
    offer = repl_comma_dot(first_row.find('td', attrs={'data-table-column-header': 'Offer'}).text.strip())

    stock_td = soup.find('td', attrs={'data-table-column-header': "Amount"})
    stock = stock_td.text.strip()
    return date.__str__(), bid, offer, stock


def wm_all_soup_to_data(wm: BeautifulSoup):
    removal = wm.find_all('tr', attrs={'class': "shaded"})
    for tr in removal:
        tr.decompose()

    table = wm.find_all('tr')
    result = []

    for tr in table:
        row = tr.find_all('td')
        date = datetime.strptime(row[0].text, '%d. %B %Y').date().strftime('%Y.%m.%d')
        cash, three_mt, stock = repl_comma_dot(row[1].text), repl_comma_dot(row[2].text), repl_comma_dot(row[3].text)
        result.append([date, cash, three_mt, stock])

    result.reverse()
    return result


@attribute_not_found_decorator
def wm_soup_to_data(wm: BeautifulSoup):
    row = wm.find('tbody').find('tr').find_all('td')
    date = datetime.strptime(row[0].text, '%d. %B %Y').date().strftime('%d.%m.%Y')
    cash, three_mt, stock = repl_comma_dot(row[1].text), repl_comma_dot(row[2].text), repl_comma_dot(row[3].text)
    return date.__str__(), cash, three_mt, stock


def td_tag_selector(tag):
    # custom tag filter
    return tag.name == 'td' and tag.has_attr("class")


def find_row(soup: BeautifulSoup):
    return soup.find('tbody').find('tr').find_all('td')


@attribute_not_found_decorator
def au_soup_to_data(soup: BeautifulSoup):
    row = find_row(soup)
    date = datetime.strptime(row[0].text, '%d-%m-%Y').date().strftime('%d.%m.%Y')
    am, pm = repl_comma_dot(row[1].text), repl_comma_dot(row[2].text)
    return date.__str__(), am, pm


@attribute_not_found_decorator
def ag_soup_to_data(soup: BeautifulSoup):
    row = find_row(soup)
    date = datetime.strptime(row[0].text, '%d-%m-%Y').date().strftime('%d.%m.%Y')
    ag_price = repl_comma_dot(row[1].text)
    return date.__str__(), ag_price


@attribute_not_found_decorator
def bnb_soup_to_data(soup: BeautifulSoup):
    div = soup.find('div', id="more_information")
    date = div.find('h4').text.split('за', 1)[1].strip()
    usd, gbp, chf = [repl_comma_dot(x.text.split(' ')[0]) for x in div.find_all('strong')[:3]]
    return date, usd, gbp, chf
