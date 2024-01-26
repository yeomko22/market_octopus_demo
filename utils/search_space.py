from enum import Enum
from typing import Optional, Union, List

from utils.categories import EnumSeekingAlphaCategory, EnumFnguideCategory
from utils.intent import EnumPrimaryIntent, EnumIndustryStockIntent, EnumMarketStrategyIntent


class EnumDomain(Enum):
    SEEKING_ALPHA_ANALYSIS = "seeking-alpha-analysis"
    FNGUIDE = "fnguide"


SEARCH_SPACE_BY_INTENT = {
    EnumPrimaryIntent.POLICY: {
        EnumDomain.SEEKING_ALPHA_ANALYSIS: [],
        EnumDomain.FNGUIDE: [
            EnumFnguideCategory.ECON,
        ]
    },
    EnumPrimaryIntent.ECONOMICS: {
        EnumDomain.SEEKING_ALPHA_ANALYSIS: [
            EnumSeekingAlphaCategory.ECONOMY,
            EnumSeekingAlphaCategory.FOREX,
        ],
        EnumDomain.FNGUIDE: [
            EnumFnguideCategory.ECON,
            EnumFnguideCategory.FX,
        ]
    },
    EnumPrimaryIntent.STOCK_MARKET_STRATEGY: {
        EnumMarketStrategyIntent.INVESTMENT_STRATEGY: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.MARKET
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.INVESTING_STRATEGY,
                EnumSeekingAlphaCategory.LONG_IDEAS,
                EnumSeekingAlphaCategory.MARKET_OUTLOOK,
                EnumSeekingAlphaCategory.PORTFOLOIO_STRATEGY,
                EnumSeekingAlphaCategory.STOCK_IDEAS,
            ]
        },
        EnumMarketStrategyIntent.DIVIDEND_STOCK: {
            EnumDomain.FNGUIDE: [],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.DIVIDEND_IDEAS,
                EnumSeekingAlphaCategory.DIVIDEND_STRATEGY,
                EnumSeekingAlphaCategory.DIVIDENDS,
            ]
        },
        EnumMarketStrategyIntent.ETF: {
            EnumDomain.FNGUIDE: [],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.ETF_ANALYSIS,
                EnumSeekingAlphaCategory.ETFS_AND_FUNDS,
            ]
        },
        EnumMarketStrategyIntent.STYLE_FACTOR_ANALYSIS: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.MARKET
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.GROWTH,
                EnumSeekingAlphaCategory.MICRO_CAP,
                EnumSeekingAlphaCategory.SMALL_CAPS,
                EnumSeekingAlphaCategory.VALUE,
            ]
        },
    },
    EnumPrimaryIntent.BOND_MARKET: {
        EnumDomain.FNGUIDE: [
            EnumFnguideCategory.BOND,
        ],
        EnumDomain.SEEKING_ALPHA_ANALYSIS: [
            EnumSeekingAlphaCategory.BONDS,
            EnumSeekingAlphaCategory.FIXED_INCOME,
        ],
    },
    EnumPrimaryIntent.INDUSTRIES_AND_SECTORS: {
        EnumIndustryStockIntent.ENERGY: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.ENERGY,
            ]
        },
        EnumIndustryStockIntent.MATERIALS: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.BASIC_MATERIALS,
            ]
        },
        EnumIndustryStockIntent.CONSUMER: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.CONSUMER,
            ]
        },
        EnumIndustryStockIntent.INDUSTRIAL: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.INDUSTRIAL,
            ]
        },
        EnumIndustryStockIntent.FINANCIAL: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.FINANCIALS,
            ]
        },
        EnumIndustryStockIntent.IT: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.TECH,
            ]
        },
        EnumIndustryStockIntent.COMMUNICATION: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.COMMUNICATION_SERVICES,
            ]
        },
        EnumIndustryStockIntent.UTILITIES: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.UTILITIES,
            ]
        },
        EnumIndustryStockIntent.REAL_ESTATE: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.REAL_ESTATE,
                EnumSeekingAlphaCategory.REITS,
            ]
        },
    },
    EnumPrimaryIntent.ALTERNATIVE_ASSET: {
        EnumDomain.FNGUIDE: [],
        EnumDomain.SEEKING_ALPHA_ANALYSIS: [
            EnumSeekingAlphaCategory.COMMODITIES,
            EnumSeekingAlphaCategory.CRYPTOCURRENCY,
            EnumSeekingAlphaCategory.GOLD_AND_PRECIOUS_METALS,
        ]
    },
    EnumPrimaryIntent.OTHERS: {
        EnumDomain.FNGUIDE: [ ],
        EnumDomain.SEEKING_ALPHA_ANALYSIS: [
            EnumSeekingAlphaCategory.CLOSED_END_FUNDS,
            EnumSeekingAlphaCategory.FINANCIAL_ADVISOR,
            EnumSeekingAlphaCategory.IPOS,
            EnumSeekingAlphaCategory.MUTUAL_FUNDS,
            EnumSeekingAlphaCategory.RETIREMENT,
        ]
    },
    EnumPrimaryIntent.CHINA: {
        EnumDomain.FNGUIDE: [
            EnumFnguideCategory.CHINA,
        ],
        EnumDomain.SEEKING_ALPHA_ANALYSIS: []
    }
}


def get_search_space(
        primary_intent: EnumPrimaryIntent,
        secondary_intent: Optional[Union[EnumMarketStrategyIntent, EnumIndustryStockIntent]],
        domain: EnumDomain
) -> List[str]:
    if primary_intent == EnumPrimaryIntent.STOCK_MARKET_STRATEGY \
        or primary_intent == EnumPrimaryIntent.INDUSTRIES_AND_SECTORS:
        return SEARCH_SPACE_BY_INTENT[primary_intent][secondary_intent][domain]
    else:
        return SEARCH_SPACE_BY_INTENT[primary_intent][domain]
