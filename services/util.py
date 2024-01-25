import json
import re
from datetime import datetime
from enum import Enum


class EnumReferenceType(Enum):
    DOMESTIC_REPORT = "한국 애널리스트 리포트"
    OVERSEAS_REPORT = "미국 애널리스트 리포트"


class EnumPrimaryIntent(Enum):
    POLICY = "정책"
    ECONOMY = "경제"
    MARKET_STRATEGY = "주식시장 전략"
    BOND = "채권시장"
    INDUSTRY_STOCK = "산업 및 종목"
    ALTERNATIVE_ASSET = "대체자산"
    ETC = "기타"

class EnumCategory(Enum):
    STOCK = "R100"
    INDUSTRY = "R200"
    MARKET = "R300"
    BOND = "R500"
    FX = "R600"
    ECON = "R700"
    CHINA = "H100"


category_dict = {
    EnumCategory.ECON.value: "경제",
    EnumCategory.MARKET.value: "주식",
    EnumCategory.BOND.value: "채권",
    EnumCategory.INDUSTRY.value: "산업",
    EnumCategory.STOCK.value: "기업",
    EnumCategory.CHINA.value: "중국",
    EnumCategory.FX.value: "외환",
}


def parse_first_json(input_string: str) -> dict:
    # 정규 표현식을 사용하여 중괄호로 둘러싸인 모든 내용을 찾음
    matches = re.findall(r'\{.*?\}', input_string)
    if not matches:
        return {}
    # 첫 번째 JSON 객체를 파싱하려고 시도
    try:
        return json.loads(matches[0])
    except json.JSONDecodeError:
        # JSON 파싱 에러 발생시 None 반환
        return {}


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
