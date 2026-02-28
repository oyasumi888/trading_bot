def calcular_sma(df):
    df['sma20'] = df['close'].rolling(20).mean()
    df['sma50'] = df['close'].rolling(50).mean()
    return df.dropna()

def generar_señal(df):
    u, a = df.iloc[-1], df.iloc[-2]
    if a['sma20'] <= a['sma50'] and u['sma20'] > u['sma50']:
        return 'COMPRAR'
    elif a['sma20'] >= a['sma50'] and u['sma20'] < u['sma50']:
        return 'VENDER'
    return 'ESPERAR'