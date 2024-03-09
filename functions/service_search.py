import concurrent.futures
import os
import subprocess
import re
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from urllib.parse import quote

import numpy as np
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pytz import timezone

from service_google import upload_news_html
from service_openai import get_embedding

google_search_url_template = ("https://www.googleapis.com/customsearch/v1"
                              "?key={API_KEY}&cx={CSE_KEY}&q={QUERY}"
                              "&num=5&sort=date:r:{start}:{end}")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
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
    if target == "domestic":
        cse_key = os.environ.get("GOOGLE_CSE_DOMESTIC")
    elif target == "yf":
        cse_key = os.environ.get("GOOGLE_CSE_YF")
    elif target == "investing":
        cse_key = os.environ.get("GOOGLE_CSE_INVESTING")
    else:
        raise ValueError("Invalid target")
    today = datetime.now(tz=timezone("Asia/Seoul"))
    start = (today - timedelta(days=7)).strftime("%Y%m%d")
    end = today.strftime("%Y%m%d")
    url = google_search_url_template.format(
        API_KEY=os.environ.get("GOOGLE_API_KEY"),
        CSE_KEY=cse_key,
        QUERY=quote(query),
        start=start,
        end=end
    )
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

    result = []
    for news_item in news_items:
        parsed_news = {
            "title": news_item["title"],
            "publisher": get_publisher(news_item["link"]),
            "url": news_item["link"]
        }
        metatags = news_item["pagemap"]["metatags"][0]
        if "article:published_time" in metatags:
            parsed_news["published_at"] = parser.parse(metatags["article:published_time"])
        result.append(parsed_news)
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
    elif url.startswith("https://www.investing.com/"):
        publisher = "investing.com"
    elif url.startswith("https://www.bloomberg.com/"):
        publisher = "bloomberg"
    return publisher


def search_news(query: str, query_embedding: List[float], target: str) -> List[dict]:
    news_items = get_news_items(query, target)
    info_list = [(news_item, query_embedding) for news_item in news_items]
    news_items = parallel_request_parse_articles(info_list)
    news_items = [x for x in news_items if x["similarity"] > 0.35]
    return news_items


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


def parse_article_cbiz(article_html: str) -> str:
    soup = BeautifulSoup(article_html, "lxml")
    article_soup = soup.find("script", id="fusion-metadata")
    if article_soup is None:
        return ""
    article_content = article_soup.text
    article_content = remove_urls(article_content)
    return article_content.strip()


def parse_article_yf(article_html: str) -> str:
    soup = BeautifulSoup(article_html, "lxml")
    article_soup = soup.find("div", class_="caas-body")
    if article_soup is None:
        return ""
    article_content = article_soup.text
    article_content = remove_urls(article_content)
    return article_content.strip()


def parse_article_investing(article_html: str) -> str:
    soup = BeautifulSoup(article_html, "lxml")
    article_soup = soup.find("div", class_="WYSIWYG")
    if article_soup is None:
        return ""
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
    elif url.startswith("https://www.investing.com/"):
        return parse_article_investing(article_html)


def parse_related_paragraph(query_embedding: List[float], article: str) -> Tuple[int, float, str]:
    query_embedding = np.array(query_embedding)
    text_chunks = text_splitter.split_text(article)
    embeddings = get_embedding(text_chunks)
    similarity_list = []
    for i, (embedding, text_chunk) in enumerate(zip(embeddings, text_chunks)):
        similarity = query_embedding.dot(embedding)
        similarity_list.append((i, similarity, text_chunk))
    return sorted(similarity_list, key=lambda x: x[0], reverse=True)[0]


def crawl_with_curl(url: str) -> str:
    curl_cmd = ["curl",
                "-L",
                "-w", " - status code: %{http_code}, sizes: %{size_request}/%{size_download}",
                url,
                "-H", "user-agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"]
    result = subprocess.run(curl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    article_html = result.stdout
    return article_html


def crawl_with_requests(url: str) -> str:
    response = requests.get(
        url=url,
        headers={
            'User-Agent': 'Mozilla/5.0',
        }
    )
    article_html = response.text
    return article_html


def request_parse_article(info: Tuple[dict, List[float]]) -> Optional[dict]:
    news_item, query_embedding = info
    url = news_item["url"]
    if url.startswith("https://www.investing.com"):
        article_html = crawl_with_curl(url)
    else:
        article_html = crawl_with_requests(url)
    uploaded_news_url = upload_news_html(url, article_html)
    article_content = parse_article(url, article_html)
    if not article_content:
        return None
    idx, similarity, related_paragraph = parse_related_paragraph(query_embedding, article_content)
    news_item["index"] = idx
    news_item["similarity"] = similarity
    news_item["related_paragraph"] = related_paragraph
    news_item["uploaded_news_url"] = uploaded_news_url
    return news_item


def parallel_request_parse_articles(info_list: List[Tuple[dict, List[float]]]) -> List[dict]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        news_items = executor.map(request_parse_article, info_list)
    news_items = [x for x in news_items if x]
    return news_items
