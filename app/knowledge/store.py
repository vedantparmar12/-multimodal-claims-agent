import os
import shutil
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _get_db_path() -> str:
    # Vercel filesystem is read-only except /tmp — copy bundled DB there on cold start
    bundled = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/vector_db"))
    if os.environ.get("VERCEL"):
        tmp = "/tmp/chroma_db"
        if not os.path.exists(tmp) and os.path.exists(bundled):
            shutil.copytree(bundled, tmp)
        return tmp
    return bundled

class PolicyStore:
    def __init__(self):
        db_path = _get_db_path()
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
        return [
            {
                "clause_id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "title": results["metadatas"][0][i].get("source", "policy_clause"),
                "relevance_score": round(1 - results["distances"][0][i], 3)
            }
            for i in range(len(results["ids"][0]))
        ]
