from datetime import datetime

import pandas as pd
import pandas_market_calendars as mcal


def get_last_trading_day() -> str:
    today = datetime.utcnow()
    nyse = mcal.get_calendar("NYSE")
    last_trading_day = nyse.valid_days(
        start_date=today - pd.Timedelta(days=365), end_date=today
    )[-1]
    return last_trading_day.strftime("%Y-%m-%d")
