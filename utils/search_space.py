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
            EnumFnguideCategory.ECON.value,
        ]
    },
    EnumPrimaryIntent.ECONOMICS: {
        EnumDomain.SEEKING_ALPHA_ANALYSIS: [
            EnumSeekingAlphaCategory.ECONOMY.value,
            EnumSeekingAlphaCategory.FOREX.value,
        ],
        EnumDomain.FNGUIDE: [
            EnumFnguideCategory.ECON.value,
            EnumFnguideCategory.FX.value,
        ]
    },
    EnumPrimaryIntent.STOCK_MARKET_STRATEGY: {
        EnumMarketStrategyIntent.INVESTMENT_STRATEGY: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.MARKET.value
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.INVESTING_STRATEGY.value,
                EnumSeekingAlphaCategory.LONG_IDEAS.value,
                EnumSeekingAlphaCategory.MARKET_OUTLOOK.value,
                EnumSeekingAlphaCategory.PORTFOLOIO_STRATEGY.value,
                EnumSeekingAlphaCategory.STOCK_IDEAS.value,
            ]
        },
        EnumMarketStrategyIntent.DIVIDEND_STOCK: {
            EnumDomain.FNGUIDE: [],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.DIVIDEND_IDEAS.value,
                EnumSeekingAlphaCategory.DIVIDEND_STRATEGY.value,
                EnumSeekingAlphaCategory.DIVIDENDS.value,
            ]
        },
        EnumMarketStrategyIntent.ETF: {
            EnumDomain.FNGUIDE: [],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.ETF_ANALYSIS.value,
                EnumSeekingAlphaCategory.ETFS_AND_FUNDS.value,
            ]
        },
        EnumMarketStrategyIntent.STYLE_FACTOR_ANALYSIS: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.MARKET.value
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.GROWTH.value,
                EnumSeekingAlphaCategory.MICRO_CAP.value,
                EnumSeekingAlphaCategory.SMALL_CAPS.value,
                EnumSeekingAlphaCategory.VALUE.value,
            ]
        },
    },
    EnumPrimaryIntent.BOND_MARKET: {
        EnumDomain.FNGUIDE: [
            EnumFnguideCategory.BOND.value,
        ],
        EnumDomain.SEEKING_ALPHA_ANALYSIS: [
            EnumSeekingAlphaCategory.BONDS.value,
            EnumSeekingAlphaCategory.FIXED_INCOME.value,
        ],
    },
    EnumPrimaryIntent.INDUSTRIES_AND_SECTORS: {
        EnumIndustryStockIntent.OVERALL: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.ENERGY.value,
                EnumSeekingAlphaCategory.BASIC_MATERIALS.value,
                EnumSeekingAlphaCategory.CONSUMER.value,
                EnumSeekingAlphaCategory.CONSUMER_STAPLE.value,
                EnumSeekingAlphaCategory.HEALTHCARE.value,
                EnumSeekingAlphaCategory.BIOTECH.value,
                EnumSeekingAlphaCategory.FINANCIALS.value,
                EnumSeekingAlphaCategory.TECH.value,
                EnumSeekingAlphaCategory.COMMUNICATION_SERVICES.value,
                EnumSeekingAlphaCategory.UTILITIES.value,
                EnumSeekingAlphaCategory.REAL_ESTATE.value,
                EnumSeekingAlphaCategory.REITS.value,
            ]
        },
        EnumIndustryStockIntent.ENERGY: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.ENERGY.value,
            ]
        },
        EnumIndustryStockIntent.MATERIALS: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.BASIC_MATERIALS.value,
            ]
        },
        EnumIndustryStockIntent.CONSUMER: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.CONSUMER.value,
            ]
        },
        EnumIndustryStockIntent.INDUSTRIAL: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.INDUSTRIAL.value,
            ]
        },
        EnumIndustryStockIntent.CONSUMER_STAPLE: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.CONSUMER_STAPLE.value,
            ]
        },
        EnumIndustryStockIntent.FINANCIAL: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.FINANCIALS.value,
            ]
        },
        EnumIndustryStockIntent.IT: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.TECH.value,
            ]
        },
        EnumIndustryStockIntent.COMMUNICATION: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.COMMUNICATION_SERVICES.value,
            ]
        },
        EnumIndustryStockIntent.UTILITIES: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.UTILITIES.value,
            ]
        },
        EnumIndustryStockIntent.REAL_ESTATE: {
            EnumDomain.FNGUIDE: [
                EnumFnguideCategory.INDUSTRY.value,
            ],
            EnumDomain.SEEKING_ALPHA_ANALYSIS: [
                EnumSeekingAlphaCategory.REAL_ESTATE.value,
                EnumSeekingAlphaCategory.REITS.value,
            ]
        },
    },
    EnumPrimaryIntent.ALTERNATIVE_ASSET: {
        EnumDomain.FNGUIDE: [],
        EnumDomain.SEEKING_ALPHA_ANALYSIS: [
            EnumSeekingAlphaCategory.COMMODITIES.value,
            EnumSeekingAlphaCategory.CRYPTOCURRENCY.value,
            EnumSeekingAlphaCategory.GOLD_AND_PRECIOUS_METALS.value,
        ]
    },
    EnumPrimaryIntent.OTHERS: {
        EnumDomain.FNGUIDE: [],
        EnumDomain.SEEKING_ALPHA_ANALYSIS: [
            EnumSeekingAlphaCategory.CLOSED_END_FUNDS.value,
            EnumSeekingAlphaCategory.FINANCIAL_ADVISOR.value,
            EnumSeekingAlphaCategory.IPOS.value,
            EnumSeekingAlphaCategory.MUTUAL_FUNDS.value,
            EnumSeekingAlphaCategory.RETIREMENT.value,
        ]
    },
    EnumPrimaryIntent.CHINA: {
        EnumDomain.FNGUIDE: [
            EnumFnguideCategory.CHINA.value,
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
