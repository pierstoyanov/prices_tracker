import playwright.sync_api
from playwright.sync_api import sync_playwright


def new_page_browser(p, url):
    browser = p.chromium.launch()
    page = browser.new_page_browser()
    return page.goto(url), browser


def page_save(page: playwright.sync_api.Page, screenshot=False, pdf=False):
    if screenshot:
        page.screenshot(path='./screenshot.png', full_page=True)

    if pdf:
        page.pdf(path='./page.pdf')
