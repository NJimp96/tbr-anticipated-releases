import os.path

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import goodreadsscraperfunctions as gsf
from selenium_stealth import stealth
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import requests as requests
import datetime as dt
import pandas as pd
import time
import json
import re

URL_TEMPLATE = "https://www.goodreads.com/review/list/8683189-ne?page=1&shelf=to-read"
#"https://www.goodreads.com/review/list/4622890-emily-may?page=2&shelf=read""
#"https://www.goodreads.com/review/list/8683189-ne?utf8=%E2%9C%93&shelf=to-read&utf8=%E2%9C%93&title=ne&per_page=30"
NUM_BOOKS_PER_PAGE = 20

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")

# options.add_argument("--headless")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

chrome_install = ChromeDriverManager().install()
folder = os.path.dirname(chrome_install)
chrome_driver_path = os.path.join(folder, "chromedriver.exe")
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )


def scrape_tbr(url_temp):
    """This functions scrapes through a good reads book list and writes to json file sample_data with the
    list of books released in the past 30 days. Book data contains author, title, cover url, book url and
    the publication date of the chosen edition"""

    # initialise master lists and get number of pages of tbr
    master_dict = {"Title": [], "Author": [], "Date": [], "Link": [], "Cover": []}
    print(URL_TEMPLATE)
    driver.get(URL_TEMPLATE)
    # time.sleep(5)
    soup_1 = bs(driver.page_source, 'html.parser')
    num_tbr_pages = gsf.get_num_pages(NUM_BOOKS_PER_PAGE, soup_1)

    # loop through each page of tbr list for book data
    for i in range(2, num_tbr_pages+1):

        # update the url with new page number and get soup
        url = re.sub(r"page=[0-9]+", f"page={i}", url_temp)
        driver.get(url)
        # time.sleep(5)
        html_soup = bs(driver.page_source, 'html.parser')
        print(i, end=", ")

        # add data to master lists
        for count, column in enumerate(master_dict):
            master_dict[column].extend(gsf.get_all_info(html_soup)[count])

    # turn master list into a pandas dataframe and convert date to datetime
    books_info = pd.DataFrame.from_dict(master_dict)
    books_info.loc[:, "Date"] = pd.to_datetime(books_info.loc[:, "Date"])
    books_info = books_info.sort_values(by=["Date"], ignore_index=True)

    # create dataframes for books released in the past month and in the upcoming week
    today = pd.to_datetime([dt.datetime.now().date()])
    day_30 = pd.to_datetime(today - dt.timedelta(days=30))
    day_7 = pd.to_datetime(today + dt.timedelta(days=7))
    books_month = books_info.loc[(books_info["Date"] >= day_30[0]) & (books_info["Date"] <= today[0])].reset_index(drop=True)
    books_week = books_info.loc[(books_info["Date"] <= day_7[0]) & (books_info["Date"] >= today[0])].reset_index(drop=True)

    books_dfs = {"full_tbr": books_info, "tbr_past_month": books_month, "tbr_coming_week": books_week}

    # convert date column in dataframes to string; convert dataframes to json and write to file
    for title, df in books_dfs.items():
        df["Date"] = df["Date"].dt.strftime("%b %d, %Y")
        json_data = json.dumps(df.to_dict(orient="records"))
        with open(f"../data/{title}.json", "w") as f:
            f.write(json_data)

    driver.quit()

    return books_info, books_month, books_week


scrape_tbr(URL_TEMPLATE)
