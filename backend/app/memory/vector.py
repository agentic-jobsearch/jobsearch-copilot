# Minimal vector store placeholder (swap with FAISS)
class VectorStore:
    def __init__(self):
        self.docs = []
    def add(self, text: str):
        self.docs.append(text)
    def search(self, q: str):
        return self.docs[:3]
