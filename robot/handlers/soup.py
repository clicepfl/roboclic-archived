import os
from dataclasses import dataclass
from datetime import datetime
from random import sample
from typing import List

import telegram
from bs4 import BeautifulSoup as bs

from ..config import MENU, REQUEST_TIMER, SOUP

EMOJIS_FOOD = ["🥕","🥔","🍞","🍔","🍟","🍕","🥘",
			"🍳","🥚","🫔","🌯","🌮","🥪","🌭","🍲","🍖","🍗","🥩"]

@dataclass
class Dish:
    price_list : List[float]
    name_resto : str
    dish_name : str
    
    def __str__(self):
        return f"🍽️<b> {min(self.price_list)} CHF</b> - <i>{self.name_resto}</i> → {self.dish_name}."
    
    
def compute_text(list_dishes : List[Dish]) -> str:
    """Given a list of Dish, computes the final text representation.

    Parameters
    ----------
    list_plat : List[Dish]
        The list of dishes.

    Returns
    -------
    str
        The final text representation of the command.
    """
    TEMPLATE_TEXT = """
     {header}
         
{text_dishes}"""
    header = "{}{}<b>On mange quoi ?</b> {}{}".format(*sample(EMOJIS_FOOD, 4))
    return TEMPLATE_TEXT.format(header=header, text_dishes="\n".join(str(p) for p in list_dishes))

def soup(update, context):
    """
    Uses bs4 and a curl script to scrape FLEP's daily menus and output all meals fitting the criterion.
    As of know, only supports price threshold (/soup 10 returns all meal under 10 chf)
    """
    text = ""
    now = datetime.now()
    if (
        "soup" not in REQUEST_TIMER
        or (now - REQUEST_TIMER["soup"]).total_seconds() >= 3600
    ):
        # Fetches the daily menu
        os.system(f"sh {SOUP} {datetime.today().strftime('%Y-%m-%d')}")
        REQUEST_TIMER["soup"] = now
        with open(MENU, "r") as markup:
            soup = bs(markup, "html.parser")
            menu = soup.find_all("tr", {"class": "menuPage"})
            context.bot_data["soup_cache"] = {"menu": menu}

    menu = context.bot_data["soup_cache"]["menu"]
    # Removes non-Lausanne resultsMARKDOWN_V2
    excluded = set(["La Ruch", "Microci", "Hodler"])

    inputs = context.args
    results : List[Dish]= []

    if len(inputs) > 1:
        price_thrsh = float(inputs[0])
    else:
        price_thrsh = 10  # Default budget is 10 CHF

    if price_thrsh in context.bot_data["soup_cache"]:
        text = context.bot_data["soup_cache"][price_thrsh]
    else:
        for item in menu:
            price_list = [
                float(price.text[2:-4])
                # Gne gneu Marahja doesn't know how to fill their menus in
                if len(item.findAll("span", {"class": "price"})) > 1
                or "E" in price.text
                else float(price.text[:-3])  # All prices are xx CHF, we only want xx
                for price in item.findAll("span", {"class": "price"})
                if "g" not in price.text and float(price.text[2:-4]) > 0
            ]  # removes prix au gramme prices as they're scam and meals with prices=0 due to restaurateur not being honnetes and cheating the price filters
            if len(price_list):
                if min(price_list) <= price_thrsh:  # Assuming the user is a student
                    resto = item.findAll("td", {"class": "restaurant"})[0].text.strip()[
                        :7
                    ]
                    if resto not in excluded:
                        dish_name = item.findAll("div", {"class": "descr"})[0].findAll("b")[0].text.replace("\n", " ")
                        results.append(Dish(price_list, resto, dish_name))
                
        if not len(results):
            text = "Pas de résultat correspondant aux filtres, c'est régime"
        else:
            text = compute_text(results)
        context.bot_data["soup_cache"][price_thrsh] = text

    update.message.reply_text(text, quote=False, parse_mode = telegram.constants.PARSEMODE_HTML)
