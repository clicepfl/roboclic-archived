from ..config import EXPLANATIONS, NORMAL_COMMANDS, SPECIAL_COMMANDS


def _display(commands):
    return "\n".join(("/" + command) for command in commands)


def help(update, context):
    if len(context.args) > 0:
        update.message.reply_text(EXPLANATIONS.get(context.args[0], "Not a command"))
    else:
        commands = _display(NORMAL_COMMANDS.union(SPECIAL_COMMANDS))
        update.message.reply_text(
            "Available commands:\n{}\nUse help 'command_name' for more info".format(
                commands
            )
        )
