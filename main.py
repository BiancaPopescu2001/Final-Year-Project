import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from home import HomeTab
from candlestick import CandlestickTab

from sentiment_analysis import SentimentAnalysisTab
from learning import LearningTab
from alpha_get_data import AlphaGetData

from News2 import CryptoChartApp


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Crypto Hub - Learn & Analysis')
        self.setGeometry(100, 100, 800, 600)
        tabs = QTabWidget()

        tabs.addTab(HomeTab(),"Home")


        tabs.addTab(CandlestickTab(),"Crypto Hub - Learn and Analysis (Tehnical Analysis)")
        tabs.addTab(LearningTab(), "Crypto Hub - Learn and Analysis (Learning)")
        tabs.addTab(CryptoChartApp(), "Crypto Hub - Learn and Analysis (News)")
        tabs.addTab(SentimentAnalysisTab(), "Crypto Hub - Learn and Analysis (Sentiment Analysis)")

        self.setCentralWidget(tabs)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.setGeometry(100, 100, 1300, 700)
    window.show()
    sys.exit(app.exec_())
    
