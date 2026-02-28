import ccxt
import pandas as pd
import os
import time
from datetime import datetime
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

def ejecutar_orden(señal, simbolo='BTC/USDT'):
    balance = exchange.fetch_balance()
    usdt = balance['total'].get('USDT', 0)
    btc = balance['total'].get('BTC', 0)
    precio_actual = exchange.fetch_ticker(simbolo)['last']

    if señal == 'COMPRAR' and usdt > 10:
        monto = usdt * 0.95  # Usa el 95% del balance disponible
        cantidad = monto / precio_actual
        orden = exchange.create_market_buy_order(simbolo, cantidad)
        print(f"✅ COMPRA ejecutada | {cantidad:.6f} BTC a ${precio_actual}")
        return orden

    elif señal == 'VENDER' and btc > 0.0001:
        orden = exchange.create_market_sell_order(simbolo, btc)
        print(f"✅ VENTA ejecutada | {btc:.6f} BTC a ${precio_actual}")
        return orden

    else:
        print(f"⏸ Sin orden ejecutada | Balance: ${usdt:.2f} USDT | {btc:.6f} BTC")

def run():
    print("🤖 Bot iniciado...")
    while True:
        try:
            ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{ahora}] Analizando mercado...")

            df = obtener_datos()
            df = calcular_sma(df)
            df = df.dropna()

            señal = generar_señal(df)
            print(f"Señal: {señal}")

            ejecutar_orden(señal)

        except Exception as e:
            print(f"❌ Error: {e}")

        # Esperar 1 hora antes de revisar de nuevo
        print("⏳ Esperando 1 hora...")
        time.sleep(60)

run()