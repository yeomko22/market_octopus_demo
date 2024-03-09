import os
from typing import List

import openai

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_embedding(text_list: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
        input=text_list,
        model="text-embedding-3-large",
        dimensions=1024
    )
    return [x.embedding for x in response.data]


def paginated_get_embedding(text_list: List[str], page_size=5) -> List[List[float]]:
    result = []
    for i in range(0, len(text_list), page_size):
        queries = text_list[i:i+page_size]
        embedding_result = get_embedding(queries)
        result.extend(embedding_result)
    return result
