from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QPushButton, QMessageBox
from alpha_get_data import AlphaGetData
import sys
from PyQt5.QtWidgets import QApplication
import pandas as pd


class HomeTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.background_image = QPixmap("fundal.jpeg")

        # Adaugăm un stil pentru text
        title_style = "font-size: 18px; color: white;"
        combo_style = "font-size: 14px; color: white; background-color: black;"

        title_label = QLabel(" ")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet(title_style)

        symbol_label = QLabel("Please, choose a symbol:")
        symbol_label.setStyleSheet(title_style)


        market_label = QLabel("Please, choose a market:")
        market_label.setStyleSheet(title_style)


        time_series_label = QLabel("Please, choose a time series:")
        time_series_label.setStyleSheet(title_style)


        interval_label = QLabel("Please, choose an interval:")
        interval_label.setStyleSheet(title_style)

        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(["BTC", "ETH", "ADA", "DOT", "SOL"])
        self.symbol_combo.setStyleSheet("font-size: 12px; height: 20px; max-width: 100px;")

        self.market_combo = QComboBox()
        self.market_combo.addItems(["USD", "EUR", "RON"])
        self.market_combo.setCurrentIndex(0)  # Set default to USD
        self.market_combo.setStyleSheet("font-size: 12px; height: 20px; max-width: 100px;")

        self.time_series_combo = QComboBox()
        self.time_series_combo.addItems(["Daily","Today", "Weekly", "Monthly"])
        self.time_series_combo.setStyleSheet("font-size: 12px; height: 20px; max-width: 100px;")
        self.time_series_combo.currentTextChanged.connect(self.update_interval_combo)

        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1min", "5min", "15min"])
        self.interval_combo.setStyleSheet("font-size: 12px; height: 20px; max-width: 100px;")
        self.interval_combo.setDisabled(True)  # Initially disabled

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.show_popup)

        layout.addWidget(title_label)
        layout.addWidget(symbol_label)
        layout.addWidget(self.symbol_combo)
        layout.addWidget(market_label)
        layout.addWidget(self.market_combo)
        layout.addWidget(time_series_label)
        layout.addWidget(self.time_series_combo)
        layout.addWidget(interval_label)
        layout.addWidget(self.interval_combo)
        layout.addWidget(self.send_button)


        self.setLayout(layout)

    def update_interval_combo(self, text):
        if text == "Today":
            self.interval_combo.setDisabled(False)
        else:
            self.interval_combo.setDisabled(True)

    def paintEvent(self, event):
        # Desenează imaginea de fundal
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background_image)

    def show_popup(self):
        symbol = self.symbol_combo.currentText()
        market = self.market_combo.currentText()
        time_series = self.time_series_combo.currentText()
        interval = None

        if time_series == "Today":
            interval = self.interval_combo.currentText()

        alpha_get_data = AlphaGetData(symbol, market, time_series, interval)

        if interval is not None:
            data = alpha_get_data.get_data_with_interval()
        else:
            data = alpha_get_data.get_data_without_interval()

        if data is not None and  not data.empty:
            data.rename_axis('timestamp', inplace=True)
            if time_series == "Today":
                # Dacă intervalul este "Today", folosește cele 6 coloane
                data.rename(columns={
                    'index': 'timestamp',
                    '1. open': 'open',
                    '2. high': 'high',
                    '3. low': 'low',
                    '4. close': 'close',
                    '5. volume': 'volume'
                }, inplace=True)
                data_frame_reset = data.reset_index()
                data_frame_reset.to_csv('crypto2.csv', index=False)  # Salvează în CSV
            else:
                data_frame_reset = data.reset_index()
                data_frame_reset.to_csv('crypto2.csv', index=False)  # Salvează în CSV

                df = pd.read_csv('crypto2.csv')
                coloane_dorite = ['timestamp', '1a. open (USD)', '2a. high (USD)', '3a. low (USD)', '4a. close (USD)',
                                  '5. volume']
                df = df[coloane_dorite]
                df = df.rename(columns={
                    '1a. open (USD)': 'open',
                    '2a. high (USD)': 'high',
                    '3a. low (USD)': 'low',
                    '4a. close (USD)': 'close',
                    '5. volume': 'volume'
                })
                df.to_csv('crypto2.csv', index=False)




        popup = QMessageBox()
        popup.setWindowTitle("Data Downloaded")
        popup.setText("Your data has been downloaded. You can now see the graphics.")
        popup.exec_()

