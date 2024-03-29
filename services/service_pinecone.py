import os
from typing import List, Optional

from pinecone import Pinecone

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("market-octopus-v2")


def filter_duplicates(matches: List[dict]) -> List[dict]:
    filtered_matches = []
    hashkey_set = set()
    for match in matches:
        hashkey = match["hashkey"]
        if hashkey not in hashkey_set:
            hashkey_set.add(hashkey)
            filtered_matches.append(match)
    return filtered_matches[:3]


def search_seeking_alpha_summary(
    query_embedding: List[float], top_k: int = 5
) -> List[dict]:
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace="seeking-alpha-analysis-summary",
        include_metadata=True,
    )
    matches = result["matches"]
    return [x for x in matches if x["score"] if x["score"] > 0.5]


def search_investment_bank(query_embedding: List[float], top_k: int = 5) -> List[dict]:
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace="investment_bank_v2",
        include_metadata=True,
    )
    matches = result["matches"]
    return [x for x in matches if x["score"] if x["score"]]


def search_seeking_alpha_content(
    query_embedding: List[float], id_list: List[str], top_k: int = 3
) -> Optional[List[dict]]:
    result = index.query(
        vector=query_embedding,
        top_k=10,
        namespace="seeking-alpha-analysis-content",
        include_metadata=True,
        filter={"id": {"$in": id_list}},
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
    return [x for x in filtered_result if x["score"] > 0.5]


def search_fnguide(
    query_embedding: List[float], top_k: int = 3
) -> Optional[List[dict]]:
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
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
    return [x for x in filtered_result if x["score"] > 0.5]


def search_related_reports(question_embedding: List[float]) -> List[dict]:
    oversea_report_list = []
    seeking_alpha_summary_list = search_seeking_alpha_summary(
        question_embedding, top_k=5
    )
    if seeking_alpha_summary_list:
        oversea_report_ids = [x["metadata"]["id"] for x in seeking_alpha_summary_list]
        seeking_alpha_content_list = search_seeking_alpha_content(
            question_embedding, oversea_report_ids, top_k=3
        )
        oversea_report_list.extend(seeking_alpha_content_list)
    investment_bank_list = search_investment_bank(question_embedding, top_k=3)
    oversea_report_list.extend(investment_bank_list)
    oversea_report_list = sorted(
        oversea_report_list, key=lambda x: x["score"], reverse=True
    )[:3]
    return oversea_report_list
