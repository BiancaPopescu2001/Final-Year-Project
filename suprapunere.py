import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pandas_ta import momentum

class CryptoChartApp(QMainWindow):
    def __init__(self, indicator='MACD'):
        super().__init__()

        self.setWindowTitle("Crypto Hub - Learn & Analyze (Learning - Indicators)")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.canvas = FigureCanvas(plt.figure())
        self.layout.addWidget(self.canvas)

        self.load_data()
        self.calculate_indicators(indicator)
        self.plot_chart(indicator)


    def load_data(self):
        self.data = pd.read_csv('crypto_static.csv')
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        self.data.set_index('timestamp', inplace=True)

    def calculate_indicators(self, indicator):
        if indicator == 'MACD':
            self.data['12ema'] = self.data['close'].ewm(span=12, adjust=False).mean()
            self.data['26ema'] = self.data['close'].ewm(span=26, adjust=False).mean()
            self.data['macd'] = self.data['12ema'] - self.data['26ema']
            self.data['signal'] = self.data['macd'].ewm(span=9, adjust=False).mean()
        elif indicator == 'RSI':
            self.data['RSI'] = self.data['close'].rolling(window=14).apply(self.calculate_rsi, raw=False)
        elif indicator == 'VWAP':
            self.calculate_vwap()
        elif indicator == 'EMA':
            self.calculate_ema()
        elif indicator == 'AROON':  # Add this block for Aroon indicator
            self.calculate_aroon()
        elif indicator == 'BOLLINGER':
            self.calculate_bollinger_bands()
        elif indicator == 'ROC':  # Add this block for ROC indicator
            self.calculate_roc()
        elif indicator == 'ADI':  # Add this block for ADI indicator
            self.calculate_adi()
        elif indicator == 'SAR':  # Add this block for SAR indicator
            self.calculate_sar()

    def calculate_rsi(self, prices):
        diff = prices.diff()
        gain = diff[diff > 0].sum()
        loss = -diff[diff < 0].sum()
        avg_gain = gain / 14
        avg_loss = loss / 14
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_vwap(self):
        self.data['VWAP'] = (self.data['volume'] * (self.data['high'] + self.data['low'] + self.data['close']) / 3).cumsum() / \
                            self.data['volume'].cumsum()

    def calculate_ema(self):
        self.data['EMA_10'] = self.data['close'].ewm(span=10, adjust=False).mean()
        self.data['EMA_20'] = self.data['close'].ewm(span=20, adjust=False).mean()

    def calculate_aroon(self):
        period = 14  # Aroon indicator period
        self.data['Aroon_Up'] = 100 * (
                    self.data['high'].rolling(window=period).apply(lambda x: x.argmax()) / (period - 1))
        self.data['Aroon_Down'] = 100 * (
                    self.data['low'].rolling(window=period).apply(lambda x: x.argmin()) / (period - 1))

    def calculate_bollinger_bands(self):
        window = 20  # Number of periods for the moving average and standard deviation
        num_std_dev = 2  # Number of standard deviations for the bands

        self.data['SMA'] = self.data['close'].rolling(window=window, min_periods=1).mean()
        self.data['Upper Band'] = self.data['SMA'] + num_std_dev * self.data['close'].rolling(window=window,
                                                                                              min_periods=1).std()
        self.data['Lower Band'] = self.data['SMA'] - num_std_dev * self.data['close'].rolling(window=window,
                                                                                              min_periods=1).std()


    def calculate_roc(self):

        period = 14  # ROC indicator period
        self.data['ROC'] = momentum.roc(self.data['close'], length=period)

    def calculate_adi(self):

        self.data['ADI'] = self.calculate_manual_adi()

    def calculate_manual_adi(self):
        adi_values = []
        adi = 0

        for i in range(len(self.data)):
            if i == 0:
                adi_values.append(0)
            else:
                clv = ((self.data['close'][i] - self.data['low'][i]) - (self.data['high'][i] - self.data['close'][i])) / \
                      (self.data['high'][i] - self.data['low'][i])
                adi += clv * self.data['volume'][i]
                adi_values.append(adi)

        return adi_values

    def calculate_sar(self):
        acceleration = 0.02
        acceleration_max = 0.2
        self.data['SAR'] = self.data['high'].shift(1)  # Initialize SAR with previous high
        self.data['EP'] = self.data['low'].rolling(window=2).max()  # Initial extreme point

        for i in range(2, len(self.data)):
            if self.data['SAR'][i - 1] < self.data['high'][i - 1]:  # Previous SAR was below previous high
                if self.data['SAR'][i - 1] < self.data['low'][i]:  # Previous SAR was below current low
                    self.data['SAR'][i] = self.data['low'][i - 1]  # SAR switches to lowest low
                    self.data['EP'][i] = self.data['low'][i]  # New extreme point
                else:
                    self.data['SAR'][i] = self.data['SAR'][i - 1] + acceleration * (
                                self.data['EP'][i - 1] - self.data['SAR'][i - 1])
                    if self.data['high'][i] > self.data['EP'][i - 1]:  # Update extreme point if current high is higher
                        self.data['EP'][i] = self.data['high'][i]
                    else:
                        self.data['EP'][i] = self.data['EP'][i - 1]
            else:  # Previous SAR was above previous high
                if self.data['SAR'][i - 1] > self.data['high'][i]:  # Previous SAR was above current high
                    self.data['SAR'][i] = self.data['high'][i - 1]  # SAR switches to highest high
                    self.data['EP'][i] = self.data['high'][i]  # New extreme point
                else:
                    self.data['SAR'][i] = self.data['SAR'][i - 1] - acceleration * (
                                self.data['SAR'][i - 1] - self.data['EP'][i - 1])
                    if self.data['low'][i] < self.data['EP'][i - 1]:  # Update extreme point if current low is lower
                        self.data['EP'][i] = self.data['low'][i]
                    else:
                        self.data['EP'][i] = self.data['EP'][i - 1]

    def plot_chart(self, indicator):
        ohlc = self.data[['open', 'high', 'low', 'close', 'volume']]
        if indicator == 'MACD':
            addplots = [
                mpf.make_addplot(self.data['macd'], color='red'),
                mpf.make_addplot(self.data['signal'], color='blue')
            ]
            title = 'MACD'
        elif indicator == 'RSI':
            addplots = [mpf.make_addplot(self.data['RSI'], color='orange')]
            title = 'Candlestick Chart with RSI'
        elif indicator == 'VWAP':
            addplots = [mpf.make_addplot(self.data['VWAP'], color='#00FF00')] #lime
            title = 'Candlestick Chart with VWAP'
        elif indicator == 'EMA':
            addplots = [
                mpf.make_addplot(self.data['EMA_10'], color='green'),
                mpf.make_addplot(self.data['EMA_20'], color='#FF00FF')
            ]
            title = 'Candlestick Chart with EMA'
        elif indicator == 'AROON':  # Add this block for Aroon indicator
            addplots = [
                mpf.make_addplot(self.data['Aroon_Up'], color='green'),
                mpf.make_addplot(self.data['Aroon_Down'], color='#FF00FF')
            ]
            title = 'Candlestick Chart with Aroon'
        elif indicator == 'BOLLINGER':
            addplots = [
                mpf.make_addplot(self.data['Upper Band'], color='purple'),
                mpf.make_addplot(self.data['Lower Band'], color='orange')
            ]
            title = 'Candlestick Chart with Bollinger Bands'
        elif indicator == 'ROC':  # Add this block for ROC indicator
            addplots = [mpf.make_addplot(self.data['ROC'], color='#00FF00')]
            title = 'Candlestick Chart with ROC'
        elif indicator == 'ADI':  # Add this block for ADI indicator
            addplots = [mpf.make_addplot(self.data['ADI'], color='purple')]
            title = 'Candlestick Chart with ADI'
        elif indicator == 'SAR':  # Add this block for SAR indicator
            addplots = [mpf.make_addplot(self.data['SAR'], color='#FF00FF')]
            title = 'Candlestick Chart with SAR'



        fig, axes = mpf.plot(ohlc, type= 'candle', style='kenan',title=title,
                             ylabel='Price', volume=True,
                             addplot=addplots,
                             panel_ratios=(3, 1),
                             returnfig=True)

        self.canvas.figure = fig
        self.canvas.draw()

def main():
    app = QApplication(sys.argv)
    indicator = 'MACD'  # Default indicator, you can change it to 'RSI' or 'VWAP' if you want a different default
    if len(sys.argv) > 1:
        indicator = sys.argv[1]
    window = CryptoChartApp(indicator)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
