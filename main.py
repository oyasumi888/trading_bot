import tkinter as tk
from ui.app import TradingBotUI

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotUI(root)
    root.mainloop()