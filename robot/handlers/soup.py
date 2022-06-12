import os
from copy import deepcopy
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
        return f"🍽️<b> {min(self.prices)} CHF</b> - <i>{self.name_resto}</i> → {self.dish_name}."


class Menu:
    dishes: Iterable[Dish]
    filters: List[Callable[[Dish], bool]]

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

    def add_filter(self, filter0: Callable[[Dish], bool]):
        self.filters.append(filter0)

    def vegetarian(self):
        self.add_filter(lambda d: d.vegetarian)

    def budget(self, budget):
        self.add_filter(lambda d: min(d.prices) <= budget)

    def filter(self):
        return Menu(
            dish
            for dish in self.dishes
            if all(filter0(dish) for filter0 in self.filters)
        )

    @staticmethod
    def from_html(html):
        # removes non-Lausanne results
        excluded = set(["La Ruch", "Microci", "Hodler"])
        # handle edge case names
        alias = {"La Tabl": "Vallotton", "Maharaj": "Maharaja"}

        soup = bs(html, "html.parser")
        content = soup.find_all("tr", {"class": "menuPage"})
        dishes = []
        for item in content:
            prices = []
            for price in item.findAll("span", {"class": "price"}):
                # removes prix au gramme prices as they're scam and meals with prices=0 due to restaurateur not being honnetes and cheating the price filters
                if "g" not in price and float(price.text[2:-4]) > 0:
                    if len(price) > 1 or "E" in price.text:
                        prices.append(float(price.text[2:-4]))
                    else:
                        prices.append(float(price.text[:-3]))
            if len(prices):
                resto = item.findAll("td", {"class": "restaurant"})[0].text.strip()[
                    :7  # very future proof solution
                ]
                resto = alias.get(resto, resto)
                if resto not in excluded:
                    descr = item.findAll("div", {"class": "descr"})[0]
                    dish_name = descr.findAll("b")[0].text.replace("\n", " ")
                    vegetarian = "végétarien" in descr
                    dishes.append(Dish(prices, resto, dish_name, vegetarian))
        return Menu(dishes)


def soup(update, context):
    """
    Uses bs4 and a curl script to scrape FLEP's daily menus and output all meals fitting the criterion.
    As of know, only supports price threshold (/soup 10 returns all meal under 10 chf)
    """
    now = datetime.now()
    if (
        "soup" not in REQUEST_TIMER
        or (now - REQUEST_TIMER["soup"]).total_seconds() >= 3600
    ):
        # Fetches the daily menu
        os.system(f"sh {SOUP} {datetime.today().strftime('%Y-%m-%d')}")
        REQUEST_TIMER["soup"] = now
        with open(MENU, "r") as markup:
            menu = Menu.from_html(markup)
            context.bot_data["soup_cache"] = {"menu": menu, "budgets": {}}

    soup_cache = context.bot_data["soup_cache"]
    menu: Menu = deepcopy(soup_cache["menu"])
    inputs: List[Any] = context.args

    # arg parsing
    budget = None
    vegetarian = None
    if len(inputs):
        for arg in inputs:
            if budget is None:
                try:
                    budget = float(arg)
                    continue
                except:
                    pass
            if vegetarian is None and arg.lower().replace("é", "e") in VEGETARIAN_WORDS:
                vegetarian = True
    if budget is None:
        budget = 10.0
    if vegetarian is None:
        vegetarian = False

    budget_key = "vegetarian" if vegetarian else "omnivore"

    if budget not in soup_cache["budgets"]:
        menu.budget(budget)
        if vegetarian:
            menu.vegetarian()
        menu = menu.filter()
        soup_cache["budgets"][budget] = {budget_key: str(menu)}
    elif vegetarian and "vegetarian" not in soup_cache["budgets"][budget]:
        menu.vegetarian()
        menu = menu.filter()
        soup_cache["budgets"][budget].update({"vegetarian": str(menu)})

    logger.info(
        f"user #{update.effective_user.id} required soup ({budget}, {budget_key})"
    )

    update.message.reply_text(
        soup_cache["budgets"][budget][budget_key],
        quote=False,
        parse_mode=telegram.constants.PARSEMODE_HTML,
    )
