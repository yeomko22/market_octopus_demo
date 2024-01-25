import os
from typing import List, Optional

from pinecone import Pinecone

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
seeking_alpha_index = pc.Index('market-octopus')


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


def search_fnguide(query_embedding: List[float], k: int = 3) -> Optional[List[dict]]:
    result = seeking_alpha_index.query(
        vector=query_embedding,
        top_k=10,
        namespace="fnguide",
        include_metadata=True,
    )
    matches = result["matches"]
    if not matches:
        return None

    # filter duplicates
    visited = set()
    filtered_result = []
    for match in matches:
        if match["metadata"]["hashkey"] in visited:
            continue
        filtered_result.append(match)
        visited.add(match["metadata"]["hashkey"])
    return filtered_result[:k]
