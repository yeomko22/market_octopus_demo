import concurrent.futures
from collections import Counter

from dateutil import parser
import numpy as np
from urllib.parse import quote
from pytz import timezone
from dateutil import parser
from datetime import datetime, timedelta
from typing import List, Tuple, Iterator
import requests
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.service_openai import get_embedding
from bs4 import BeautifulSoup
import os
import re

google_search_url_template = ("https://www.googleapis.com/customsearch/v1"
                              "?key={API_KEY}&cx={CSE_KEY}&q={QUERY}"
                              "&num=10&sort=date:r:{start}:{end}")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
    keep_separator=True,
)


def remove_urls(text):
    url_pattern = r'https?://\S+|www\.\S+'
    clean_text = re.sub(url_pattern, '', text)
    return clean_text


def _request_search_api(query: str, target: str) -> dict:
    if target == "국내":
        cse_key = st.secrets["GOOGLE_CSE_DOMESTIC"]
    elif target == "해외":
        cse_key = st.secrets["GOOGLE_CSE_OVERSEA"]
    else:
        cse_key = st.secrets["GOOGLE_CSE_BOTH"]

    today = datetime.now(tz=timezone("Asia/Seoul"))
    start = (today - timedelta(days=3)).strftime("%Y%m%d")
    end = today.strftime("%Y%m%d")
    url = google_search_url_template.format(
        API_KEY=st.secrets["GOOGLE_API_KEY"],
        CSE_KEY=cse_key,
        QUERY=quote(query),
        start=start,
        end=end
    )
    print(url)
    response = requests.get(url)
    return response.json()


def get_news_items(query: str, target: str) -> List[dict]:
    news_items = []
    response_json = _request_search_api(query, target)
    total_results = response_json["searchInformation"]["totalResults"]
    if not total_results:
        return news_items
    if total_results == "0":
        if "spelling" not in response_json:
            return news_items
        query = response_json["spelling"]["correctedQuery"]
        response_json = _request_search_api(query, target)
    news_items = response_json.get("items", [])
    if not news_items:
        return news_items

    # 같은 언론사의 기사는 최대 3개까지만 선택
    publisher_count = Counter()
    result = []
    for news_item in news_items:
        publisher = get_publisher(news_item["link"])
        if publisher_count[publisher] >= 3:
            continue
        publisher_count[publisher] += 1
        result.append({
            "title": news_item["title"],
            "publisher": get_publisher(news_item["link"]),
            "published_at": parser.parse(news_item["pagemap"]["metatags"][0]["article:published_time"]),
            "url": news_item["link"]
        })
    return result


def get_publisher(url: str) -> str:
    publisher = ""
    if url.startswith("https://news.einfomax.co.kr"):
        publisher = "연합 인포맥스"
    elif url.startswith("https://www.hankyung.com"):
        publisher = "한국경제"
    elif url.startswith("https://www.mk.co.kr"):
        publisher = "매일경제"
    elif url.startswith("https://www.businesspost.co.kr"):
        publisher = "비즈니스 포스트"
    elif url.startswith("https://finance.yahoo.com/"):
        publisher = "yahoo finance"
    return publisher


def search_news(query: str, query_embedding: List[float], target: str) -> List[dict]:
    news_items = get_news_items(query, target)
    info_list = [(news_item, query_embedding) for news_item in news_items]
    news_items = parallel_request_parse_articles(info_list)
    news_items = [x for x in news_items if x["similarity"] > 0.45]
    news_items = sorted(news_items, key=lambda x: x["similarity"], reverse=True)
    return news_items[:3]


def parse_article_einfomax(article_html: str) -> str:
    soup = BeautifulSoup(article_html, "lxml")
    article_content = soup.find("article", id="article-view-content-div").text
    article_content = remove_urls(article_content)
    return article_content.strip()


def parse_article_hankyung(article_html: str) -> str:
    soup = BeautifulSoup(article_html, "lxml")
    article_content = soup.find("div", id="articletxt").text
    article_content = remove_urls(article_content)
    return article_content.strip()


def parse_article_mk(article_html: str) -> str:
    soup = BeautifulSoup(article_html, "lxml")
    article_content = soup.find("div", attrs={"itemprop": "articleBody"}).text
    article_content = remove_urls(article_content)
    return article_content.strip()


def parse_article_bp(article_html: str) -> str:
    soup = BeautifulSoup(article_html, "lxml")
    article_soup = soup.find("div", class_="detail_editor")
    if article_soup is None:
        return ""
    article_content = article_soup.text
    article_content = remove_urls(article_content)
    return article_content.strip()


def parse_article_yf(article_html: str) -> str:
    soup = BeautifulSoup(article_html, "lxml")
    article_soup = soup.find("div", class_="caas-body")
    article_content = article_soup.text
    article_content = remove_urls(article_content)
    return article_content.strip()


def parse_article(url: str, article_html: str) -> str:
    if url.startswith("https://news.einfomax.co.kr"):
        return parse_article_einfomax(article_html)
    elif url.startswith("https://www.hankyung.com"):
        return parse_article_hankyung(article_html)
    elif url.startswith("https://www.mk.co.kr/"):
        return parse_article_mk(article_html)
    elif url.startswith("https://www.businesspost.co.kr/"):
        return parse_article_bp(article_html)
    elif url.startswith("https://finance.yahoo.com"):
        return parse_article_yf(article_html)


def parse_related_paragraph(query_embedding: List[float], article: str) -> Tuple[float, str]:
    query_embedding = np.array(query_embedding)
    text_chunks = text_splitter.split_text(article)
    embeddings = get_embedding(text_chunks)
    similarity_list = []
    for i, (embedding, text_chunk) in enumerate(zip(embeddings, text_chunks)):
        similarity = query_embedding.dot(embedding)
        similarity_list.append((similarity, text_chunk))
    return sorted(similarity_list, key=lambda x: x[0], reverse=True)[0]


def request_parse_article(info: Tuple[dict, List[float]]) -> dict:
    news_item, query_embedding = info
    response = requests.get(
        url=news_item["url"],
        headers={
            'User-Agent': 'Mozilla/5.0',
        }
    )
    article_html = response.text
    article_content = parse_article(news_item["url"], article_html)
    if not article_content:
        return 0, ""
    similarity, related_paragraph = parse_related_paragraph(query_embedding, article_content)
    news_item["similarity"] = similarity
    news_item["related_paragraph"] = related_paragraph
    return news_item


def parallel_request_parse_articles(info_list: List[Tuple[dict, List[float]]]) -> Iterator[dict]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        news_items = executor.map(request_parse_article, info_list)
    return news_items
