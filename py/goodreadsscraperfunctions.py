from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from datetime import *
import requests as requests
import math
import re


def get_num_pages(books_per_page, soup):
    """This function takes in the number of books per page on the goodreads to-reads list
    and finds the number of pages to scrape.
    This is done by finding the total number of books on the list and dividing that by the number of books per page."""

    s = soup
    title = s.find("title").get_text()
    print(title)
    num_pages = float(re.search(r"[0-9]+", title).group(0))
    print(num_pages)
    return math.ceil(num_pages/books_per_page)


def get_links_images(soup):
    """This function takes in the html soup
    and returns a tuple containing a list of book urls and src links for images"""

    book_covers = soup.find_all("td", class_="field cover")

    book_urls = []
    book_imgs = []
    for cover in book_covers:
        url = "https://goodreads.com" + cover.find("a")["href"]
        img = cover.find("img")["src"]
        if "nophoto" not in img:
            img = img.replace(re.search("._[a-zA-Z0-9]+_", img).group(0), "").replace("compressed.", "")
        book_urls.append(url)
        book_imgs.append(img)

    return book_urls, book_imgs


def get_titles_authors(soup):
    """This function takes in the html soup of a goodreads to-read list
        and returns a tuple containing a list of book titles and authors"""

    titles_soup = soup.find_all('td', class_='field title')
    authors_soup = soup.find_all('td', class_='field author')

    authors = []
    titles = [title.get_text().strip("title").strip().replace("\n", "").replace("       ", "").replace("'", f"")
              for title in titles_soup]

    for author in authors_soup:
        author = author.get_text().strip().replace("\n*", "").replace("author ", "").split(",")
        if len(author) >= 2:
            author = f"{author[1]} {author[0]}"
        else:
            author = author[0]

        authors.append(author)

    return titles, authors


def get_dates(soup):
    """This function takes in the html soup of a goodreads to-read list
        and returns a list of publication dates of the chosen editions"""
    pub_date_edition_soup = soup.find_all("td", class_="field date_pub_edition")
    pub_date_edition = []

    for new_date in pub_date_edition_soup:
        new_date = new_date.get_text().replace("date pub edition      ", "").strip()
        if new_date == "date pub edition unknown":
            new_date = date.today() + (5 * timedelta(days=365))
            new_date = new_date.strftime("%b %d, %Y")
        elif "," not in new_date and not new_date.isnumeric():
            new_date = new_date[:3] + ' 01, ' + new_date[4:]
        elif new_date.isnumeric():
            new_date = "Jan 01, " + new_date

        pub_date_edition.append(datetime.strptime(new_date, "%b %d, %Y"))

    return pub_date_edition


def get_all_info(soup):
    """This function takes in soup and a nested list of titles, authors, pub_dates, links and covers"""

    titles = get_titles_authors(soup)[0]
    authors = get_titles_authors(soup)[1]
    pub_dates = get_dates(soup)
    links = get_links_images(soup)[0]
    covers = get_links_images(soup)[1]
    return titles, authors, pub_dates, links, covers
