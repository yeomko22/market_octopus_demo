from enum import Enum


class EnumFnguideCategory(Enum):
    STOCK = "R100"
    INDUSTRY = "R200"
    MARKET = "R300"
    BOND = "R500"
    FX = "R600"
    ECON = "R700"
    CHINA = "H100"


fnguide_category_dict = {
    EnumFnguideCategory.STOCK: "기업",
    EnumFnguideCategory.INDUSTRY: "산업",
    EnumFnguideCategory.MARKET: "주식",
    EnumFnguideCategory.BOND: "채권",
    EnumFnguideCategory.FX: "외환",
    EnumFnguideCategory.ECON: "경제",
    EnumFnguideCategory.CHINA: "중국",
}


class EnumSeekingAlphaCategory(Enum):
    ECONOMY = "Economy"
    FOREX = "Forex"
    INVESTING_STRATEGY = "Investing Strategy"
    LONG_IDEAS = "Long Ideas"
    MARKET_OUTLOOK = "Market Outlook"
    PORTFOLOIO_STRATEGY = "Portfolio Strategy"
    STOCK_IDEAS = "Stock Ideas"
    DIVIDEND_IDEAS = "Dividend Ideas"
    DIVIDEND_STRATEGY = "Dividend Strategy"
    DIVIDENDS = "Dividends"
    ETF_ANALYSIS = "ETF Analysis"
    ETFS_AND_FUNDS = "ETFs and Funds"
    GROWTH = "Growth"
    MICRO_CAP = "Micro-Caps"
    SMALL_CAPS = "Small-Caps"
    VALUE = "Value"
    BONDS = "Bonds"
    FIXED_INCOME = "Fixed Income"
    ENERGY = "Energy"
    BASIC_MATERIALS = "Basic Materials"
    CONSUMER = "Consumer"
    INDUSTRIAL = "Industrial"
    CONSUMER_STAPLE = "Consumer Staple"
    HEALTHCARE = "Healthcare"
    BIOTECH = "Biotech"
    FINANCIALS = "Financials"
    TECH = "Tech"
    COMMUNICATION_SERVICES = "Communication Services"
    UTILITIES = "Utilities"
    REAL_ESTATE = "Real Estate"
    REITS = "Reits"
    COMMODITIES = "Commodities"
    CRYPTOCURRENCY = "Cryptocurrency"
    GOLD_AND_PRECIOUS_METALS = "Gold & Precious Metals"
    CLOSED_END_FUNDS = "Closed End Funds"
    FINANCIAL_ADVISOR = "Financial Advisor"
    IPOS = "IPOs"
    MUTUAL_FUNDS = "M&A"
    RETIREMENT = "Retirement"
