import requests

TIMESTAMP = None


def get_access_token(client_id, client_secret):

    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=payload)
    response.raise_for_status()
    token = response.json()['access_token']
    timestamp = response.json()['expires']
    return token, timestamp


def get_access_token_implicit(client_id):

    payload = {
        'client_id': client_id,
        'grant_type': 'implicit'
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=payload)
    response.raise_for_status()
    token = response.json()['access_token']
    return token


def get_cart(token, chat_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/{chat_id}', headers=headers)
    response.raise_for_status()
    return response.json()


def get_cart_items(token, chat_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/{chat_id}/items', headers=headers)
    response.raise_for_status()
    return response.json()


def delete_cart_item(token, chat_id, product_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.delete(f'https://api.moltin.com/v2/carts/{chat_id}/items/{product_id}', headers=headers)
    response.raise_for_status()
    return response.json()


def create_customer(token, chat_id, email):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    payload = {
        'data': {
            'type': 'customer',
            'name': str(chat_id),
            'email': email
        }
    }
    response = requests.post(f'https://api.moltin.com/v2/customers', headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def get_price_book(token, price_book_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/pcm/pricebooks/{price_book_id}', headers=headers)
    response.raise_for_status()
    return response.json()


def create_cart(token, chat_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'x-moltin-customer-token': chat_id
    }
    payload = {
        'data': {
            'name': chat_id,
            'description': f'{chat_id}\'s cart'
        }
    }
    response = requests.post(f'https://api.moltin.com/v2/carts', headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def add_products_to_cart(token, chat_id, product_id, quantity):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'data': {
            "id": product_id,
            "type": "cart_item",
            "quantity": quantity,
        }
    }
    response = requests.post(f'https://api.moltin.com/v2/carts/{chat_id}/items', headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def get_products(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get('https://api.moltin.com/pcm/products', headers=headers)
    response.raise_for_status()
    return response.json()


def get_product(token, product_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/catalog/products/{product_id}', headers=headers)
    response.raise_for_status()
    return response.json()


def get_stock(token, product_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/inventories/{product_id}', headers=headers)
    response.raise_for_status()
    return response.json()


def get_file(token, file_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/files/{file_id}', headers=headers)
    response.raise_for_status()
    return response.json()
