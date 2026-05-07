import os
import chromadb
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PolicyStore:
    def __init__(self, db_path: str = "./data/vector_db"):
        self.chroma = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma.get_or_create_collection(
            name="voltedge_rules",
            metadata={"hnsw:space": "cosine"}
        )

    def _get_embedding(self, text: str):
        res = client.embeddings.create(input=text, model="text-embedding-3-small")
        return res.data[0].embedding

    def upsert_policy_chunks(self, chunks: list):
        # Using upsert to ensure re-running the ingestion script doesn't create duplicate entries.
        embeddings = [self._get_embedding(c) for c in chunks]
        ids = [f"segment_{i}" for i in range(len(chunks))]
        metadatas = [{"source": "volt_edge_v1"} for _ in chunks]

        self.collection.upsert(
            ids=ids, 
            documents=chunks, 
            embeddings=embeddings, 
            metadatas=metadatas
        )

    def search(self, query: str, limit: int = 3):
        query_vec = self._get_embedding(query)
        results = self.collection.query(query_embeddings=[query_vec], n_results=limit)
        return results.get("documents", [[]])[0]
