from bs4 import BeautifulSoup as bs
from datetime import datetime
import requests as requests
import math
import re


def get_num_pages(books_per_page, url):
    """This function takes in the number of books per page on the goodreads to-reads list
    and and finds the number of pages to scrape.
    This is done by finding the total number of books on the list and dividing that by the number of books per page."""

    p = requests.get(url)
    s = bs(p.content, "html.parser")
    title = s.find("title").get_text()
    num_pages = float(re.search(r"[0-9]+", title).group(0))
    return math.ceil(num_pages/books_per_page)


def get_links_images(soup):
    """This function takes in the html soup
    and returns a tuple containing a list of book urls and src links for images"""

    book_covers = soup.find_all("td", class_="field cover")
    book_urls = [cover.find("a")["href"] for cover in book_covers]
    book_urls_complete = ["https://goodreads.com"+book_u for book_u in book_urls]
    book_imgs = [covers.find("img")["src"] for covers in book_covers]
    book_imgs_complete = [img.replace(re.search("._[a-zA-Z0-9]+_", img).group(0), "").replace("compressed.", "") for img in book_imgs]
    return book_urls_complete, book_imgs_complete


def get_titles_authors(soup):
    """This function takes in the html soup of a goodreads to-read list
        and returns a tuple containing a list of book titles and authors"""

    titles_soup = soup.find_all('td', class_='field title')
    authors_soup = soup.find_all('td', class_='field author')
    titles_2 = [title.get_text().strip("title").strip().replace("\n", "").replace("       ", "") for title in titles_soup]
    # due to a quirk in the json reader in javascript need to add a backslash to all '.
    titles_3 = [title.replace("'", f"") for title in titles_2]
    authors = [author.get_text().strip().replace("\n*", "").replace("author ", "").split(",") for author in
               authors_soup]
    authors_2 = [f"{author[1]} {author[0]}" if len(author) >= 2 else f"{author[0]}" for author in authors]

    return titles_3, authors_2


def get_dates(soup):
    """This function takes in the html soup of a goodreads to-read list
        and returns a list of publication dates of the chosen editions"""
    pub_date_edition_soup = soup.find_all("td", class_="field date_pub_edition")
    pub_date_edition = [date.get_text().replace("date pub edition      ", "").strip() for date in pub_date_edition_soup]
    pub_date_edition = [f"{datetime.now().year + 5}" if date == "date pub edition unknown" else date for date in pub_date_edition]
    return pub_date_edition


def get_all_info(soup):
    """This function takes in soup and a nested list of titles, authors, pub_dates, links and covers"""

    titles = get_titles_authors(soup)[0]
    authors = get_titles_authors(soup)[1]
    pub_dates = get_dates(soup)
    links = get_links_images(soup)[0]
    covers = get_links_images(soup)[1]
    return titles, authors, pub_dates, links, covers
