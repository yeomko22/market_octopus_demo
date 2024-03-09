import base64
from copy import deepcopy
from typing import List
import json
import os
from datetime import datetime
from hashlib import md5

from google.cloud import storage
from google.oauth2.service_account import Credentials
from service_html import get_reference_page_html

encoded_google_secret = os.environ.get("GOOGLE_SECRET", "")
decoded_google_secret = base64.b64decode(encoded_google_secret).decode("utf-8")
google_secret_json = json.loads(decoded_google_secret)

credentials = Credentials.from_service_account_info(google_secret_json)
storage_client = storage.Client(credentials=credentials)


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



