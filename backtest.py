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

def obtener_datos(simbolo='BTC/USDT', timeframe='1h', limit=500):
    velas = exchange.fetch_ohlcv(simbolo, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(velas, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calcular_sma(df):
    df['sma20'] = df['close'].rolling(window=20).mean()
    df['sma50'] = df['close'].rolling(window=50).mean()
    return df

def backtest(df, capital_inicial=1000):
    capital = capital_inicial
    btc = 0
    operaciones = []

    for i in range(1, len(df)):
        anterior = df.iloc[i - 1]
        actual = df.iloc[i]

        # Señal de compra
        if anterior['sma20'] <= anterior['sma50'] and actual['sma20'] > actual['sma50']:
            if capital > 0:
                btc = capital / actual['close']
                capital = 0
                operaciones.append({
                    'tipo': 'COMPRA',
                    'precio': actual['close'],
                    'timestamp': actual['timestamp']
                })

        # Señal de venta
        elif anterior['sma20'] >= anterior['sma50'] and actual['sma20'] < actual['sma50']:
            if btc > 0:
                capital = btc * actual['close']
                btc = 0
                operaciones.append({
                    'tipo': 'VENTA',
                    'precio': actual['close'],
                    'timestamp': actual['timestamp']
                })

    # Si quedamos con BTC al final, lo convertimos a dólares
    if btc > 0:
        capital = btc * df.iloc[-1]['close']

    return capital, operaciones

# Ejecutar
df = obtener_datos()
df = calcular_sma(df)
df = df.dropna()  # Eliminar filas sin SMA calculada

capital_final, operaciones = backtest(df)

print(f"Capital inicial: $1000")
print(f"Capital final:   ${capital_final:.2f}")
print(f"Ganancia/Pérdida: ${capital_final - 1000:.2f}")
print(f"Total operaciones: {len(operaciones)}")
print()
for op in operaciones:
    print(f"{op['tipo']} | {op['timestamp']} | ${op['precio']:.2f}")