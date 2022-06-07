# RoboCLIC ?
_Le bot Telegram de la [CLIC](https://clic.epfl.ch)_

### Requirements

Install dependencies [Telegram API wrapper](https://github.com/python-telegram-bot/python-telegram-bot) and BeautifulSoup 4

```
pip install -r requirements.txt
```

See the [Telegram Bot API documentation](https://core.telegram.org/bots) to obtain your bot token, to be stored in a ```.keys``` JSON file under ```{ "token": "YOUR_TOKEN" }```. Then simply launch the bot
```
python roboclic.py
```

Please disable the bot's privacy mode before using it.

Note that a few optional features expect additional parameters from the `.keys` file, namely `groups` (list of chat IDs), `phone` (string) and `admin` (chat ID).

### Features

The bot offers various features, among which countdown commands for key events, a game consisting in guessing the author of rap punchlines from the French classic _Bande Organisée_, a poll game consisting in guessing which CLIC member said a given sentence, and many more! Configuration files are available to change the poll options (i.e., the CLIC members) and other relevant parameters. Please consider keeping `options.json` and `birthdays.json` consistent.

Enjoy!
