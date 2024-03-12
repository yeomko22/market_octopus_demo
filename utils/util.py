from datetime import datetime
from hashlib import md5
import csv
from typing import Dict, Tuple

import pytz


def get_date_diff(published_at: datetime) -> str:
    date_diff = (datetime.now() - published_at).days
    if date_diff == 0:
        return "오늘"
    elif date_diff < 7:
        return f"{date_diff}일 전"
    elif date_diff < 14:
        return "1주 전"
    elif date_diff < 21:
        return "2주 전"
    elif date_diff < 28:
        return "3주 전"
    elif date_diff < 35:
        return "4주 전"
    elif date_diff < 42:
        return "한달 전"
    else:
        return published_at.strftime("%Y-%m-%d")


def convert_timezone(created_at: datetime) -> datetime:
    return created_at.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Asia/Seoul"))


def load_tickers() -> Tuple[Dict[str, str], Dict[str, str]]:
    ticker_dict = {}
    ticker_desc_dict = {}
    with open("data/tickers.csv") as fr:
        reader = csv.reader(fr)
        next(reader)
        for i, (ticker, name, description) in enumerate(reader):
            if i > 200:
                break
            ticker_dict[ticker] = name
            ticker_desc_dict[ticker] = description
    return ticker_dict, ticker_desc_dict


def hash_string(s: str) -> str:
    return md5(s.encode()).hexdigest()


def base64_encode(s: str) -> str:
    return s.encode("utf-8").hex()


def base64_decode(s: str) -> str:
    return bytes.fromhex(s).decode("utf-8")
