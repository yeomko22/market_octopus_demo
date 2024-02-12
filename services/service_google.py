import base64
import json
from datetime import datetime
from hashlib import md5
from typing import List

import streamlit as st
from google.cloud import storage
from google.cloud import translate
from google.oauth2.service_account import Credentials

encoded_google_secret = st.secrets["GOOGLE_TRANSLATE_SECRET"]
decoded_google_secret = base64.b64decode(encoded_google_secret).decode("utf-8")
google_secret_json = json.loads(decoded_google_secret)

credentials = Credentials.from_service_account_info(google_secret_json)
google_translate_client = translate.TranslationServiceClient(credentials=credentials)
storage_client = storage.Client(credentials=credentials)


def translate(queries: List[str], kor_to_eng: bool = True) -> List[str]:
    if kor_to_eng:
        src_language = "ko"
        tar_language = "en-US"
    else:
        src_language = "en-US"
        tar_language = "ko"
    parent = f"projects/{google_secret_json['project_id']}/locations/global"
    response = google_translate_client.translate_text(
        request={
            "parent": parent,
            "contents": queries,
            "mime_type": "text/plain",
            "source_language_code": src_language,
            "target_language_code": tar_language,
        }
    )
    translations = response.translations
    return [x.translated_text for x in translations]


def paginated_translate(chunks: List[str], metadata:dict, pagesize: int = 5) -> List[str]:
    result = []
    for i in range(0, len(chunks), pagesize):
        queries = chunks[i:i + pagesize]
        queries = [f"title: {metadata['title']}\ncontent: {chunk}" for chunk in queries]
        translated = translate(queries)
        result.extend(translated)
    return result


def upload_html(url: str, html: str) -> str:
    bucket = storage_client.bucket("reference_page")
    datetime_str = datetime.now().strftime("%Y%m%d")
    hashkey = md5(url.encode()).hexdigest()
    destination_path = f"{datetime_str}/reference_page/{hashkey}.html"
    blob = bucket.blob(destination_path)
    blob.upload_from_string(html, content_type="text/html")
    reference_page_url = f"https://storage.googleapis.com/reference_page/{destination_path}"
    return reference_page_url


def upload_news_html(url: str, html: str) -> str:
    bucket = storage_client.bucket("reference_page")
    datetime_str = datetime.now().strftime("%Y%m%d")
    hashkey = md5(url.encode()).hexdigest()
    destination_path = f"{datetime_str}/news/{hashkey}.html"
    blob = bucket.blob(destination_path)
    blob.upload_from_string(html, content_type="text/html")
    reference_page_url = f"https://storage.googleapis.com/reference_page/{destination_path}"
    return reference_page_url
