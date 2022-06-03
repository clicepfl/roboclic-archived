from datetime import datetime


def countdown(*time):
    """
    Returns time left until given time, as (days, hours, minutes)
    """
    r = datetime(*time) - datetime.now()
    return r.days, r.seconds // 3600, r.seconds % 3600 // 60