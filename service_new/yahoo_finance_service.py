import pandas as pd
import yfinance


class YahooFinanceService:
    def __init__(self):
        self.ticker_df = pd.read_csv(
            "data/ticker_translation.csv", index_col=["ticker"]
        )
        self.ticker_df = self.ticker_df.iloc[:500]

    def get_ticker_name(self, ticker: str) -> str:
        return self.ticker_df.loc[ticker, "name"]

    def get_ticker_description(self, ticker: str) -> str:
        return self.ticker_df.loc[ticker, "kor_description"]

    def get_stock_price(self, ticker: str) -> pd.DataFrame:
        df = yfinance.download(ticker, period="1y", progress=False)
        return df
