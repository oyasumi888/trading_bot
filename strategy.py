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

def obtener_datos(simbolo='BTC/USDT', timeframe='1h', limit=100):
    velas = exchange.fetch_ohlcv(simbolo, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(velas, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calcular_sma(df):
    df['sma20'] = df['close'].rolling(window=20).mean()
    df['sma50'] = df['close'].rolling(window=50).mean()
    return df

def generar_señal(df):
    ultima = df.iloc[-1]
    anterior = df.iloc[-2]

    if anterior['sma20'] <= anterior['sma50'] and ultima['sma20'] > ultima['sma50']:
        return 'COMPRAR'
    elif anterior['sma20'] >= anterior['sma50'] and ultima['sma20'] < ultima['sma50']:
        return 'VENDER'
    else:
        return 'ESPERAR'

# Ejecutar
df = obtener_datos()
df = calcular_sma(df)

señal = generar_señal(df)
print(f"Señal actual: {señal}")
print(df[['timestamp', 'close', 'sma20', 'sma50']].tail(10))