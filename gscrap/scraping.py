import requests
import re
import datetime

import pandas as pd
import yalm

from bs4 import BeautifulSoup
from pathlib import Path
from typing import List
from gscrap.selenium_steam import steam_scrapper

# Not the most descriptive name.. TODO(fer): Find a better name
func_map = {
        'title': get_title,
        'price': get_price,
        'discount': get_discount,
        'store': get_store,
        'region': get_region,
        'dlc': get_dlc,
        'url': get_url,
        'platform': get_platform,
        'availability': get_availability,
        'release': get_release,
        'comment': get_comment,
        'rating': get_rating,
        'genre': get_genre,
        }


def save_background(dir_path: str = ".", store: str = "insta-gaming"):
    """Saves the background image of the page to the dir_path with the name `store_background.jpg."""
    background_url = re.findall(
        "http.*?jpg", soup.find("div", {"id": "backgroundLink"})["style"])[0]
    background_imagen = requests.get(background_url)
    with open("background.jpg", "wb") as f:
        f.write(background_imagen.content)


def get_games(store, soup):
    if store == "insta-gaming":
        games = soup.find_all("div", class_=["category-best", "item mainshadow"])
    else:
        games = []
    for game in games:
        yield game


def get_title(game: str, store: str) -> str:
    if store == "insta-gaming":
        return game.find("div", class_="name").text

    else:
        return 'Untitled'

def get_price(game, store):
    if store == 'insta-gaming':
        price = re.findall("\d+\.?\d+",
                           game.find("div", class_="price").text)[0]
    return price

def get_discount(game, store):
    if store == 'insta-gaming':
        return game.find("div", class_="discount").text
    else:
        return f'Discount not implemented for {store}'

def save_game_cover(game, path, store):
    imagen_url = game.find("img", class_="picture mainshadow").get("src")

    imagen = requests.get(imagen_url)
    with open(folder_name + "/" + str(numero_id) + ".jpg", "wb") as f:
        f.write(imagen.content)

def get_store(game, store):
    return store

def get_region(game, store):
    if store == 'insta-gaming':
        return game["data-region"]

def get_dlc(game, store):
    if store == 'insta-gaming':
        return game['data-dlc']

def get_url(game, store):
    if store == 'insta-gaming':
        return game.a['href']

def get_platform(game, store):
    pass

def get_availability(game, store):
    pass

def get_release(game, store):
    pass

def get_comment(game, store):
    pass

def get_rating(game, store):
    pass

def get_genre(game, store):
    pass

next_page_exists(soup, store):
    if store == 'instant-gamming':
        return soup.find(class_="pagination bottom").find_all("li")[-1].text == '>'
    else:
        return False

load_next_page(soup):
    if store == 'instant-gamming':
        last_element = soup.find(class_="pagination bottom").find_all("li")[-1]
        next_url = last_element.find('a')['href']
        url = base_link + next_url
        source = requests.get(url)
        return BeautifulSoup(source.content)

def get_info(col):
    """Wrapper for the mapping of function to avoid raising exceptions"""
    # TODO: Here there should be a way to handle new soups? I dunno.
    try:
        value = func_map[col]
    except NameError:
        raise NameError(f'{col} is not a possible column name')
    except:
        value = 'Not found'
    finally:
        return value

def scrap_games(*stores, cols=[], background=False):

    df = pd.DataFrame(columns=cols)

    for store in stores:
        base_url = config[store]["base_url"]
        cat_url = config[store]["catalog_url"]
        url = base_link + page_link

        soup = BeautifulSoup(requests.get(url))

        if background:
            save_background(output_path, store=store)

        while True: #TODO(fer): Look for something better? (max_pages?)

            for game in get_games(store, soup):
                df.append({col:func_map[col](game, store) for col in cols})

            if next_page_exists(soup, store):
                soup = load_next_page(soup, store)
            else:
                break

    df.to_csv('test.csv')
