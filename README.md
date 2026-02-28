# Trading Bot

Bot de trading automatizado para crypto usando Python y ccxt.

## Stack
- Python 3.11
- ccxt (conexión a exchanges)
- pandas / numpy (análisis de datos)
- python-dotenv (manejo de variables de entorno)

## Exchange
Binance Testnet (simulación)

## Progreso
- [x] Paso 1 - Configuración del entorno y conexión al testnet
- [ ] Paso 2 - Obtener datos del mercado
- [ ] Paso 3 - Estrategia SMA crossover
- [ ] Paso 4 - Backtesting
- [ ] Paso 5 - Bot en vivo (simulación)

## Setup
1. Clonar el repositorio
2. Crear entorno conda: `conda create -n trading_bot python=3.11`
3. Activar entorno: `conda activate trading_bot`
4. Instalar dependencias: `pip install ccxt pandas numpy python-dotenv`
5. Crear archivo `.env` con tus API keys de Binance Testnet