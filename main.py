import os
from datetime import datetime

import gspread
import pandas as pd
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright

from playwright_shortcuts import new_page_browser, page_save


def get_url_contents(url: str, wait_for_selector=None):
    with sync_playwright() as p:
        page, browser = new_page_browser(p, url)

        if wait_for_selector:
            page.wait_for_selector(wait_for_selector)

        page_save(page, False, False)

        soup = BeautifulSoup(page.content(), 'html.parser')

        date = datetime.strptime(soup.find('div', os.environ["DATE_DIV"]).find_all('span')[3]
                                 .text.strip(),
                                 "%d %b %Y").date()
        print(date)

        prices_table = soup.find('table', class_="data-set-table__table").find('tbody').find_all('tr')

        first_row = prices_table[0]
        contract = first_row.find('th', attrs={'data-table-column-header': 'Contract'}).text.strip()
        bid = first_row.find('td', attrs={'data-table-column-header': 'Bid'}).text.strip()
        offer = first_row.find('td', attrs={'data-table-column-header': 'Offer'}).text.strip()
        print(f'Period: {contract} Bid: {bid}, Offer: {offer}')

        page.close()
        browser.close()

    return [date, bid, offer]


def get_first_empty_row(s: gspread.spreadsheet.Spreadsheet.sheet1, cols_to_sample=2):
    cols = s.range(1, 1, s.row_count, cols_to_sample)
    return max([cell.row for cell in cols if cell.value]) + 1


def get_table():
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(f'{os.environ["KEYFILE_NAME"]}.json', scopes)
    client = gspread.authorize(credentials)
    sheet = client.open(os.environ['SHEET_NAME']).sheet1

    cur_row = get_first_empty_row(sheet)

    contents = get_url_contents(os.environ['TARGET_URL'], 'div[class=data-set-table__main]')
    print(cur_row, contents)
    sheet.add_rows(contents, cur_row)

    print(sheet.range('A1:C2'))


# get_table()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Main")
