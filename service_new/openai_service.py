from typing import List

import openai


class OpenaiService:
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)

    def get_embedding(self, text_list: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=text_list, model="text-embedding-3-large", dimensions=1024
        )
        return [x.embedding for x in response.data]

    def paginated_get_embedding(
        self, text_list: List[str], page_size=5
    ) -> List[List[float]]:
        result = []
        for i in range(0, len(text_list), page_size):
            queries = text_list[i : i + page_size]
            embedding_result = self.get_embedding(queries)
            result.extend(embedding_result)
        return result

    def get_streaming_response(self, messages: List[dict], model="gpt-3.5-turbo-0125"):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            timeout=10,
            stream=True,
        )
        return response
