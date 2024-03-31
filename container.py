import streamlit as st
from dependency_injector import containers
from dependency_injector.providers import Singleton

from service_new.openai_service import OpenaiService
from service_new.pinecone_service import PineconeService
from service_new.yahoo_finance_service import YahooFinanceService
from service_new.search_service import SearchService


class Container(containers.DeclarativeContainer):
    openai_service = Singleton(
        OpenaiService, openai_api_key=st.secrets["OPENAI_API_KEY"]
    )
    yahoo_finance_service = Singleton(YahooFinanceService)
    pinecone_service = Singleton(
        PineconeService, pinecone_api_key=st.secrets["PINECONE_API_KEY"]
    )
    search_service = Singleton(
        SearchService,
        openai_service=openai_service,
        pinecone_service=pinecone_service,
        yahoo_finance_service=yahoo_finance_service,
    )
