from datetime import datetime

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
