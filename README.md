# Trading Bot

Bot de trading automatizado para crypto usando Python y ccxt.

## Stack
- Python 3.11
- ccxt (conexión a exchanges)
- pandas / numpy (análisis de datos)
- python-dotenv (manejo de variables de entorno)
- matplotlib (gráficas)
- python-telegram-bot (notificaciones)

## Exchange
Binance Testnet (simulación)

## Características
- Estrategia SMA Crossover (SMA20 / SMA50)
- Soporte para múltiples pares (BTC, ETH, BNB, SOL, XRP)
- Stop Loss y Take Profit configurables
- Interfaz gráfica con gráfica de precio en tiempo real
- Logs guardados en archivo por día
- Notificaciones por Telegram en cada operación

## Estructura
```
trading_bot/
│
├── bot/
│   ├── __init__.py
│   ├── exchange.py      # Conexión a Binance
│   ├── data.py          # Obtener datos del mercado
│   ├── strategy.py      # Lógica SMA, señales
│   ├── risk.py          # Stop Loss / Take Profit y órdenes
│   └── logger.py        # Logs en archivo
│   └── notificaciones.py # Notificaciones Telegram
│
├── ui/
│   ├── __init__.py
│   └── app.py           # Interfaz gráfica
│
├── backtest.py          # Backtesting de estrategia
├── main.py              # Punto de entrada
├── .env                 # API keys (no se sube a GitHub)
├── .gitignore
└── README.md
```

## Setup
1. Clonar el repositorio
2. Crear entorno conda: `conda create -n trading_bot python=3.11`
3. Activar entorno: `conda activate trading_bot`
4. Instalar dependencias: `pip install ccxt pandas numpy python-dotenv matplotlib python-telegram-bot requests`
5. Crear archivo `.env` con tus credenciales:
```
API_KEY=tu_api_key
SECRET_KEY=tu_secret_key
TELEGRAM_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_chat_id
```
6. Ejecutar: `python main.py`

## Progreso
- [x] Paso 1 - Configuración del entorno y conexión al testnet
- [x] Paso 2 - Obtener datos del mercado
- [x] Paso 3 - Estrategia SMA crossover
- [x] Paso 4 - Backtesting
- [x] Paso 5 - Bot en vivo (simulación)
- [x] Mejora 1 - Stop Loss / Take Profit
- [x] Mejora 2 - Soporte para múltiples criptos
- [x] Mejora 3 - Logs guardados en archivo
- [x] Mejora 4 - Notificaciones por Telegram