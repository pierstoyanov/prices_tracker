import os

from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page


def new_page_browser(p):
    browser = p.chromium.launch()
    page = browser.new_page()
    return browser, page


def page_save_screenshot_pdf(page: Page, screenshot=False, pdf=False):
    if screenshot:
        page.screenshot(path='./screenshot.png', full_page=True)

    if pdf:
        page.pdf(path='./page.pdf')


def repl_comma_dot(s: str):
    return s.replace(',', '').replace('.', ',')


def get_url_contents(url: str, load_state=None, wait_selector=None, screenshot=False, pdf=False):
    with sync_playwright() as p:
        browser, page = new_page_browser(p)
        page.goto(url)

        if wait_selector:
            page.wait_for_selector(wait_selector)

        if load_state:
            page.wait_for_load_state(load_state)

        page_save_screenshot_pdf(page, screenshot, pdf)

        soup = BeautifulSoup(page.content(), 'html.parser')
        browser.close()
    return soup


def get_click_url_contents(url: str, load_state=None, wait_selector=None, click_locators=list(), screenshot=False, pdf=False):
    with sync_playwright() as p:
        browser, page = new_page_browser(p)
        page.goto(url)

        if wait_selector:
            page.wait_for_selector(wait_selector)

        if load_state:
            page.wait_for_load_state(load_state)

        if click_locators:
            for clk in click_locators:
                page.locator(clk).click()
                # page.screenshot(path='./screenshot.png', full_page=True)

        page_save_screenshot_pdf(page, screenshot, pdf)

        soup = BeautifulSoup(page.content(), 'html.parser')
        browser.close()
    return soup


def cu_soup_to_data(soup: BeautifulSoup):
    try:
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

    except AttributeError:
        return 'Element not found in soup!'


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


def au_soup_to_data(soup: BeautifulSoup):
    row = find_row(soup)
    date = datetime.strptime(row[0].text, '%d-%m-%Y').date().strftime('%d.%m.%Y')
    am, pm = repl_comma_dot(row[1].text), repl_comma_dot(row[2].text)
    return date.__str__(), am, pm


def ag_soup_to_data(soup: BeautifulSoup):
    row = find_row(soup)
    date = datetime.strptime(row[0].text, '%d-%m-%Y').date().strftime('%d.%m.%Y')
    ag_price = repl_comma_dot(row[1].text)
    return date.__str__(), ag_price
