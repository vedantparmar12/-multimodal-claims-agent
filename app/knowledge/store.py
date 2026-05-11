import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _get_embedding(text: str):
    res = _openai.embeddings.create(input=text, model="text-embedding-3-small")
    return res.data[0].embedding

class PolicyStore:
    # Module-level singleton — seeded once per container lifecycle
    _instance = None

    @classmethod
    def get(cls) -> "PolicyStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # EphemeralClient = in-memory, no filesystem writes, works on Vercel
        self.chroma = chromadb.EphemeralClient()
        self.collection = self.chroma.get_or_create_collection(
            name="voltedge_rules",
            metadata={"hnsw:space": "cosine"}
        )
        self._seed_if_empty()

    def _seed_if_empty(self):
        if self.collection.count() > 0:
            return
        policy_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../data/policies/sample-policy.md")
        )
        if not os.path.exists(policy_path):
            return
        with open(policy_path) as f:
            content = f.read()
        sections = [f"## {s.strip()}" for s in content.split("##") if s.strip()]
        self.upsert_policy_chunks(sections)

    def upsert_policy_chunks(self, chunks: list):
        embeddings = [_get_embedding(c) for c in chunks]
        ids = [f"segment_{i}" for i in range(len(chunks))]
        metadatas = [{"source": "volt_edge_v1"} for _ in chunks]
        self.collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query: str, limit: int = 3):
        query_vec = _get_embedding(query)
        results = self.collection.query(query_embeddings=[query_vec], n_results=limit)
        return [
            {
                "clause_id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "title": results["metadatas"][0][i].get("source", "policy_clause"),
                "relevance_score": round(1 - results["distances"][0][i], 3)
            }
            for i in range(len(results["ids"][0]))
        ]
