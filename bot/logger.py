import logging
import os
from datetime import datetime

def crear_logger():
    # Crear carpeta logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Nombre del archivo con fecha
    fecha = datetime.now().strftime('%Y-%m-%d')
    archivo = f"logs/bot_{fecha}.log"

    logger = logging.getLogger('trading_bot')
    logger.setLevel(logging.INFO)

    # Evitar duplicar handlers si se llama varias veces
    if not logger.handlers:
        handler = logging.FileHandler(archivo, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

logger = crear_logger()