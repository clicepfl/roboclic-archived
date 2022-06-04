from .. import open_utf8_r
from ..config import KEYS, RAYAN, ARTHUR

import random
from typing import Any


class SimpleText:
    def __init__(self, message: str) -> str:
        self.message = message
    
    def __call__(self, update: Any) -> None:
        update.message.reply_text(self.message, quote=False)


def _quote(file):
    """
    Selects random line from file
    """
    quotes = open_utf8_r(file).read().splitlines()
    return random.choice(quotes)


def _telephone_du(reuf="reuf"):
    return f"{KEYS.get('phone', '3630')} le téléphone du {reuf} !"


noel = SimpleText(_telephone_du("Père Noël"))
reuf = SimpleText(_telephone_du)
rayan = SimpleText(_quote(RAYAN).capitalize())
arthur = SimpleText(_quote(ARTHUR))
hugo = SimpleText("???")
