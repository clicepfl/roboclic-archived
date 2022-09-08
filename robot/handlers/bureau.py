from telegram import Poll

from ..rights import clic


@clic
def bureau(update, context):
    question = "Qui est au bureau ?"
    choices = [
        "Je suis actuellement au bureau",
        "Je suis à proximité du bureau",
        "Je compte m'y rendre bientôt",
        "J'y suis pas",
        "Je suis pas en Suisse",
        "Je suis à Satellite",
    ]
    context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question,
        options=choices,
        type=Poll.REGULAR,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
