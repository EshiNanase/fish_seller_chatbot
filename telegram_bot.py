import os
import textwrap
import time

import dotenv
import logging
import redis as r

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from functools import partial
from elasticpath import get_access_token, get_product, get_file, get_stock, add_products_to_cart, get_cart_items, delete_cart_item, create_customer
from telegram_send import send_basket, send_menu
from logger import ChatbotLogsHandler

logger = logging.getLogger(__file__)


def start(bot, update, access_token):
    message, reply_markup = send_menu(access_token)
    update.message.reply_text(text=message, reply_markup=reply_markup)

    return "HANDLE_MENU"


def get_product_detail(bot, update, access_token):

    query = update.callback_query
    data = query.data.split(':::')

    if 'basket' in data:
        cart_items = get_cart_items(access_token, query.message.chat_id)
        message, reply_markup = send_basket(cart_items)

        bot.edit_message_text(text=message,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup
                              )
        return "HANDLE_BASKET"

    product_id = data[0]

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


def get_basket(bot, update, access_token):

    query = update.callback_query
    data = query.data

    if data == 'back_to_menu':
        message, reply_markup = send_menu(access_token)
        bot.edit_message_text(text=message,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup
                              )
        return "HANDLE_MENU"

    if data == 'payment':
        message = 'Отправляй почту, дружище (o･ω･o)'
        bot.edit_message_text(text=message,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id
                              )

        return "WAITING_EMAIL"

    delete_cart_item(access_token, query.message.chat_id, data)

    cart_items = get_cart_items(access_token, query.message.chat_id)
    message, reply_markup = send_basket(cart_items)

    bot.edit_message_text(text=message,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=reply_markup
                          )
    return "HANDLE_BASKET"


def wait_for_email(bot, update, access_token):

    email = update.message.text
    chat_id = update.message.chat_id
    create_customer(access_token, chat_id, email)
    update.message.reply_text(text=f'Вы отправили мне эту почту {email}')

    message, reply_markup = send_menu(access_token)
    update.message.reply_text(text=message, reply_markup=reply_markup)

    return "HANDLE_MENU"


def go_back(bot, update, access_token):

    query = update.callback_query

    if query.data != 'back':
        data = query.data.split(':::')
        product_id = data[0]
        quantity = int(data[1])
        add_products_to_cart(access_token, query.message.chat_id, product_id, quantity)
        return "HANDLE_MENU"

    message, reply_markup = send_menu(access_token)

    bot.send_message(text=message, chat_id=query.message.chat_id, reply_markup=reply_markup)
    bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return "HANDLE_MENU"


def handle_users_reply(bot, update, access_token, timestamp, client_id, client_secret, redis):

    if timestamp + 3600 < time.time():
        access_token, timestamp = get_access_token(client_id, client_secret)

    start_credentials = partial(start, access_token=access_token)
    get_product_detail_credentials = partial(get_product_detail, access_token=access_token)
    go_back_credentials = partial(go_back, access_token=access_token)
    get_basket_credentials = partial(get_basket, access_token=access_token)
    wait_for_email_credentials = partial(wait_for_email, access_token=access_token)

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
        'HANDLE_MENU': get_product_detail_credentials,
        'HANDLE_DESCRIPTION': go_back_credentials,
        'HANDLE_BASKET': get_basket_credentials,
        'WAITING_EMAIL': wait_for_email_credentials
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update)
        redis.set(chat_id, next_state)
    except Exception as err:
        print(err)


def main() -> None:
    dotenv.load_dotenv()

    telegram_token = os.environ['TELEGRAM_TOKEN']
    telegram_chat_id = os.environ['TELEGRAM_CHAT_ID']

    logging.basicConfig(level=logging.WARNING)
    logger.addHandler(ChatbotLogsHandler(telegram_chat_id, telegram_token))

    redis_host = os.environ['REDIS_HOST']
    redis_port = os.environ['REDIS_PORT']
    redis_password = os.environ['REDIS_PASSWORD']
    redis = r.Redis(host=redis_host, port=redis_port, password=redis_password)

    moltin_client_id = os.environ['MOLTIN_CLIENT_ID']
    moltin_secret_key = os.environ['MOLTIN_SECRET_KEY']
    moltin_access_token, timestamp = get_access_token(moltin_client_id, moltin_secret_key)

    handle_users_reply_moltin = partial(
        handle_users_reply,
        client_id=moltin_client_id,
        access_token=moltin_access_token,
        timestamp=timestamp,
        client_secret=moltin_secret_key,
        redis=redis
    )

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply_moltin))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply_moltin))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply_moltin))

    updater.start_polling()


if __name__ == '__main__':
    main()
