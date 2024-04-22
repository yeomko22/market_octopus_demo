from pinecone import Pinecone
from datetime import datetime, timedelta
from typing import List


class PineconeService:
    def __init__(self, pinecone_api_key: str):
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index = self.pc.Index("superbsearch-new")

    def search(
        self,
        query_vector: List[float],
        top_k: int,
        include_metadata: bool,
        namespace: str,
        filter: dict,
    ) -> List[dict]:
        response = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=include_metadata,
            namespace=namespace,
            filter=filter,
        )
        matches = response["matches"]
        return matches
