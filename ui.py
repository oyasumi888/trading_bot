import tkinter as tk
from tkinter import ttk
import threading
import time
import ccxt
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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

# ── Lógica del bot ──────────────────────────────────────────
def obtener_datos():
    velas = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)
    df = pd.DataFrame(velas, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
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

def ejecutar_orden(señal):
    balance = exchange.fetch_balance()
    usdt = balance['total'].get('USDT', 0)
    btc = balance['total'].get('BTC', 0)
    precio = exchange.fetch_ticker('BTC/USDT')['last']

    if señal == 'COMPRAR' and usdt > 10:
        cantidad = (usdt * 0.95) / precio
        exchange.create_market_buy_order('BTC/USDT', cantidad)
        return f"COMPRA | {cantidad:.6f} BTC a ${precio:.2f}"
    elif señal == 'VENDER' and btc > 0.0001:
        exchange.create_market_sell_order('BTC/USDT', btc)
        return f"VENTA | {btc:.6f} BTC a ${precio:.2f}"
    return None

# ── Interfaz ────────────────────────────────────────────────
class TradingBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Bot - BTC/USDT")
        self.root.geometry("700x750")
        self.root.configure(bg="#1e1e2e")
        self.corriendo = False
        self.build_ui()

    def build_ui(self):
        # Título
        tk.Label(self.root, text="🤖 Trading Bot", font=("Helvetica", 18, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=10)

        # Frame de stats
        frame_stats = tk.Frame(self.root, bg="#313244", padx=20, pady=10)
        frame_stats.pack(fill="x", padx=20, pady=5)

        self.lbl_precio = tk.Label(frame_stats, text="Precio BTC: --", font=("Helvetica", 12),
                                   bg="#313244", fg="#cdd6f4")
        self.lbl_precio.grid(row=0, column=0, sticky="w", pady=2)

        self.lbl_usdt = tk.Label(frame_stats, text="Balance USDT: --", font=("Helvetica", 12),
                                 bg="#313244", fg="#a6e3a1")
        self.lbl_usdt.grid(row=1, column=0, sticky="w", pady=2)

        self.lbl_btc = tk.Label(frame_stats, text="Balance BTC: --", font=("Helvetica", 12),
                                bg="#313244", fg="#a6e3a1")
        self.lbl_btc.grid(row=2, column=0, sticky="w", pady=2)

        self.lbl_señal = tk.Label(frame_stats, text="Señal: --", font=("Helvetica", 14, "bold"),
                                  bg="#313244", fg="#f9e2af")
        self.lbl_señal.grid(row=3, column=0, sticky="w", pady=2)

        self.lbl_ultima = tk.Label(frame_stats, text="Última actualización: --", font=("Helvetica", 10),
                                   bg="#313244", fg="#6c7086")
        self.lbl_ultima.grid(row=4, column=0, sticky="w", pady=2)

        # Botón iniciar/detener
        self.btn = tk.Button(self.root, text="▶ Iniciar Bot", font=("Helvetica", 12, "bold"),
                             bg="#a6e3a1", fg="#1e1e2e", relief="flat", padx=20, pady=8,
                             command=self.toggle_bot)
        self.btn.pack(pady=10)

        # Gráfica
        frame_grafica = tk.Frame(self.root, bg="#1e1e2e")
        frame_grafica.pack(fill="both", expand=True, padx=20, pady=5)

        self.figura = Figure(figsize=(6, 3), facecolor="#1e1e2e")
        self.ax = self.figura.add_subplot(111)
        self.ax.set_facecolor("#181825")

        self.canvas = FigureCanvasTkAgg(self.figura, master=frame_grafica)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Historial
        tk.Label(self.root, text="Historial de operaciones", font=("Helvetica", 11, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack()

        frame_log = tk.Frame(self.root, bg="#1e1e2e")
        frame_log.pack(fill="both", expand=True, padx=20, pady=5)

        self.log = tk.Text(frame_log, bg="#181825", fg="#cdd6f4", font=("Courier", 10),
                           relief="flat", state="disabled", height=10)
        self.log.pack(fill="both", expand=True)

    def toggle_bot(self):
        if not self.corriendo:
            self.corriendo = True
            self.btn.config(text="⏹ Detener Bot", bg="#f38ba8")
            threading.Thread(target=self.loop_bot, daemon=True).start()
        else:
            self.corriendo = False
            self.btn.config(text="▶ Iniciar Bot", bg="#a6e3a1")

    def loop_bot(self):
        while self.corriendo:
            try:
                df = obtener_datos()
                señal = generar_señal(df)
                self.actualizar_grafica(df)
                balance = exchange.fetch_balance()
                precio = exchange.fetch_ticker('BTC/USDT')['last']
                usdt = balance['total'].get('USDT', 0)
                btc = balance['total'].get('BTC', 0)
                ahora = datetime.now().strftime('%H:%M:%S')

                # Actualizar UI
                self.lbl_precio.config(text=f"Precio BTC: ${precio:,.2f}")
                self.lbl_usdt.config(text=f"Balance USDT: ${usdt:,.2f}")
                self.lbl_btc.config(text=f"Balance BTC: {btc:.6f}")
                self.lbl_ultima.config(text=f"Última actualización: {ahora}")

                colores = {'COMPRAR': '#a6e3a1', 'VENDER': '#f38ba8', 'ESPERAR': '#f9e2af'}
                self.lbl_señal.config(text=f"Señal: {señal}", fg=colores[señal])

                # Ejecutar orden si hay señal
                resultado = ejecutar_orden(señal)
                if resultado:
                    self.agregar_log(f"[{ahora}] ✅ {resultado}")
                else:
                    self.agregar_log(f"[{ahora}] ⏸ {señal}")

            except Exception as e:
                self.agregar_log(f"❌ Error: {e}")

            time.sleep(60)

    def actualizar_grafica(self, df):
        self.ax.clear()
        self.ax.set_facecolor("#181825")

        self.ax.plot(df['timestamp'], df['close'], color="#cdd6f4", linewidth=1, label="Precio")
        self.ax.plot(df['timestamp'], df['sma20'], color="#a6e3a1", linewidth=1.5, label="SMA20")
        self.ax.plot(df['timestamp'], df['sma50'], color="#f38ba8", linewidth=1.5, label="SMA50")

        self.ax.legend(loc="upper left", facecolor="#313244", labelcolor="#cdd6f4", fontsize=8)
        self.ax.tick_params(colors="#6c7086", labelsize=7)
        self.ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m/%d %H:%M'))
        self.figura.autofmt_xdate(rotation=30)

        for spine in self.ax.spines.values():
            spine.set_edgecolor("#313244")

        self.canvas.draw()

    def agregar_log(self, texto):
        self.log.config(state="normal")
        self.log.insert("end", texto + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

# ── Main ────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotUI(root)
    root.mainloop()