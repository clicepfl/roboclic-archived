# Qui a dit ça ?
_Qui a dit ça ? Le fameux jeu de la CLIC_

### Requirements

Install the right [Telegram API wrapper](https://github.com/python-telegram-bot/python-telegram-bot) for Python.
You will also need [Unidecode](https://pypi.org/project/Unidecode/). Namely:

```
$ pip install python-telegram-bot
$ pip install unidecode
```

Then simply launch the bot
```
$ python bot.py
```
You can edit the list of people _qui l'ont peut-être dit_ via a direct edit of the JSON file ```options.json```. The key should be a unicode version of a potentially fancier value. Typically, you want to add an entry of the form ```"francois": "François"```.

Enjoy!

### Upcoming changes

The above mentioned JSON file along with a Telegram selection menu of the answer/member.
