from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
import plotly.graph_objects as go
import pandas as pd
from PyQt5.QtGui import QPixmap, QPainter
from pandas_ta import momentum
from plotly.subplots import make_subplots
import numpy as np

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QtWidgets.QTabWidget(self)
        self.setCentralWidget(self.central_widget)

        self.candlestick_tab = CandlestickTab()
        self.central_widget.addTab(self.candlestick_tab, "Candlestick")

class CandlestickTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_button = QtWidgets.QPushButton('Load CSV', self)
        self.plot_button = QtWidgets.QPushButton('Show Chart', self)
        self.chart_selector = QtWidgets.QComboBox(self)
        self.browser = QtWebEngineWidgets.QWebEngineView(self)

        vlayout = QtWidgets.QVBoxLayout(self)
        vlayout.addWidget(self.load_button, alignment=QtCore.Qt.AlignHCenter)
        vlayout.addWidget(self.chart_selector, alignment=QtCore.Qt.AlignHCenter)
        vlayout.addWidget(self.plot_button, alignment=QtCore.Qt.AlignHCenter)
        vlayout.addWidget(self.browser)

        self.background_image = QPixmap("fundal.jpeg")

        self.load_button.clicked.connect(self.load_csv)
        self.plot_button.clicked.connect(self.show_selected_chart)
        self.df = None
        self.chart_displayed = None
        self.chart_selector.addItems(["MACD", "RSI", "VWAP", "EMA", "SAR", "Aroon", "Bollinger Bands",
                                      "ROC"])  # Add chart options
        self.resize(1000, 800)


    def load_csv(self):
        self.df = pd.read_csv('crypto2.csv')
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])

        if not self.df.empty:
            QtWidgets.QMessageBox.information(self, "CSV Loaded", "CSV data loaded successfully.")
        else:
            QtWidgets.QMessageBox.warning(self, "Empty CSV", "No data available in the CSV.")

    def calculate_macd(self):
        if self.df is not None and not self.df.empty:
            self.df['12EMA'] = self.df['close'].ewm(span=12, adjust=False).mean()
            self.df['26EMA'] = self.df['close'].ewm(span=26, adjust=False).mean()
            self.df['MACD'] = self.df['12EMA'] - self.df['26EMA']
            self.df['Signal Line'] = self.df['MACD'].ewm(span=9, adjust=False).mean()

    def calculate_rsi(self):
        if self.df is not None and not self.df.empty:
            delta = self.df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()

            rs = avg_gain / avg_loss
            self.df['RSI'] = 100 - (100 / (1 + rs))

    def calculate_ema(self):
        if self.df is not None and not self.df.empty:
            self.df['EMA_10'] = self.df['close'].ewm(span=10, adjust=False).mean()
            self.df['EMA_20'] = self.df['close'].ewm(span=20, adjust=False).mean()

    def calculate_sar(self):
        if self.df is not None and not self.df.empty:
            acceleration = 0.02
            acceleration_max = 0.2
            self.df['SAR'] = self.df['high'].shift(1)
            self.df['SAR_DIRECTION'] = -1
            self.df['EP'] = self.df['low'].rolling(window=2).max()

            for i in range(2, len(self.df)):
                if self.df.loc[i - 1, 'SAR_DIRECTION'] == 1:
                    if self.df.loc[i, 'low'] > self.df.loc[i - 1, 'SAR']:
                        self.df.loc[i, 'SAR_DIRECTION'] = 1
                        acceleration = min(acceleration + 0.02, acceleration_max)
                        self.df.loc[i, 'SAR'] = self.df.loc[i - 1, 'SAR'] + acceleration * (
                                    self.df.loc[i - 1, 'EP'] - self.df.loc[i - 1, 'SAR'])
                        self.df.loc[i, 'EP'] = self.df.loc[i, 'low']
                    else:
                        self.df.loc[i, 'SAR_DIRECTION'] = -1
                        acceleration = 0.02
                        self.df.loc[i, 'SAR'] = self.df.loc[i - 1, 'high']
                        self.df.loc[i, 'EP'] = self.df.loc[i, 'high']
                else:
                    if self.df.loc[i, 'high'] < self.df.loc[i - 1, 'SAR']:
                        self.df.loc[i, 'SAR_DIRECTION'] = -1
                        acceleration = min(acceleration + 0.02, acceleration_max)
                        self.df.loc[i, 'SAR'] = self.df.loc[i - 1, 'SAR'] - acceleration * (
                                    self.df.loc[i - 1, 'SAR'] - self.df.loc[i - 1, 'EP'])
                        self.df.loc[i, 'EP'] = self.df.loc[i, 'high']
                    else:
                        self.df.loc[i, 'SAR_DIRECTION'] = 1
                        acceleration = 0.02
                        self.df.loc[i, 'SAR'] = self.df.loc[i - 1, 'low']
                        self.df.loc[i, 'EP'] = self.df.loc[i, 'low']

    def show_selected_chart(self):
        selected_chart = self.chart_selector.currentText()  # Get the selected chart from the dropdown list

        if selected_chart == "MACD":
            self.show_macd_chart()
        elif selected_chart == "RSI":
            self.show_rsi_chart()
        elif selected_chart == "VWAP":
            self.show_vwap_chart()
        elif selected_chart == "EMA":
            self.show_ema_chart()
        elif selected_chart == "SAR":
            self.show_sar_chart()
        elif selected_chart == "Aroon":
            self.show_aroon_chart()
        elif selected_chart == "Bollinger Bands":
            self.show_bollinger_bands_chart()
        elif selected_chart == "ROC":
            self.show_roc_chart()

    def show_candlestick_chart(self):
        if self.df is not None and not self.df.empty:
            self.calculate_macd()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, row_heights=[0.7, 0.3])

            candlestick_trace = go.Candlestick(x=self.df['timestamp'],
                                               open=self.df['open'],
                                               high=self.df['high'],
                                               low=self.df['low'],
                                               close=self.df['close'],
                                               name='Candlestick')

            macd_trace = go.Scatter(x=self.df['timestamp'], y=self.df['MACD'], mode='lines', line=dict(width=2),
                                    name='MACD')
            signal_trace = go.Scatter(x=self.df['timestamp'], y=self.df['Signal Line'], mode='lines',
                                      name='Signal Line')

            fig.add_trace(candlestick_trace, row=1, col=1)
            fig.add_trace(macd_trace, row=2, col=1)
            fig.add_trace(signal_trace, row=2, col=1)

            fig.update_layout(height=1000)
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            self.chart_displayed = "Candlestick"
        else:
            self.browser.setHtml("<p>No data available for plotting.</p>")



    def show_macd_chart(self):
        if self.df is not None and not self.df.empty:
            self.calculate_macd()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, row_heights=[0.7, 0.3])

            candlestick_trace = go.Candlestick(x=self.df['timestamp'],
                                               open=self.df['open'],
                                               high=self.df['high'],
                                               low=self.df['low'],
                                               close=self.df['close'],
                                               name='Candlestick')

            macd_trace = go.Scatter(x=self.df['timestamp'], y=self.df['MACD'], mode='lines', line=dict(width=2),
                                    name='MACD')
            signal_trace = go.Scatter(x=self.df['timestamp'], y=self.df['Signal Line'], mode='lines',
                                      name='Signal Line')

            fig.add_trace(candlestick_trace, row=1, col=1)
            fig.add_trace(macd_trace, row=2, col=1)
            fig.add_trace(signal_trace, row=2, col=1)

            fig.update_layout(height=1000)
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            self.chart_displayed = "MACD"
        else:
            self.browser.setHtml("<p>No data available for plotting.</p>")
    def calculate_vwap(self):
        if self.df is not None and not self.df.empty:
            self.df['VWAP'] = np.cumsum(self.df['close'] * self.df['volume']) / np.cumsum(self.df['volume'])

    def show_vwap_chart(self):
        self.calculate_vwap()
        if self.df is not None and not self.df.empty:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, row_heights=[0.7, 0.3])

            candlestick_trace = go.Candlestick(x=self.df['timestamp'],
                                               open=self.df['open'],
                                               high=self.df['high'],
                                               low=self.df['low'],
                                               close=self.df['close'],
                                               name='Candlestick')

            vwap_trace = go.Scatter(x=self.df['timestamp'], y=self.df['VWAP'], mode='lines', line=dict(width=2),
                                    name='VWAP')

            fig.add_trace(candlestick_trace, row=1, col=1)
            fig.add_trace(vwap_trace, row=2, col=1)

            fig.update_layout(height=1000)
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        else:
            self.browser.setHtml("<p>No data available for plotting.</p>")

    def calculate_aroon(self):
        if self.df is not None and not self.df.empty:
            period = 14  # Aroon indicator period
            self.df['Aroon_Up'] = 100 * (
                        self.df['high'].rolling(window=period).apply(lambda x: x.argmax()) / (period - 1))
            self.df['Aroon_Down'] = 100 * (
                        self.df['low'].rolling(window=period).apply(lambda x: x.argmin()) / (period - 1))

    def show_aroon_chart(self):
        if self.df is not None and not self.df.empty:
            self.calculate_aroon()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, row_heights=[0.7, 0.3])

            candlestick_trace = go.Candlestick(x=self.df['timestamp'],
                                               open=self.df['open'],
                                               high=self.df['high'],
                                               low=self.df['low'],
                                               close=self.df['close'],
                                               name='Candlestick')

            aroon_up_trace = go.Scatter(x=self.df['timestamp'], y=self.df['Aroon_Up'], mode='lines', line=dict(width=2),
                                        name='Aroon Up')
            aroon_down_trace = go.Scatter(x=self.df['timestamp'], y=self.df['Aroon_Down'], mode='lines',
                                          line=dict(width=2),
                                          name='Aroon Down')

            fig.add_trace(candlestick_trace, row=1, col=1)
            fig.add_trace(aroon_up_trace, row=2, col=1)
            fig.add_trace(aroon_down_trace, row=2, col=1)

            fig.update_layout(height=1000)
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            self.chart_displayed = "Aroon"
        else:
            self.browser.setHtml("<p>No data available for plotting.</p>")

    def calculate_bollinger_bands(self):
        if self.df is not None and not self.df.empty:
            window = 20  # Number of periods for the moving average and standard deviation
            num_std_dev = 2  # Number of standard deviations for the bands

            self.df['SMA'] = self.df['close'].rolling(window=window, min_periods=1).mean()
            self.df['Upper Band'] = self.df['SMA'] + num_std_dev * self.df['close'].rolling(window=window,
                                                                                            min_periods=1).std()
            self.df['Lower Band'] = self.df['SMA'] - num_std_dev * self.df['close'].rolling(window=window,
                                                                                            min_periods=1).std()

    def show_bollinger_bands_chart(self):
        if self.df is not None and not self.df.empty:
            self.calculate_bollinger_bands()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, row_heights=[0.7, 0.3])

            candlestick_trace = go.Candlestick(x=self.df['timestamp'],
                                               open=self.df['open'],
                                               high=self.df['high'],
                                               low=self.df['low'],
                                               close=self.df['close'],
                                               name='Candlestick')

            sma_trace = go.Scatter(x=self.df['timestamp'], y=self.df['SMA'], mode='lines', line=dict(width=2),
                                   name='SMA')
            upper_band_trace = go.Scatter(x=self.df['timestamp'], y=self.df['Upper Band'], mode='lines',
                                          line=dict(width=2),
                                          name='Upper Bollinger Band')
            lower_band_trace = go.Scatter(x=self.df['timestamp'], y=self.df['Lower Band'], mode='lines',
                                          line=dict(width=2),
                                          name='Lower Bollinger Band')

            fig.add_trace(candlestick_trace, row=1, col=1)
            fig.add_trace(sma_trace, row=2, col=1)
            fig.add_trace(upper_band_trace, row=2, col=1)
            fig.add_trace(lower_band_trace, row=2, col=1)

            fig.update_layout(height=1000)
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            self.chart_displayed = "Bollinger Bands"
        else:
            self.browser.setHtml("<p>No data available for plotting.</p>")

    def show_ema_chart(self):
        if self.df is not None and not self.df.empty:
            self.calculate_ema()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, row_heights=[0.7, 0.3])

            candlestick_trace = go.Candlestick(x=self.df['timestamp'],
                                               open=self.df['open'],
                                               high=self.df['high'],
                                               low=self.df['low'],
                                               close=self.df['close'],
                                               name='Candlestick')

            ema_10_trace = go.Scatter(x=self.df['timestamp'], y=self.df['EMA_10'], mode='lines', line=dict(width=2),
                                      name='EMA')
            ema_20_trace = go.Scatter(x=self.df['timestamp'], y=self.df['EMA_20'], mode='lines', line=dict(width=2),
                                      name='SMA')

            fig.add_trace(candlestick_trace, row=1, col=1)
            fig.add_trace(ema_10_trace, row=2, col=1)
            fig.add_trace(ema_20_trace, row=2, col=1)

            fig.update_layout(height=1000)
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            self.chart_displayed = "EMA"
        else:
            self.browser.setHtml("<p>No data available for plotting.</p>")
    def calculate_roc(self):
        if self.df is not None and not self.df.empty:
            period = 14  # ROC indicator period
            self.df['ROC'] = momentum.roc(self.df['close'], length=period)

    def show_roc_chart(self):
        if self.df is not None and not self.df.empty:
            self.calculate_roc()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, row_heights=[0.7, 0.3])

            candlestick_trace = go.Candlestick(x=self.df['timestamp'],
                                               open=self.df['open'],
                                               high=self.df['high'],
                                               low=self.df['low'],
                                               close=self.df['close'],
                                               name='Candlestick')

            roc_trace = go.Scatter(x=self.df['timestamp'], y=self.df['ROC'], mode='lines', line=dict(width=2),
                                   name='ROC')

            fig.add_trace(candlestick_trace, row=1, col=1)
            fig.add_trace(roc_trace, row=2, col=1)

            fig.update_layout(height=1000)
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            self.chart_displayed = "ROC"
        else:
            self.browser.setHtml("<p>No data available for plotting.</p>")

    def show_rsi_chart(self):  # Rename this function to show_rsi_chart
        if self.df is not None and not self.df.empty:
            self.calculate_rsi()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, row_heights=[0.7, 0.3])

            candlestick_trace = go.Candlestick(x=self.df['timestamp'],
                                               open=self.df['open'],
                                               high=self.df['high'],
                                               low=self.df['low'],
                                               close=self.df['close'],
                                               name='Candlestick')

            rsi_trace = go.Scatter(x=self.df['timestamp'], y=self.df['RSI'], mode='lines', line=dict(width=2),
                                   name='RSI')

            fig.add_trace(candlestick_trace, row=1, col=1)
            fig.add_trace(rsi_trace, row=2, col=1)

            fig.update_layout(height=1000)
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            self.chart_displayed = "RSI"
        else:
            self.browser.setHtml("<p>No data available for plotting.</p>")

    def paintEvent(self, event):
        # Desenează imaginea de fundal
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background_image)



    def show_roc_chart(self):
        if self.df is not None and not self.df.empty:
            self.calculate_roc()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, row_heights=[0.7, 0.3])

            candlestick_trace = go.Candlestick(x=self.df['timestamp'],
                                               open=self.df['open'],
                                               high=self.df['high'],
                                               low=self.df['low'],
                                               close=self.df['close'],
                                               name='Candlestick')

            roc_trace = go.Scatter(x=self.df['timestamp'], y=self.df['ROC'], mode='lines', line=dict(width=2),
                                   name='ROC')

            fig.add_trace(candlestick_trace, row=1, col=1)
            fig.add_trace(roc_trace, row=2, col=1)

            fig.update_layout(height=1000)
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            self.chart_displayed = "ROC"
        else:
            self.browser.setHtml("<p>No data available for plotting.</p>")

    def show_sar_chart(self):
        if self.df is not None and not self.df.empty:
            self.calculate_sar()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, row_heights=[0.7, 0.3])

            candlestick_trace = go.Candlestick(x=self.df['timestamp'],
                                               open=self.df['open'],
                                               high=self.df['high'],
                                               low=self.df['low'],
                                               close=self.df['close'],
                                               name='Candlestick')

            sar_trace = go.Scatter(x=self.df['timestamp'], y=self.df['SAR'], mode='markers', marker=dict(size=5),
                                   name='SAR')

            fig.add_trace(candlestick_trace, row=1, col=1)
            fig.add_trace(sar_trace, row=2, col=1)

            fig.update_layout(height=1000)
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            self.chart_displayed = "SAR"
        else:
            self.browser.setHtml("<p>No data available for plotting.</p>")


