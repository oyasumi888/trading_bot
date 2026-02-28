from bot.exchange import exchange

def verificar_sl_tp(precio_actual, precio_compra, stop_loss_pct, take_profit_pct):
    if precio_compra is None:
        return None
    if precio_actual <= precio_compra * (1 - stop_loss_pct / 100):
        return 'STOP_LOSS'
    if precio_actual >= precio_compra * (1 + take_profit_pct / 100):
        return 'TAKE_PROFIT'
    return None

def ejecutar_orden(señal, simbolo='BTC/USDT'):
    from bot.data import obtener_balance, obtener_precio
    balance = obtener_balance()
    precio = obtener_precio(simbolo)

    if señal == 'COMPRAR' and balance['USDT'] > 10:
        cantidad = (balance['USDT'] * 0.95) / precio
        exchange.create_market_buy_order(simbolo, cantidad)
        return f"COMPRA | {cantidad:.6f} BTC a ${precio:,.2f}"

    elif señal == 'VENDER' and balance['BTC'] > 0.0001:
        exchange.create_market_sell_order(simbolo, balance['BTC'])
        return f"VENTA | {balance['BTC']:.6f} BTC a ${precio:,.2f}"

    return None

def ejecutar_venta_emergencia(simbolo='BTC/USDT'):
    from bot.data import obtener_balance, obtener_precio
    balance = obtener_balance()
    precio = obtener_precio(simbolo)
    if balance['BTC'] > 0.0001:
        exchange.create_market_sell_order(simbolo, balance['BTC'])
        return f"VENTA EMERGENCIA | {balance['BTC']:.6f} BTC a ${precio:,.2f}"
    return None