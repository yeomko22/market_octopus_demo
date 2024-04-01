from service_new.openai_service import OpenaiService
from typing import List
import streamlit as st
from datetime import datetime, timedelta
from service_new.pinecone_service import PineconeService
from service_new.yahoo_finance_service import YahooFinanceService


class SearchService:
    def __init__(
        self,
        openai_service: OpenaiService,
        pinecone_service: PineconeService,
        yahoo_finance_service: YahooFinanceService,
    ):
        self.openai_service = openai_service
        self.pinecone_service = pinecone_service
        self.yahoo_finance_service = yahoo_finance_service
        self.instruct_by_screening = {
            "": "",
            "1_1": "The stock has recently seen increased volume and a long white candlestick, which shows that investors are buying in and that the buyers are confident.",
            "1_2": "The stock has recently seen increased volume and a long black candlestick, which shows that investors are joining the sell-off and the confidence of the hawks",
            "2_1": "The stock recently broke above its range, signaling the start of a new uptrend. It's a sign of new investors coming in and psychological resistance being overcome.",
            "2_2": "The stock recently broke below its range, signaling the start of a new downtrend. It signals an outflow of new investors.",
            "3_1": "This stock is showing smash gains. A stock that was falling closes above the previous day's high, suggesting a possible reversal.",
            "3_2": "This stock is showing a smash downtrend. A stock that was rising closes below the previous day's low, suggesting a possible pullback.",
            "4_1": "This stock shows a sideways movement after a pullback. This suggests price stabilization, weakening selling pressure, and a possible trend reversal.",
            "4_2": "This stock shows a recent price increase followed by sideways movement. This suggests that the price is stabilizing, buying interest is weakening, and a trend reversal is possible.",
            "5_1": "The stock is nearing its 3-month support level, which, if held, would signal a bounce in the stock.",
            "5_2": "The stock's price is near its 3-month support level, which is a sign that the stock is headed lower.",
        }

    def get_screening_desc(self, screening: str):
        return self.instruct_by_screening[screening]

    def search_summary(self, ticker: str):
        ticker_name = self.yahoo_finance_service.get_ticker_name(ticker)
        prompt = f"""
Recent news about {ticker_name}.
today: {datetime.now().strftime("%Y-%m-%d")}
        """.strip()
        embedding = self.openai_service.get_embedding([prompt])[0]
        documents = self.pinecone_service.search(
            query_vector=embedding,
            top_k=50,
            include_metadata=False,
            namespace="summary",
            filter={
                "publishedAtTs": {
                    "$gte": (datetime.utcnow() - timedelta(days=7)).timestamp()
                },
            },
        )
        document_ids = [x["id"] for x in documents]
        return document_ids

    def search_content(self, ticker: str, screening: str, document_ids: List[str]):
        ticker_name = self.yahoo_finance_service.get_ticker_name(ticker)
        instruct = self.instruct_by_screening[screening]
        prompt = f"""
The stock price of {ticker_name} ({ticker}) has been fluctuating recently. 
{instruct}
Find the article which contains the most relevant information.
        """.strip()
        embedding = self.openai_service.get_embedding([prompt])[0]
        documents = self.pinecone_service.search(
            query_vector=embedding,
            top_k=20,
            include_metadata=True,
            namespace="content",
            filter={"hashid": {"$in": document_ids}},
        )
        documents = [x["metadata"] for x in documents]
        filtered_documents = []
        visited_hashid = set()
        visited_title = set()
        for document in documents:
            if document["hashid"] in visited_hashid:
                continue
            if document["title"] in visited_title:
                continue
            visited_hashid.add(document["hashid"])
            visited_title.add(document["title"])
            filtered_documents.append(document)
        sorted_documents = sorted(
            filtered_documents, key=lambda x: x["publishedAtTs"], reverse=True
        )
        return sorted_documents[:3]

    def search_related_news(self, ticker: str, screening: str):
        with st.spinner("search news..."):
            document_ids = self.search_summary(ticker)
            documents = self.search_content(ticker, screening, document_ids)
        return documents
