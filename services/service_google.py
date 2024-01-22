import base64
import json
from typing import List

import streamlit as st
from google.cloud import translate
from google.oauth2.service_account import Credentials

encoded_google_secret = st.secrets["GOOGLE_TRANSLATE_SECRET"]
decoded_google_secret = base64.b64decode(encoded_google_secret).decode("utf-8")
google_secret_json = json.loads(decoded_google_secret)

credentials = Credentials.from_service_account_info(google_secret_json)
google_translate_client = translate.TranslationServiceClient(credentials=credentials)


def translate(queries: List[str]) -> List[str]:
    parent = f"projects/{google_secret_json['project_id']}/locations/global"
    response = google_translate_client.translate_text(
        request={
            "parent": parent,
            "contents": queries,
            "mime_type": "text/plain",
            "source_language_code": "ko",
            "target_language_code": "en-US",
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
