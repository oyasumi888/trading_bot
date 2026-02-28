import pandas as pd
from bot.exchange import exchange

def obtener_datos(simbolo='BTC/USDT', timeframe='1h', limit=100):
    velas = exchange.fetch_ohlcv(simbolo, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(velas, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def obtener_precio(simbolo='BTC/USDT'):
    return exchange.fetch_ticker(simbolo)['last']

def obtener_balance():
    balance = exchange.fetch_balance()
    return {
        'USDT': balance['total'].get('USDT', 0),
        'BTC': balance['total'].get('BTC', 0)
    }