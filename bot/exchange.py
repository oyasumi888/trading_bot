import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

def crear_exchange():
    exchange = ccxt.binance({
        'apiKey': os.getenv('API_KEY'),
        'secret': os.getenv('SECRET_KEY'),
        'options': {
            'defaultType': 'spot',
            'adjustForTimeDifference': True,
        },
        'hostname': 'testnet.binance.vision',
        'urls': {
            'api': {
                'rest': 'https://testnet.binance.vision'
            }
        }
    })
    exchange.set_sandbox_mode(True)
    return exchange

exchange = crear_exchange()