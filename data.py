import ccxt
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

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

# Obtener velas de BTC/USDT cada 1 hora, las últimas 100
velas = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)

# Convertir a DataFrame
df = pd.DataFrame(velas, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Convertir timestamp a fecha legible
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

print(df.tail(10))