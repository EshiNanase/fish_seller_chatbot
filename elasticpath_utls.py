import dotenv
import os
import requests


def get_access_token(client_id, client_secret):

    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=payload)
    token = response.json()['access_token']
    return token


def get_cart(token, cart_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/:{cart_id}', headers=headers)
    return response.json()


def create_cart(token, chat_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'data': {
            'name': chat_id,
            'description': f'{chat_id}\'s cart'
        }
    }
    response = requests.post(f'https://api.moltin.com/v2/carts', headers=headers, json=payload)
    return response.json()


def get_products(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get('https://api.moltin.com/pcm/products', headers=headers)
    return response.json()


def get_product(token, product_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/pcm/products/{product_id}', headers=headers)
    return response.json()


def get_file(token, file_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/files/{file_id}', headers=headers)
    return response.json()


def main() -> None:
    dotenv.load_dotenv()

    moltin_application_key = os.environ['MOLTIN_APPLICATION_KEY']
    moltin_client_id = os.environ['MOLTIN_CLIENT_ID']
    moltin_secret_key = os.environ['MOLTIN_SECRET_KEY']
    moltin_access_token = get_access_token(moltin_client_id, moltin_secret_key)


if __name__ == '__main__':
    main()
