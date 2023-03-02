import os
import textwrap

import dotenv
import logging
import redis as r

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from functools import partial
from elasticpath_utls import get_products, get_access_token, get_product, get_file, get_stock, add_products_to_cart
from pprint import pprint


def start(bot, update, client_id, client_secret):

    access_token = get_access_token(client_id, client_secret)
    products = get_products(access_token)

    message = textwrap.dedent(
        """
        Внимание, внимание!
        Открывается веселое гуляние!
        Торопись, честной народ,
        Тебя ярмарка зовет!
        """
    )

    keyboard = []
    for product in products['data']:
        keyboard.append([InlineKeyboardButton(product['attributes']['name'], callback_data=product['id'])])
    keyboard.append([InlineKeyboardButton('Корзина', callback_data='basket')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text=message, reply_markup=reply_markup)
    return "HANDLE_MENU"


def product_detail(bot, update, client_id, client_secret):

    query = update.callback_query
    data = query.data.split(':::')

    product_id = data[0]
    access_token = get_access_token(client_id, client_secret)

    product = get_product(access_token, product_id)

    image_id = product['data']['relationships']['main_image']['data']['id']
    image_url = get_file(access_token, image_id)['data']['link']['href']

    description = product['data']['attributes']['description']
    description = description.replace('\n', '')

    name = product['data']['attributes']['name']
    price = product['data']['meta']['display_price']['with_tax']['formatted']
    stock = get_stock(access_token, product_id)['data']['available']

    message = textwrap.dedent(
        fr"""
        {name}
        
        Price: {price}
        Stock: {stock} kg
        
        {description}
        """
    )

    keyboard = [
        [
            InlineKeyboardButton('1 kg', callback_data=f'{product_id}:::1'),
            InlineKeyboardButton('5 kg', callback_data=f'{product_id}:::5'),
            InlineKeyboardButton('10 kg', callback_data=f'{product_id}:::10')
         ],
        [InlineKeyboardButton('Назад', callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_photo(caption=message, photo=image_url, chat_id=query.message.chat_id, reply_markup=reply_markup)
    bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return "HANDLE_DESCRIPTION"


def go_back(bot, update, client_id, client_secret):

    query = update.callback_query

    access_token = get_access_token(client_id, client_secret)

    if query.data != 'back':
        data = query.data.split(':::')
        product_id = data[0]
        quantity = int(data[1])
        response = add_products_to_cart(access_token, query.message.chat_id, product_id, quantity)
        pprint(response)
        return "HANDLE_MENU"

    products = get_products(access_token)

    keyboard = []
    for product in products['data']:
        keyboard.append([InlineKeyboardButton(product['attributes']['name'], callback_data=product['id'])])

    message = textwrap.dedent(
        """
        Внимание, внимание!
        Открывается веселое гуляние!
        Торопись, честной народ,
        Тебя ярмарка зовет!
        """
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(text=message, chat_id=query.message.chat_id, reply_markup=reply_markup)
    bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return "HANDLE_MENU"


def handle_users_reply(bot, update, client_id, client_secret):

    start_credentials = partial(start, client_id=client_id, client_secret=client_secret)
    product_detail_credentials = partial(product_detail, client_id=client_id, client_secret=client_secret)
    go_back_credentials = partial(go_back, client_id=client_id, client_secret=client_secret)

    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = redis.get(chat_id).decode("utf-8")
    states_functions = {
        'START': start_credentials,
        'HANDLE_MENU': product_detail_credentials,
        'HANDLE_DESCRIPTION': go_back_credentials
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update)
        redis.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection(host, port, password):
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global redis
    database_host = host
    database_port = port
    database_password = password
    redis = r.Redis(host=database_host, port=database_port, password=database_password)


def main() -> None:
    dotenv.load_dotenv()

    token = os.environ['TELEGRAM_TOKEN']

    redis_host = os.environ['REDIS_HOST']
    redis_port = os.environ['REDIS_PORT']
    redis_password = os.environ['REDIS_PASSWORD']

    moltin_application_key = os.environ['MOLTIN_APPLICATION_KEY']
    moltin_client_id = os.environ['MOLTIN_CLIENT_ID']
    moltin_secret_key = os.environ['MOLTIN_SECRET_KEY']

    get_database_connection(redis_host, redis_port, redis_password)

    handle_users_reply_moltin = partial(handle_users_reply, client_id=moltin_client_id, client_secret=moltin_secret_key)

    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply_moltin))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply_moltin))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply_moltin))

    updater.start_polling()


if __name__ == '__main__':
    main()
