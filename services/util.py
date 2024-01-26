import json
import re
from datetime import datetime
from enum import Enum


class EnumReferenceType(Enum):
    DOMESTIC_REPORT = "한국 애널리스트 리포트"
    OVERSEAS_REPORT = "미국 애널리스트 리포트"


class EnumPrimaryIntent(Enum):
    POLICY = "Policy"
    ECONOMICS = "Economics"
    STOCK_MARKET_STRATEGY = "Stock market strategy"
    BOND_MARKET = "Bond market"
    INDUSTRIES_AND_SECTORS = "Industries and sectors"
    ALTERNATIVE_ASSET = "Alternative assets"
    CHINA = "China"
    OTHERS = "Others"


PRIMARY_INTENT_DICT = {
    EnumPrimaryIntent.POLICY: "정책",
    EnumPrimaryIntent.ECONOMICS: "경제",
    EnumPrimaryIntent.STOCK_MARKET_STRATEGY: "주식시장 전략",
    EnumPrimaryIntent.BOND_MARKET: "채권시장",
    EnumPrimaryIntent.INDUSTRIES_AND_SECTORS: "산업 및 종목",
    EnumPrimaryIntent.ALTERNATIVE_ASSET: "대체자산",
    EnumPrimaryIntent.CHINA: "중국",
    EnumPrimaryIntent.OTHERS: "기타",
}


class EnumMarketStrategyIntent(Enum):
    INVESTMENT_STRATEGY = "Ivestment strategy"
    DIVIDEND_STOCK = "Dividend stock"
    ETF = "ETF"
    STYLE_FACTOR_ANALYSIS = "Style factor analysis"


ENUM_MARKET_STRATEGY_INTENT_DICT = {
    EnumMarketStrategyIntent.INVESTMENT_STRATEGY: "투자 전략",
    EnumMarketStrategyIntent.DIVIDEND_STOCK: "배당주",
    EnumMarketStrategyIntent.ETF: "ETF",
    EnumMarketStrategyIntent.STYLE_FACTOR_ANALYSIS: "스타일 팩터 분석",
}


class EnumIndustryStockIntent(Enum):
    OVERALL = "Overall"
    ENERGY = "Energy"
    MATERIALS = "Materials"
    CONSUMER = "Consumer"
    INDUSTRIAL = "Industrial"
    FINANCIAL = "Financial"
    IT = "IT"
    COMMUNICATION = "Commnication"
    UTILITIES = "Utilities"
    REAL_ESTATE = "Real Estate"


ENUM_INDUSTRY_STOCK_INTENT_DICT = {
    EnumIndustryStockIntent.OVERALL: "전체",
    EnumIndustryStockIntent.ENERGY: "에너지",
    EnumIndustryStockIntent.MATERIALS: "소재",
    EnumIndustryStockIntent.CONSUMER: "소비재",
    EnumIndustryStockIntent.INDUSTRIAL: "산업재",
    EnumIndustryStockIntent.FINANCIAL: "금융",
    EnumIndustryStockIntent.IT: "IT",
    EnumIndustryStockIntent.COMMUNICATION: "통신",
    EnumIndustryStockIntent.UTILITIES: "유틸리티",
    EnumIndustryStockIntent.REAL_ESTATE: "부동산",
}


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
