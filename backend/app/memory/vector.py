# Minimal vector store placeholder (swap with FAISS)
class VectorStore:
    def __init__(self):
        self.docs = {}
    def add_vector(self, vector_id: str, text: str):
        """Add a vector with an ID"""
        self.docs[vector_id] = text
    def add(self, text: str):
        """Add a vector without ID"""
        self.docs[len(self.docs)] = text
    def search(self, q: str):
        return list(self.docs.values())[:3]
