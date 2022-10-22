import timeit

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import date
from typing import List


class HistoryPrices:
    def __init__(
            self,
            dates: list[float],
            oopen: list[float],
            high: list[float],
            low: list[float],
            close: list[float],
            adj_close: list[float],
            volume: list[float],
    ):
        self.dates = dates
        self.oopen = oopen
        self.high = high
        self.low = low
        self.close = close
        self.adj_close = adj_close
        self.volume = volume


class Asset:

    def __init__(self, ticker: str):
        self.info = yf.Ticker(ticker).info
        self.historical_market_data = self.get_historical_data(ticker)

    def get_historical_data(self, ticker):
        raw_data = yf.download(ticker, end='2020-11-18').sort_values(
            by='Date',
            ascending=False,
        )
        cleaned_data = raw_data.drop(
            raw_data[raw_data['Low'] == raw_data['High']].index
        )
        cleaned_data = cleaned_data.drop(
            cleaned_data[cleaned_data['Open'] == 0].index
        )
        cleaned_data['C_to_C_Return'] = (
                cleaned_data['Adj Close'].pct_change() * 100
        ).round(3)
        cleaned_data['H_to_L_Return'] = self.get_percentage(
            cleaned_data['High'],
            cleaned_data['Low'],
        )
        cleaned_data['O_to_C_Return'] = self.get_percentage(
            cleaned_data['Close'],
            cleaned_data['Open'],
        )
        return cleaned_data

    def get_financials(self):
        return yf.Ticker(self.info['symbol']).financials

    def get_range_count(self, data):
        # Purpose: Histogram
        ranges = {i: 0 for i in np.arange(-2, 2.5, 0.5)}
        for key in ranges.keys():
            if key <= -2:
                ranges[key] = data[data <= key].count()
            elif key >= 2:
                ranges[key] = data[data >= key].count()
            else:
                ranges[key] = data[(data > key) & (data < key + 0.5)].count()
        return ranges

    def get_mean(self, df):
        return df.to_frame().mean(0)

    def get_kurtosis(self, df):
        # Benchmark of 2: More than the benchmark means that the tails are
        # going to be fatter compared to standard deviation.
        return df.to_frame().kurt(0)

    def get_skewness(self, df):
        # Benchmark of 0: More or less than 0 represents how likely is to get
        # positive or negative return compared to standard deviation
        return df.to_frame().skew(0)

    def get_std_err(self, df):
        return df.to_frame().sem(0)

    def get_median(self, df):
        return df.to_frame().median()

    def get_mode(self, df):
        return df.to_frame().mode(axis=0)

    def get_percentage(self, a, b):
        return (((a - b) / b) * 100).round(3)


stock = Asset('^GSPC')
# print(stock.historical_market_data)
# print(stock.get_range_count(stock.historical_market_data['O_to_C_Return']))
print(
    f"KURTOSIS: {stock.get_kurtosis(stock.historical_market_data['C_to_C_Return'])}")
print(
    f"SKEWNESS: {stock.get_skewness(stock.historical_market_data['C_to_C_Return'])}")
print(f"MEAN: {stock.get_mean(stock.historical_market_data['C_to_C_Return'])}")
print(
    f"STANDARD ERROR: {stock.get_std_err(stock.historical_market_data['C_to_C_Return'])}")
print(
    f"MEDIAN: {stock.get_median(stock.historical_market_data['C_to_C_Return'])}")
print(
    f"MODE: {stock.get_mode(stock.historical_market_data['C_to_C_Return'])}")
