def coffee(update, context):
    text = ""
    if len(context.args) > 0:
        if "vide" in context.args or "plus" in context.args:
            context.bot_data["empty"] = True
            text = "Il faut remplir le stock de café !!!"
        elif "plein" in context.args or "rempli" in context.args:
            context.bot_data["empty"] = False
            text = "Le stock de café a été rempli !"
    elif context.bot_data.get("empty", False):
        text = "Il n'y a plus de café !!!"
    else:
        text = "Pas de panique, il y a encore du café"
    update.message.reply_text(text, quote=False)
