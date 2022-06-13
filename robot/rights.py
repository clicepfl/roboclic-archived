from functools import wraps

from telegram.ext import CommandHandler

from .config import KEYS, logger

LOGGING_GROUP_INFO = "user #{} tried to start [{}] from group #{}"
LOGGING_DM_INFO = "user #{} tried to start [{}]"


def clic(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if "groups" in KEYS and chat_id not in KEYS["groups"]:
            template = LOGGING_GROUP_INFO if chat_id == user_id else LOGGING_DM_INFO
            return logger.info(template.format(user_id, func, chat_id))
        return func(update, context, *args, **kwargs)

    return wrapped


def admin(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if "admin" in KEYS and user_id != KEYS["admin"]:
            template = LOGGING_GROUP_INFO if chat_id == user_id else LOGGING_DM_INFO
            return logger.info(template.format(user_id, func, chat_id))
        return func(update, context, *args, **kwargs)

    return wrapped
