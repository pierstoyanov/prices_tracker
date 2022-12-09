import os

from data_enter import add_daily_row
from data_gather import get_url_contents, cu_soup_to_data, au_soup_to_data, get_click_url_contents, ag_soup_to_data, \
    wm_soup_to_data

load_states = ['load', 'domcontentloaded', 'networkidle']

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # cu
    cu_wait = 'td[class=data-set-table__main]'
    cu_soup = get_url_contents(os.environ["URL_ONE"], load_states[2])
    cu_data = cu_soup_to_data(cu_soup)
    res = add_daily_row('copper', cu_data)
    print(res)

    # wm
    wm_wait = "div[class=year]"
    wm_soup = get_url_contents(os.environ["URL_THREE"], load_state=load_states[2])
    wm_data = wm_soup_to_data(wm_soup)
    res = add_daily_row('copperwm', wm_data)
    print(res)

    # au
    au_wait = "td[class=-index0]"
    au_soup = get_url_contents(os.environ["URL_TWO"], wait_selector=au_wait)
    au_data = au_soup_to_data(au_soup)
    res = add_daily_row('gold', au_data, average=True)
    print(res)

    # ag
    # ag_wait = "td[class=-index0]"
    ag_click = ['div.metals-dropdown li', 'ul.dropdown-menu >> text=Silver']
    ag_soup = get_click_url_contents(os.environ["URL_TWO"],
                                     load_state=load_states[2],
                                     click_locators=ag_click)
    ag_data = ag_soup_to_data(ag_soup)
    res = add_daily_row('silver', ag_data)
    print(res)
