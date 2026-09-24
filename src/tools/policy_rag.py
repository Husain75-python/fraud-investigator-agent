import chromadb
from typing import List

class PolicyRAG:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("bank_policies")
        self._seed_policies()

    def _seed_policies(self):
        """Populates memory vector store with baseline fraud policy rules."""
        policies = [
            "POL-101: Transactions with risk score > 0.85 from unrecognized devices require immediate account block and SAR filing.",
            "POL-102: Transactions with risk score between 0.40 and 0.85 must trigger Step-Up Authentication before processing.",
            "POL-103: Multi-account device sharing across more than 3 customer accounts is considered organized fraud typology.",
            "POL-104: Suspicious Activity Reports (SARs) must be filed within 30 days for any confirmed identity takeover pattern."
        ]
        self.collection.add(
            documents=policies,
            ids=[f"p_{i}" for i in range(len(policies))]
        )

    def search_policies(self, query: str, top_k: int = 2) -> List[str]:
        """Retrieves relevant policy rules based on investigation context."""
        results = self.collection.query(query_texts=[query], n_results=top_k)
        return results["documents"][0] if results["documents"] else []