import functions_framework
from dotenv import load_dotenv

load_dotenv(".env.yaml")

from service_openai import get_embedding
from service_search import search_news
from typing import List, Tuple
from service_html import get_reference_page_html
from service_google import upload_html
from copy import deepcopy
import concurrent.futures


def parallel_search_news(request_info: Tuple[str, List[float], str]) -> List[dict]:
    query, query_embedding, target = request_info
    news_items = search_news(query, query_embedding, target)
    return news_items


def search_related_news(
        kor_question: str,
        eng_question: str,
        kor_queries: List[str],
        eng_queries: List[str],
        question_range: str
):
    related_news = []
    kor_question_embedding, eng_question_embedding = get_embedding([kor_question, eng_question])
    for kor_query, eng_query in zip(kor_queries, eng_queries):
        request_info = []
        if question_range == "국내" or question_range == "전체":
            request_info.append((kor_query, kor_question_embedding, "domestic"))
        if question_range == "해외" or question_range == "전체":
            request_info.append((eng_query, eng_question_embedding, "yf"))
            request_info.append((eng_query, eng_question_embedding, "investing"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_news_result = executor.map(parallel_search_news, request_info)
        if search_news_result:
            for news_list in search_news_result:
                related_news.extend(news_list)
        if related_news:
            break
    related_news = sorted(related_news, key=lambda x: x["similarity"], reverse=True)[:3]
    return related_news


def upload_related_news(related_news_list: List[dict]) -> List[dict]:
    updated_news_list = []
    for related_news in related_news_list:
        updated_news = deepcopy(related_news)
        reference_page_html = get_reference_page_html(
            origin_url=related_news["uploaded_news_url"],
            reference_url=related_news["url"],
            related_paragraph=related_news["related_paragraph"]
        )
        reference_page_url = upload_html(related_news["uploaded_news_url"], reference_page_html)
        updated_news["reference_page_url"] = reference_page_url
        updated_news_list.append(updated_news)
    return updated_news_list


@functions_framework.http
def run(request):
    kor_question = request.json["kor_question"]
    eng_question = request.json["eng_question"]
    kor_queries = request.json["kor_queries"]
    eng_queries = request.json["eng_queries"]
    question_range = request.json["question_range"]
    related_news = search_related_news(
        kor_question=kor_question,
        eng_question=eng_question,
        kor_queries=kor_queries,
        eng_queries=eng_queries,
        question_range=question_range
    )
    if related_news:
        related_news = upload_related_news(related_news)
    return related_news
