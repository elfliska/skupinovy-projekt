import sys
import random
import time
import requests  # Opraveno na správný import
from binance.client import Client
from binance.enums import *
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QMessageBox, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Binance API klíče (nahraďte svými)
api_key = 'pzyZD961Lbiz1SW0nrCiBtsciigrdt4viWnB8BA01Ga3YjHplDTdDnk5gq1tt0Yu'  # Sem dejte svůj Binance API klíč
api_secret = 'UIN4VL2kIEvGVW4UJbAZAYI2Vhfq7EEKmjaqlKqCMcbYt1MsORUEhTbhVnjrkiiQ'  # Sem dejte svůj Binance API secret klíč

# Inicializace klienta Binance
client = Client(api_key, api_secret)

# Počáteční kapitál
initial_capital = 10000  # Počáteční kapitál v USD
current_balance = initial_capital
virtual_balance = current_balance  # Virtuální zůstatek pro demo trading

# Funkce pro získání historických dat pro svíčkový graf
def get_candlestick_data(symbol, interval='1h', limit=100):
    # Získáme historická data pro BTC a ETH (například 100 svíček)
    klines = client.get_historical_klines(symbol, interval, limit=limit)
    ohlc = []
    for kline in klines:
        ohlc.append([float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4])])  # Open, High, Low, Close
    return ohlc

# Funkce pro investování do kryptoměny (simulace nákupu)
def invest_crypto(symbol, amount_in_usd):
    price = get_crypto_price(symbol)
    amount_to_buy = amount_in_usd / price
    return amount_to_buy, price

# Funkce pro získání aktuální ceny kryptoměny z Binance
def get_crypto_price(symbol):
    avg_price = client.get_avg_price(symbol=symbol)
    return float(avg_price['price'])

# Funkce pro demo trading - long a short
def demo_trading(symbol, action, amount_in_usd):
    global virtual_balance
    if action == 'long':
        # Nákup kryptoměny (long)
        amount_bought, buy_price = invest_crypto(symbol, amount_in_usd)
        virtual_balance -= amount_in_usd
        result = f"Zakoupeno {amount_bought:.4f} {symbol} za cenu {buy_price:.2f} USD."
    elif action == 'short':
        # Prodej kryptoměny (short)
        amount_bought, buy_price = invest_crypto(symbol, amount_in_usd)
        amount_sold, sell_price = sell_crypto(symbol, amount_bought, virtual_balance)
        virtual_balance += amount_sold
        result = f"Prodáno {amount_bought:.4f} {symbol} za cenu {sell_price:.2f} USD. Zůstatek: {virtual_balance:.2f} USD."

    return result

# Funkce pro prodej kryptoměny (simulace prodeje)
def sell_crypto(symbol, amount, current_balance):
    price = get_crypto_price(symbol)
    amount_in_usd = amount * price
    new_balance = current_balance + amount_in_usd
    return new_balance, price

