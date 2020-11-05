# RoboCLIC ?
_Le bot Telegram de la [CLIC](https://clic.epfl.ch)_

### Requirements

Install the right [Telegram API wrapper](https://github.com/python-telegram-bot/python-telegram-bot) for Python. Namely

```
pip install python-telegram-bot
```

See the Telegram API documentation to obtain your bot token, to be stored in a ```.keys``` file under ```token=YOUR_TOKEN```. Then simply launch the bot
```
python bot.py
```
The bot offers various features, among which countdown commands for key events, a game consisting in guessing the author of rap punchlines from the French classic _Bande Organisée_, and a poll game consisting in guessing which CLIC member said a given sentence. Configuration files are available to change the poll options (i.e., the CLIC members) and the _Bande Organisée_ lyrics. The countdown commands are hardcoded in the main Python file.

Enjoy!
