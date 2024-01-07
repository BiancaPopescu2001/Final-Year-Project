# from requests_html import HTMLSession
from urllib.parse import urljoin
import requests
import pandas as pd
import plotly.graph_objects as go
class AlphaGetData:
    def __init__(self, symbol, market, time_series, interval):
        self.symbol = symbol
        self.market = market
        self.time_series = time_series
        self.interval = interval
        self.api_key = '1C7ABR2QCUTNPBF2'  # Înlocuiți cu cheia dvs. API Alpha Vantage

    def get_data_with_interval(self):
        function = 'CRYPTO_INTRADAY' if self.time_series == 'Today' else 'DIGITAL_CURRENCY_' + self.time_series
        url = f'https://www.alphavantage.co/query?function={function}&symbol={self.symbol}&market={self.market}&interval={self.interval}&apikey={self.api_key}'

        response = requests.get(url)
        data = response.json()
        time_series_data = None
        for key, value in data.items():
            if key.startswith('Time Series') or key.startswith('Digital Currency'):
                time_series_data = value
                break

        if time_series_data is not None:
            df = pd.DataFrame(time_series_data).T
            return df
        else:
            return None

    def get_data_without_interval(self):
        function = 'DIGITAL_CURRENCY_' + self.time_series
        url = f'https://www.alphavantage.co/query?function={function}&symbol={self.symbol}&market={self.market}&apikey={self.api_key}'

        response = requests.get(url)
        data = response.json()
        time_series_data = None
        for key, value in data.items():
            if key.startswith('Time Series') or key.startswith('Digital Currency'):
                time_series_data = value
                break

        if time_series_data is not None:
            df = pd.DataFrame(time_series_data).T
            return df
        else:
            return None