# GUI aplikace
class TradingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Demo Trading Binance')
        self.setGeometry(100, 100, 800, 600)

        # Tmavé a fialové barevné schéma pro UI
        self.setStyleSheet("background-color: #2e2e2e; color: white;")

        # Vytvoření layoutu pro okno
        layout = QVBoxLayout()

        # Titulní text
        self.title_label = QLabel("Simulace demo tradingu s Binance API")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #8a2be2;")
        layout.addWidget(self.title_label)

        # ComboBox pro výběr kryptoměny (BTC nebo ETH)
        self.crypto_combobox = QComboBox()
        self.crypto_combobox.addItem("BTCUSDT")  # Bitcoin
        self.crypto_combobox.addItem("ETHUSDT")  # Ethereum
        layout.addWidget(self.crypto_combobox)

        # Textové pole pro zadání částky pro investici
        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Zadejte částku v USD")
        self.amount_input.setStyleSheet("background-color: #3c3c3c; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.amount_input)

        # Tlačítko pro dlouhý obchod (long)
        self.long_button = QPushButton("Investovat (Long)", self)
        self.long_button.setStyleSheet("background-color: #8a2be2; color: white; padding: 10px; border-radius: 5px;")
        self.long_button.clicked.connect(self.long_trade)
        layout.addWidget(self.long_button)

        # Tlačítko pro krátký obchod (short)
        self.short_button = QPushButton("Prodat (Short)", self)
        self.short_button.setStyleSheet("background-color: #8a2be2; color: white; padding: 10px; border-radius: 5px;")
        self.short_button.clicked.connect(self.short_trade)
        layout.addWidget(self.short_button)

        # Tlačítko pro zobrazení aktuálního zůstatku
        self.balance_button = QPushButton("Zobrazit aktuální zůstatek", self)
        self.balance_button.setStyleSheet("background-color: #8a2be2; color: white; padding: 10px; border-radius: 5px;")
        self.balance_button.clicked.connect(self.show_balance)
        layout.addWidget(self.balance_button)

        # Aktuální zůstatek label
        self.balance_label = QLabel(f"Aktuální virtuální zůstatek: {virtual_balance} USD")
        layout.addWidget(self.balance_label)

        # Přidání grafu do UI
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Získání a zobrazení svíčkového grafu
        self.update_candlestick_chart()

        # Nastavení hlavního layoutu pro okno
        self.setLayout(layout)

    def long_trade(self):
        action = 'long'
        amount = float(self.amount_input.text())  # Přečteme částku z textového pole
        symbol = self.crypto_combobox.currentText()  # Získáme vybranou kryptoměnu
        result = demo_trading(symbol, action, amount)
        QMessageBox.information(self, "Investice (Long)", result)
        self.update_balance()

    def short_trade(self):
        action = 'short'
        amount = float(self.amount_input.text())  # Přečteme částku z textového pole
        symbol = self.crypto_combobox.currentText()  # Získáme vybranou kryptoměnu
        result = demo_trading(symbol, action, amount)
        QMessageBox.information(self, "Prodej (Short)", result)
        self.update_balance()

    def show_balance(self):
        QMessageBox.information(self, "Aktuální zůstatek", f"Aktuální virtuální zůstatek: {virtual_balance:.2f} USD")

    def update_balance(self):
        # Aktualizuje zůstatek v GUI
        self.balance_label.setText(f"Aktuální virtuální zůstatek: {virtual_balance:.2f} USD")

    def update_candlestick_chart(self):
        symbol = self.crypto_combobox.currentText()  # Získáme vybranou kryptoměnu
        data = get_candlestick_data(symbol)  # Získáme historická data
        opens = [item[0] for item in data]
        highs = [item[1] for item in data]
        lows = [item[2] for item in data]
        closes = [item[3] for item in data]

        self.ax.clear()  # Vymazání předchozího grafu
        for i in range(len(data)):
            color = 'green' if closes[i] > opens[i] else 'red'
            self.ax.plot([i, i], [lows[i], highs[i]], color=color)  # Vykreslení vertikální části svíčky
            self.ax.plot([i-0.2, i+0.2], [opens[i], opens[i]], color=color, linewidth=6)  # Dolní část svíčky
            self.ax.plot([i-0.2, i+0.2], [closes[i], closes[i]], color=color, linewidth=6)  # Horní část svíčky

        # Nastavíme pozice pro označení osy X
        num_ticks = len(data) // 5  # Počet tick hodnot na ose X
        tick_positions = range(0, len(data), num_ticks)  # Pozice pro tick hodnoty na ose X
        self.ax.set_xticks(tick_positions)

        # Nastavení hodnot pro tick hodnoty (počet hodnot na ose X by měl odpovídat počtu tick pozic)
        self.ax.set_xticklabels([str(i) for i in tick_positions])  # Odpovídající štítky

        self.ca  nvas.draw()  # Aktualizace grafu

# Spuštění aplikace
def main():
    app = QApplication(sys.argv)
    window = TradingApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()