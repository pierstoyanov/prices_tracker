## PricesTracker

#### :page_facing_up: Description
PricesTracker is a Python/Flask app for daily data scraping and delivery to Viber bot.

#### :computer: Technologies and Libraries Used
    
- ***web framework***: flask
- ***database***: google sheets, sheets api, gspread
- ***web scraping***: playwright, requests
- ***data manipulation***: beautifulsoup4, pandas

#### :bookmark_tabs: Packages and modules in the app
    Modules:
    main.py - flask route entry point
    request_handlers.py - handlers for flask routes
    cron.yaml - sets up cron jobs for GAE

<details>
<summary>bot</summary>
<br>
user management, message generation, custom viber keyboards
<br>
</details>

<details>
<summary>data_collection</summary>
<br>
scraping, extraction and storage of data
</details>

<details>
<summary>google_sheets</summary>
<br>
handles google Sheets API and gspread lib
</details>

<details>
<summary>logger</summary>
<br>
manages logging with logging module / google cloud logging
</details>

<details>
<summary>scheduler</summary>
<br>
for scheduling tasks in conatinerized environment.
For GAE deployment scheduling is done with GAE scheduler/cron.yaml
</details>