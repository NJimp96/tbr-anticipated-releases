import goodreadsscraperfunctions as gsf
from bs4 import BeautifulSoup as bs
import requests as requests
import datetime as dt
import pandas as pd
import json
import re

URL_TEMPLATE = "https://www.goodreads.com/review/list/152889088-gs?&shelf=to-read&page=1"
NUM_BOOKS_PER_PAGE = 30


def scrape_tbr(url_temp):
    """This functions scrapes through a good reads book list and writes to json file sample_data with the
    list of books released in the past 30 days. Book data contains author, title, cover url, book url and
    the publication date of the chosen edition"""

    # initialise master lists and get number of pages of tbr
    master_dict = {"Title": [], "Author": [], "Date": [], "Link": [], "Cover": []}
    num_tbr_pages = gsf.get_num_pages(NUM_BOOKS_PER_PAGE, URL_TEMPLATE)

    # loop through each page of tbr list for book data
    for i in range(1, num_tbr_pages+1):

        # update the url with new page number and get soup
        url = re.sub(r"page=[0-9]+", f"page={i}", url_temp)
        page = requests.get(url)
        html_soup = bs(page.content, 'html.parser')

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
        with open(f"{title}.json", "w") as f:
            f.write(json_data)

    return books_info, books_month, books_week


scrape_tbr(URL_TEMPLATE)
