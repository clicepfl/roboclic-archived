from functools import wraps

from telegram.ext import CommandHandler

from .config import KEYS, logger

LOGGING_INFO = "user #{} tried to start ({}) from chat #{}"


def clic(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if "groups" in KEYS and chat_id not in KEYS["groups"]:
            return logger.info(LOGGING_INFO.format(user_id, func, chat_id))
        return func(update, context, *args, **kwargs)

    return wrapped


def admin(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if "admin" in KEYS and user_id not in KEYS["admin"]:
            return logger.info(LOGGING_INFO.format(user_id, func, chat_id))
        return func(update, context, *args, **kwargs)

    return wrapped
