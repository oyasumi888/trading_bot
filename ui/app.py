import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
from bot.logger import logger
from bot.notificaciones import enviar_mensaje
from bot.data import obtener_datos, obtener_precio, obtener_balance
from bot.strategy import calcular_sma, generar_señal
from bot.risk import verificar_sl_tp, ejecutar_orden, ejecutar_venta_emergencia

class TradingBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Bot")
        self.root.geometry("700x800")
        self.root.configure(bg="#1e1e2e")
        self.corriendo = False
        self.precio_compra = None
        self.build_ui()

    def build_ui(self):
        # Título
        tk.Label(self.root, text="🤖 Trading Bot", font=("Helvetica", 18, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=10)
        
        # Selector de cripto
        frame_cripto = tk.Frame(self.root, bg="#1e1e2e")
        frame_cripto.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_cripto, text="Par:", font=("Helvetica", 11),
            bg="#1e1e2e", fg="#cdd6f4").pack(side="left", padx=5)

        self.simbolo = ttk.Combobox(frame_cripto, width=12, font=("Helvetica", 11),
                                values=["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"],
                                state="readonly")
        self.simbolo.set("BTC/USDT")
        self.simbolo.pack(side="left", padx=5)

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

        # Frame de configuracion
        frame_config = tk.Frame(self.root, bg="#313244", padx=20, pady=10)
        frame_config.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_config, text="Stop Loss %:", font=("Helvetica", 11),
                 bg="#313244", fg="#cdd6f4").grid(row=0, column=0, sticky="w", padx=5)
        self.stop_loss = tk.Entry(frame_config, width=6, font=("Helvetica", 11),
                                  bg="#181825", fg="#cdd6f4", insertbackground="white")
        self.stop_loss.insert(0, "3")
        self.stop_loss.grid(row=0, column=1, padx=5)

        tk.Label(frame_config, text="Take Profit %:", font=("Helvetica", 11),
                 bg="#313244", fg="#cdd6f4").grid(row=0, column=2, sticky="w", padx=5)
        self.take_profit = tk.Entry(frame_config, width=6, font=("Helvetica", 11),
                                    bg="#181825", fg="#cdd6f4", insertbackground="white")
        self.take_profit.insert(0, "5")
        self.take_profit.grid(row=0, column=3, padx=5)

        # Botón
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
                           relief="flat", state="disabled", height=8)
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
                ahora = datetime.now().strftime('%H:%M:%S')
                simbolo = self.simbolo.get()

                df = obtener_datos(simbolo)
                df = calcular_sma(df)
                señal = generar_señal(df)
                precio = obtener_precio(simbolo)
                balance = obtener_balance()

                # Actualizar UI
                self.root.title(f"Trading Bot - {simbolo}")
                self.lbl_precio.config(text=f"Precio {simbolo}: ${precio:,.2f}")
                self.lbl_usdt.config(text=f"Balance USDT: ${balance['USDT']:,.2f}")
                self.lbl_btc.config(text=f"Balance {simbolo.split('/')[0]}: {balance.get(simbolo.split('/')[0], 0):.6f}")
                self.lbl_ultima.config(text=f"Última actualización: {ahora}")

                colores = {'COMPRAR': '#a6e3a1', 'VENDER': '#f38ba8', 'ESPERAR': '#f9e2af'}
                self.lbl_señal.config(text=f"Señal: {señal}", fg=colores[señal])

                self.actualizar_grafica(df)

                # Verificar SL/TP
                sl_tp = verificar_sl_tp(
                    precio, self.precio_compra,
                    float(self.stop_loss.get()),
                    float(self.take_profit.get())
                )

                if sl_tp:
                    resultado = ejecutar_venta_emergencia(simbolo)
                    if resultado:
                        self.agregar_log(f"[{ahora}] 🚨 {sl_tp} | {resultado}")
                        logger.warning(f"{sl_tp} | {resultado}")
                        enviar_mensaje(f"🚨 <b>{sl_tp}</b>\n{resultado}")
                        self.precio_compra = None
                else:
                    resultado = ejecutar_orden(señal, simbolo)
                    if resultado:
                        if 'COMPRA' in resultado:
                            self.precio_compra = precio
                            enviar_mensaje(f"✅ <b>COMPRA ejecutada</b>\n{resultado}")
                        elif 'VENTA' in resultado:
                            self.precio_compra = None
                            enviar_mensaje(f"✅ <b>VENTA ejecutada</b>\n{resultado}")
                        self.agregar_log(f"[{ahora}] ✅ {resultado}")
                        logger.info(f"ORDEN | {resultado}")
                    else:
                        self.agregar_log(f"[{ahora}] ⏸ {señal}")
                        logger.info(f"SEÑAL | {señal} | Precio: ${precio:,.2f}")

            except Exception as e:
                self.agregar_log(f"❌ Error: {e}")
                logger.error(f"ERROR | {e}")
            
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