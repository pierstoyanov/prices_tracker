# from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright, Page
#
#
# # collect data with playwright and return BeautifulSoup4 soup
# def new_page_browser(p):
#     """Open new browser with playwright
#     :returns: (browser, page) - playwright browser object, new page  """
#     browser = p.chromium.launch(headless=True)
#     page = browser.new_page()
#     return browser, page
#
#
# def page_save_screenshot_pdf(page: Page, screenshot=False, pdf=False):
#     if screenshot:
#         page.screenshot(path='./screenshot.png', full_page=True)
#
#     if pdf:
#         page.pdf(path='./page.pdf')
#
#
# def get_url_contents(url: str, load_state=None, wait_selector=None, screenshot=False, pdf=False):
#     with sync_playwright() as p:
#         browser, page = new_page_browser(p)
#         page.goto(url)
#
#         if wait_selector:
#             page.wait_for_selector(wait_selector)
#
#         if load_state:
#             page.wait_for_load_state(load_state)
#
#         page_save_screenshot_pdf(page, screenshot, pdf)
#
#         soup = BeautifulSoup(page.content(), 'html.parser')
#         browser.close()
#     return soup
#
#
# def get_click_url_contents(url: str, load_state=None, wait_selector=None, click_locators=None,
#                            screenshot=False, pdf=False):
#     if click_locators is None:
#         click_locators = []
#         with sync_playwright() as p:
#         browser, page = new_page_browser(p)
#         page.goto(url)
#
#         if wait_selector:
#             page.wait_for_selector(wait_selector)
#
#         if load_state:
#             page.wait_for_load_state(load_state)
#
#         if click_locators:
#             for clk in click_locators:
#                 page.locator(clk).click()
#                 # page.screenshot(path='./screenshot.png', full_page=True)
#
#         page_save_screenshot_pdf(page, screenshot, pdf)
#
#         soup = BeautifulSoup(page.content(), 'html.parser')
#         browser.close()
#     return soup
