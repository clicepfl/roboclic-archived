from .. import open_utf8_r

import json
import logging
from datetime import datetime


LIMIT = 10
POLL = 0

JUL = "robot/config/jul.txt"
RAYAN = "robot/config/rayan.txt"
ARTHUR = "robot/config/arthur.txt"
HELPER_TEXTS = "robot/config/helper_texts.txt"
STATS = "robot/config/stats.json"
SOUP = "robot/config/soup.sh"

NORMAL_COMMANDS = {
    "jul",
    "hugo",
    "reuf",
    "noel",
    "arthur",
    "rayan",
    "birthday",
    "bureau",
    "year",
    "stats",
    "cafe",
}
SPECIAL_COMMANDS = {"poll", "help"}

EXPLANATIONS = {}
for line in open_utf8_r(HELPER_TEXTS):
    (fname, help_text) = line.split(" ", 1)
    EXPLANATIONS[fname] = help_text

KEYS = json.load(open(".keys"))
OPTIONS = json.load(open("robot/config/options.json"))
BIRTHDAYS = json.load(open("robot/config/birthday.json"))

REQUEST_TIMER = {"launched": datetime.now()}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
