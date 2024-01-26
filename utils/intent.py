from enum import Enum


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
