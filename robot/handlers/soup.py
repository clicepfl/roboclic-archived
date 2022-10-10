import os
from dataclasses import dataclass
from datetime import datetime
from random import sample
from typing import Any, Callable, Iterable, List

import telegram
from bs4 import BeautifulSoup as bs

from ..config import MENU, REQUEST_TIMER, SOUP, logger


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
    now = datetime.now()
    
    if "soup_group" not in REQUEST_TIMER:
       REQUEST_TIMER["soup_group"] = {}
    if str(update.message.chat_id) in REQUEST_TIMER["soup_group"] and (now-REQUEST_TIMER["soup_group"][str(update.message.chat_id)][0]).total_seconds() < 3600:
        context.bot.send_message(
                chat_id = update.message.chat_id,
                text = "🙄",
                reply_to_message_id = REQUEST_TIMER["soup_group"][update.message.chat_id][1],
                disable_notification = True)
        return
    if (
        "soup" not in REQUEST_TIMER
        or (now - REQUEST_TIMER["soup"]).total_seconds() >= 3600
    ):
        # Fetches the daily menu
        os.system(f"sh {SOUP} {datetime.today().strftime('%Y-%m-%d')}")
        REQUEST_TIMER["soup"] = now
        with open(MENU, "r") as markup:
            context.bot_data["soup_cache"] = Menu.from_html(markup)

    menu: Menu = context.bot_data["soup_cache"]
    inputs: List[Any] = context.args

    # arg parsing
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

    soup_id = update.message.reply_text(
        str(menu),
        quote=False,
        parse_mode=telegram.constants.PARSEMODE_HTML,
    ).message_id
    REQUEST_TIMER["soup_group"][str(update.message.chat_id)] = (now, soup_id)
