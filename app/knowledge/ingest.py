import os
from app.knowledge.store import PolicyStore

def run_ingestion():
    store = PolicyStore()
    policy_path = "data/policies/sample-policy.md"
    
    if not os.path.exists(policy_path):
        print(f"Error: {policy_path} not found.")
        return

    with open(policy_path, "r") as f:
        content = f.read()

    # Split by header to keep context together
    sections = [f"## {s.strip()}" for s in content.split("##") if s.strip()]
    
    store.upsert_policy_chunks(sections)
    print(f"Indexed {len(sections)} sections.")

if __name__ == "__main__":
    run_ingestion()
