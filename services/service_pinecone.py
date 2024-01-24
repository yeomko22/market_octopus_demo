import os
from typing import List, Optional


from pinecone import Pinecone
from services.util import EnumIntent, EnumCategory

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
# fnguide_index = pc.Index('financial-analyst')
seeking_alpha_index = pc.Index('market-octopus')
search_space_by_intent = {
    EnumIntent.ECONOMIC_INDICATOR: [
        EnumCategory.ECON.value,
    ],
    EnumIntent.POLICY_AND_REGULATION: [
        EnumCategory.INDUSTRY.value,
        EnumCategory.MARKET.value,
    ],
    EnumIntent.MARKET_TREND: [
        EnumCategory.MARKET.value,
    ],
    EnumIntent.MARKET_PREDICTION: [
        EnumCategory.ECON.value,
        EnumCategory.MARKET.value,
    ],
    EnumIntent.INVESTMENT_STRATEGY: [
        EnumCategory.ECON.value,
        EnumCategory.MARKET.value,
    ],
    EnumIntent.NEW_TECHNOLOGY: [
        EnumCategory.MARKET.value,
        EnumCategory.INDUSTRY.value,
        EnumCategory.STOCK.value,
    ],
    EnumIntent.INDUSTRY_ANALYSIS: [
        EnumCategory.MARKET.value,
        EnumCategory.INDUSTRY.value,
    ],
    EnumIntent.STOCK_RECOMMENDATION: [
        EnumCategory.MARKET.value,
        EnumCategory.STOCK.value,
    ],
    EnumIntent.STOCK_DIRECTION_PREDICTION: [
        EnumCategory.ECON.value,
        EnumCategory.MARKET.value,
        EnumCategory.INDUSTRY.value,
        EnumCategory.STOCK.value,
    ],
}


def filter_duplicates(matches: List[dict]) -> List[dict]:
    filtered_matches = []
    hashkey_set = set()
    for match in matches:
        hashkey = match["hashkey"]
        if hashkey not in hashkey_set:
            hashkey_set.add(hashkey)
            filtered_matches.append(match)
    return filtered_matches[:3]


# def search_fnguide(intent: EnumIntent, query_embedding: List[float]) -> List[dict]:
#     results = fnguide_index.query(
#         vector=query_embedding,
#         top_k=10,
#         include_metadata=True,
#         namespace="financial_report",
#         filter={"category": {"$in": search_space_by_intent[intent]}}
#     )
#     matches = [x["metadata"] for x in results["matches"]]
#     matches = filter_duplicates(matches)
#     return matches


def search_seeking_alpha_summary(query_embedding: List[float], k: int = 3) -> List[dict]:
    result = seeking_alpha_index.query(
        vector=query_embedding,
        top_k=k,
        namespace="seeking-alpha-analysis-summary",
        include_metadata=True,
    )
    matches = result["matches"]
    return [x for x in matches if x["score"] >= 0.8]


def search_seeking_alpha_content(query_embedding: List[float], id_list: List[str], k: int = 3) -> Optional[List[dict]]:
    result = seeking_alpha_index.query(
        vector=query_embedding,
        top_k=10,
        namespace="seeking-alpha-analysis-content",
        include_metadata=True,
        filter={"id": {"$in": id_list}}
    )
    matches = result["matches"]
    if not matches:
        return None

    # filter duplicates
    visited = set()
    filtered_result = []
    for match in matches:
        if match["metadata"]["id"] in visited:
            continue
        filtered_result.append(match)
        visited.add(match["metadata"]["id"])
    return filtered_result[:k]
