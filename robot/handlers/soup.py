import datetime
from dataclasses import dataclass
from io import BytesIO
from random import sample
from typing import Any, Callable, Iterable, List

import telegram
import certifi
import pycurl
from bs4 import BeautifulSoup as bs

from ..config import MENU, REQUEST_TIMER, SOUP, SOUP_ENDPOINT, logger


EMOJIS_FOOD = [
    "🥕",
    "🥔",
    "🍞",
    "🍔",
    "🍟",
    "🍕",
    "🥘",
    "🍳",
    "🥚",
    "🫔",
    "🌯",
    "🌮",
    "🥪",
    "🌭",
    "🍲",
    "🍖",
    "🍗",
    "🥩",
]
VEGETARIAN_WORDS = {"veg", "vege", "vegetarien", "vegetarian"}

@dataclass
class Dish:
    prices: List[float]
    name_resto: str
    dish_name: str
    vegetarian: bool

    def __str__(self):
        return f"🍽️{'🥬' if self.vegetarian else '🍖'}<b> {min(self.prices)} CHF</b> - <i>{self.name_resto}</i> → {self.dish_name}."


class Menu:
    dishes: Iterable[Dish]

    def __init__(self, dishes: Iterable[Dish]):
        self.dishes = dishes
        self.filters = []

    def __str__(self):
        content = "\n".join(str(p) for p in self.dishes)
        if content:
            header = "{}{} <b>On mange quoi ?</b> {}{}".format(*sample(EMOJIS_FOOD, 4))
            return "{}\n\n{}".format(header, content)
        else:
            return "Pas de résultat correspondant aux filtres, c'est régime"

    @staticmethod
    def from_html(html):
        # removes non-Lausanne results
        excluded = set(["La Ruch", "Microci", "Hodler"])
        # handle edge case names
        alias = {"La Tabl": "Vallotton", "Maharaj": "Maharaja", "Satelli": "Sat"}
       
        soup = bs(html, "html.parser")
        content = soup.find_all("tr", {"class": "menuPage"})
        dishes = []
        for item in content:
            prices = []
            for price in item.find_all("span", {"class": "price"}):
                try:
                    # removes prix au gramme prices as they're scam and meals with prices=0 due to restaurateur not being honnetes and cheating the price filters
                    if "g" not in price and float(price.text[2:-4]) > 0:
                        if len(price) > 1 or "E" in price.text:
                            prices.append(float(price.text[2:-4]))
                        else:
                            prices.append(float(price.text[:-3]))
                except:
                    # do not add the restaurant's entry
                    pass
            if len(prices):
                resto = item.find("td", {"class": "restaurant"}).text.strip()[
                    :7  # very future proof solution
                ]
                resto = alias.get(resto, resto)
                if resto not in excluded:
                    descr = item.find("div", {"class": "descr"})
                    dish_name = descr.find("b").text.replace("\n", " ")
                    vegetarian = bool(descr.find(string="végétarien"))
                    dishes.append(Dish(prices, resto, dish_name, vegetarian))
        return Menu(dishes)


class MenuFilter:
    filters: List[Callable[[Dish], bool]]

    def __init__(self) -> None:
        self.filters = []

    def add_filter(self, filter0: Callable[[Dish], bool]) -> None:
        self.filters.append(filter0)

    def vegetarian(self) -> None:
        self.add_filter(lambda d: d.vegetarian)

    def budget(self, budget: float) -> None:
        self.add_filter(lambda d: min(d.prices) <= budget)

    def __call__(self, menu: Menu) -> Menu:
        logger.info(f"Filtering with {self.filters}")
        return Menu(
            dish
            for dish in menu.dishes
            if all(filter0(dish) for filter0 in self.filters)
        )


def soup(update, context):
    """
    Uses bs4 and a curl script to scrape FLEP's daily menus and output all meals fitting the criterion.
    As of know, only supports price threshold (/soup 10 returns all meal under 10 chf)
    """
    logger.info(f"user #{update.effective_user.id} required soup ({context.args})")

    # timer entry relevant for caching logic
    now = datetime.datetime.now()

    # limit the number of soup request per chat id to one per hour
    # this is the cache entry to store the chat ids and their request times
    group_cache = "soup_group"
    
    # create the request timer cache entry
    if group_cache not in REQUEST_TIMER:
       REQUEST_TIMER[group_cache] = {}

    # the chat id of the current request, this is the id of a timer cache entry
    group_request = str(update.message.chat_id)

    # the chat id already exists in the timer cache and the current request is too recent
    if (
        group_request in REQUEST_TIMER[group_cache] and
        (now - REQUEST_TIMER[group_cache][group_request]).total_seconds() < 3600
    ):
        logger.info("dropped soup request")
        return

    # limit the fetch of the menu's data to one per hour
    # a request still has to trigger the fetch!
    fetch_cache = "soup_cache"

    # fetch if nothing is currently cached or if the cache expired
    if (
        fetch_cache not in REQUEST_TIMER or
        (now - REQUEST_TIMER[fetch_cache]).total_seconds() >= 3600
    ):

        # fetch the raw html
        try:
            menu_buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(pycurl.URL, SOUP_ENDPOINT)
            c.setopt(pycurl.WRITEDATA, menu_buffer)
            c.setopt(pycurl.CAINFO, certifi.where())
            c.perform()
            c.close()
            markup = menu_buffer.getValue().decode(('iso-8859-1'))
        
        except:
            logger.error("error when fetching raw menu")

            # wait 10 minutes before trying to fetch again
            REQUEST_TIMER[fetch_cache] = now - datetime.timedelta(hours=1) + datetime.timedelta(minutes=10)

            update.message.reply_text(
                "Petit problème du côté d'EPFL campus ! La commande sera de nouveau disponible dans quelques minutes.",
                quote=False
            )
            return

        # update the most recent fetch's timestamp
        REQUEST_TIMER[fetch_cache] = now

        # parse the raw html
        try:
            parsed_menu = Menu.from_html(markup)
        except:
            # wait 10 minutes before trying to fetch and parse again
            REQUEST_TIMER[fetch_cache] = now - datetime.timedelta(hours=1) + datetime.timedelta(minutes=10)
            return

        # the parsed html is cached in the bot's memory
        context.bot_data[fetch_cache] = parsed_menu

    # following the code above, the cache entry must exist
    menu: Menu = context.bot_data[fetch_cache]

    # regular arg parsing
    inputs: List[Any] = context.args
    budget = None
    vegetarian = None
    if len(inputs):
        for arg in inputs[:2]:
            if budget is None:
                try:
                    budget = max(5.0, min(40.0, round(float(arg), 1)))
                    continue
                except:
                    pass
            if vegetarian is None and arg.lower().replace("é", "e") in VEGETARIAN_WORDS:
                vegetarian = True
    if budget is None:
        budget = False
    if vegetarian is None:
        vegetarian = False

    if budget or vegetarian:
        menu_filter = MenuFilter()
        if budget:
            menu_filter.budget(budget)
        if vegetarian:
            menu_filter.vegetarian()
        if len(menu_filter.filters):
            menu = menu_filter(menu)

    # send the menu! :)
    update.message.reply_text(
        str(menu),
        quote=False,
        parse_mode=telegram.constants.PARSEMODE_HTML,
    )

    # the group/user has to wait 1h before any further soup request
    REQUEST_TIMER[group_cache][group_request] = now
