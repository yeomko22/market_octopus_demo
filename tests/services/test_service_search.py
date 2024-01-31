import json
from typing import List

import pytest

from services.service_search import (get_news_items, parse_article_einfomax, parse_related_paragraph,
                                     parse_article_hankyung, parse_article_mk, parse_article_bp, parse_article_yf)


@pytest.fixture(scope="session")
def kor_query() -> str:
    query = "최근 미국의 금리 인하가 2024년 주식 시장에 미치는 영향"
    return query


@pytest.fixture(scope="session")
def eng_query() -> str:
    eng_query = "impact of U.S. interest rate cut on stock market 2024"
    return eng_query


@pytest.fixture(scope="session")
def kor_query_embedding() -> List[float]:
    with open("tests/services/data/kor_query_embedding.json") as fr:
        query_embedding = json.loads(fr.read())
        return query_embedding


@pytest.fixture(scope="session")
def eng_query_embedding() -> List[float]:
    with open("tests/services/data/eng_query_embedding.json") as fr:
        query_embedding = json.loads(fr.read())
        return query_embedding


@pytest.fixture(scope="session")
def article_einfomax_html() -> str:
    with open("tests/services/data/article_einfomax.html") as fr:
        html = fr.read()
        return html


@pytest.fixture(scope="session")
def article_hankyung_html() -> str:
    with open("tests/services/data/article_hankyung.html") as fr:
        html = fr.read()
        return html


@pytest.fixture(scope="session")
def article_mk_html() -> str:
    with open("tests/services/data/article_mk.html") as fr:
        html = fr.read()
        return html


@pytest.fixture(scope="session")
def article_yf_html() -> str:
    with open("tests/services/data/article_yf.html") as fr:
        html = fr.read()
        return html


@pytest.fixture(scope="session")
def article_bp_html() -> str:
    with open("tests/services/data/article_bp.html") as fr:
        html = fr.read()
        return html


def test_search_news(kor_query: str):
    result = get_news_items(kor_query, target="국내")
    assert 0 < len(result) <= 5


def test_parse_einfomax(article_einfomax_html: str):
    article_content = parse_article_einfomax(article_einfomax_html)
    assert article_content is not None
    assert len(article_content) > 100


def test_parse_hankyung(article_hankyung_html: str):
    article_content = parse_article_hankyung(article_hankyung_html)
    assert article_content is not None
    assert len(article_content) > 100


def test_parse_mk(article_mk_html: str):
    article_content = parse_article_mk(article_mk_html)
    assert article_content is not None
    assert len(article_content) > 100


def test_parse_bp(article_bp_html: str):
    article_content = parse_article_bp(article_bp_html)
    assert article_content is not None
    assert len(article_content) > 100


def test_parse_yf(article_yf_html: str):
    article_content = parse_article_yf(article_yf_html)
    assert article_content is not None
    assert len(article_content) > 100


def test_tmp():
    import requests
    url = "https://finance.yahoo.com/news/aktia-bank-plc-incentive-plans-160000034.html"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    with open("tests/services/data/article_yf.html", "w") as fw:
        fw.write(response.text)


def test_parse_related_paragraph(kor_query_embedding: List[float], article_einfomax_html: str):
    article_content = parse_article_einfomax(article_einfomax_html)
    paragraph = parse_related_paragraph(kor_query_embedding, article_content)
    assert paragraph is not None
    assert len(paragraph) > 100
