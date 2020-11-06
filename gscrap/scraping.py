# TODO: Add documentation EVERYWHERE
# TODO: Add type hinting EVERYWHERE

import requests
import re
from tqdm.auto import tqdm
from pandas import DataFrame
from yaml import load, Loader
from bs4 import BeautifulSoup
from bs4.element import Tag
from gscrap.selenium_steam import steam_scrapper

from typing import List, Generator

def get_games(store: str, soup: BeautifulSoup) -> Generator[None, Tag, None]:
    if store == "instant-gaming":
        games = soup.find_all("div", class_=["category-best", "item mainshadow"])
    else:
        games = []
    for game in games:
        yield game


def get_title(game: Tag, store: str) -> str:
    if store == "instant-gaming":
        return game.find("div", class_="name").text

    return f'{store} not implemented'


def get_price(game: Tag, store: str) -> str:
    if store == "instant-gaming":
        return re.findall("\d+\.?\d+", game.find("div", class_="price").text)[0]
    return f'{store} not implemented'

def get_discount(game: Tag, store: str) -> str:
    if store == "instant-gaming":
        return game.find("div", class_="discount").text
    return f"Discount not implemented for {store}"


def get_store(game: Tag, store: str) -> str:
    return store


def get_region(game: Tag, store: str) -> str:
    if store == "instant-gaming":
        return game["data-region"]
    return f'{store} not implemented'

def get_dlc(game: Tag, store: str) -> str:
    if store == "instant-gaming":
        return game["data-dlc"]
    return f'{store} not implemented'

def get_url(game: Tag, store: str) -> str:
    if store == "instant-gaming":
        return game.a["href"]
    return f'{store} not implemented'


def get_platform(game: Tag, store: str) -> str:
    pass


def get_availability(game: Tag, store: str) -> str:
    pass


def get_release(game: Tag, store: str) -> str:
    pass


def get_comment(game: Tag, store: str) -> str:
    pass


def get_rating(game: Tag, store: str) -> str:
    pass


def get_genre(game: Tag, store: str) -> str:
    pass


# Not the most descriptive name.. TODO(fer): Find a better name
func_map = {
    "title": get_title,
    "price": get_price,
    "discount": get_discount,
    "store": get_store,
    "region": get_region,
    "dlc": get_dlc,
    "url": get_url,
    "platform": get_platform,
    "availability": get_availability,
    "release": get_release,
    "comment": get_comment,
    "rating": get_rating,
    "genre": get_genre,
}


def next_page_exists(soup: BeautifulSoup, store: str) -> bool:
    if store == "instant-gaming":
        return soup.find(class_="pagination bottom").find_all("li")[-1].text == ">"
    else:
        return False


def load_next_page(soup: BeautifulSoup, store: str, base_url: str) -> BeautifulSoup:
    if store == "instant-gaming":
        last_element = soup.find(class_="pagination bottom").find_all("li")[-1]
        next_url = last_element.find("a")["href"]
        url = base_url + next_url
        source = requests.get(url)
        return BeautifulSoup(source.content, "html.parser")


def get_info(col: str, game: Tag, store: str) -> str:
    """Wrapper for the mapping of function to avoid raising exceptions"""
    # TODO: Here there should be a way to handle new soups? I dunno.
    try:
        value = func_map[col](game, store)
    except NameError:
        raise NameError(f"{col} is not a possible column name")
    except:
        value = "Not found"
    finally:
        return value


def scrap_games(*stores: str, cols: List[str]=[]):

    df = DataFrame(columns=cols)

    with open("config.ylm", "r") as c:
        config = load(c, Loader=Loader)

    pb_stores = tqdm(stores)
    for store in pb_stores:
        # TODO: Check if those entries exist on config yalm and make
        # meaningful error messages
        base_url = config[store]["base_url"]
        url =  base_url + config[store]["catalog_url"]

        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        page_num = 1
        while True:  # TODO(fer): Look for something better? (max_pages?)
            pb_stores.set_description(f"page {page_num} in {store}")
            for game in get_games(store, soup):
                df = df.append(
                    {col: get_info(col, game, store) for col in cols}, ignore_index=True
                )

            if next_page_exists(soup, store):
                soup = load_next_page(soup, store, base_url)
            else:
                break

            page_num += 1

    return df
