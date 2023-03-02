# Fish Seller Bot

Bot for selling fish  ζº͜))))&gt;&gt;&lt;

![](https://github.com/EshiNanase/fish_seller_chatbot/blob/main/example.gif)

Example:
Telegram: https://t.me/ultimate_fish_seller_chatbot

## Prerequisites

Virtual environment needs to be:

```
python==3.9
```
## Installing

First, you need to clone the code:

```
git clone https://github.com/EshiNanase/fish_seller_chatbot.git
```
Second, you need to install requirements.txt:

```
pip install -r requirements.txt
```
Third, you need to create a shop on elasticpath.com:
```
https://euwest.cm.elasticpath.com/
```
Forth, in this shop you need to create:
```
Products on elasticpath.com/products page, then define price and set them live
Price Book on elasticpath.com/pricebooks page and add created products
Catalog on elasticpath.com/catalogs page, add created price book there and add created products to Products List
```
Fifth, you need to create redis database following these instructions:
```
https://app.redislabs.com/
```
## Environment variables

The code needs .env file with such environment variables as:

```
TELEGRAM_TOKEN = token of your Telegram bot, text https://t.me/BotFather to create one
TELEGRAM_CHAT_ID = needed for logger you can find it here https://t.me/userinfobot
REDIS_HOST = host of you redis db, you'll get it once you create redis db
REDIS_PORT = port of you redis db, you'll get it once you create redis db
REDIS_PASSWORD = password of you redis db, you need to create redis db and remember the password
MOLTIN_CLIENT_ID = your client id, you can find it on elasticpath.com/application-keys page
MOLTIN_SECRET_KEY = your client secret key, you can find it on elasticpath.com/application-keys#legacy-key page
```
## Running

The code should be ran in cmd like so:

```
python telegram_bot.py
```