from datetime import datetime

import pytz


def get_time(timedelta):
    """
    Number of seconds in a time interval
    """
    return timedelta.days * 24 * 60 * 60 + timedelta.seconds


def progression_bar(percent):
    """
    ASCII progress bar given a percentage
    """
    total = 25
    tiles = min(total, int(round(percent / 4)))
    return "[" + "#" * tiles + "-" * (total - tiles) * 2 + "]"


def year(update, contact):
    timezone = pytz.timezone("Europe/Zurich")
    today = datetime.now(timezone)
    start = datetime(today.year, 1, 1, 0, 0).astimezone(timezone)
    end = datetime(today.year, 12, 31, 23, 59).astimezone(timezone)

    passed = today - start
    total = end - start

    percent = max(0, get_time(passed) / get_time(total) * 100)
    display = progression_bar(percent)

    update.message.reply_text("{:.2f}%\n{}".format(percent, display), quote=False)
