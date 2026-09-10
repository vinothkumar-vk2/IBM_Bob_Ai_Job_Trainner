import numpy as np
from typing import List, Dict, Any
import os

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[VectorDB] FAISS not found, using pure numpy cosine similarity index.")

from Rag_system.interview_kb import INTERVIEW_KNOWLEDGE

class VectorDB:
    """FAISS-backed Vector Database for role-specific interview knowledge retrieval and resume indexing."""
    
    def __init__(self, rag_system=None):
        from Rag_system.reg_system import RagSystem
        self.rag = rag_system or RagSystem()
        self.index = None
        self.chunks: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = None
        
        # Pre-seed with knowledge base
        self.initialize_knowledge_base()

    def initialize_knowledge_base(self):
        """Indexes the built-in comprehensive interview knowledge base."""
        kb_chunks = []
        kb_meta = []
        
        for item in INTERVIEW_KNOWLEDGE:
            header = f"[Role: {item['role']} | Category: {item['category']} | Topic: {item.get('topic', '')}]"
            full_text = f"{header}\n{item['content']}"
            sub_chunks = self.rag.split_data(full_text)
            for sc in sub_chunks:
                kb_chunks.append(sc)
                kb_meta.append({
                    "source": "knowledge_base",
                    "role": item["role"],
                    "category": item["category"]
                })
        
        if kb_chunks:
            self.add_texts(kb_chunks, kb_meta)
            print(f"[VectorDB] Indexed {len(kb_chunks)} foundational interview knowledge chunks.")

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]] = None):
        """Embeds and adds new text chunks to the vector database."""
        if not texts:
            return
        
        new_embeddings = self.rag.embed(texts)
        
        if self.embeddings is None:
            self.embeddings = new_embeddings
            self.chunks = list(texts)
            self.metadata = list(metadatas) if metadatas else [{"source": "custom"}] * len(texts)
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
            self.chunks.extend(texts)
            if metadatas:
                self.metadata.extend(metadatas)
            else:
                self.metadata.extend([{"source": "custom"}] * len(texts))

        dimension = self.embeddings.shape[1]
        
        if FAISS_AVAILABLE:
            # Using Inner Product (cosine similarity on normalized vectors)
            self.index = faiss.IndexFlatIP(dimension)
            self.index.add(self.embeddings)

    def create_index(self, document_text: str, source_label: str = "uploaded_document"):
        """Indexes user-provided documents (resumes, job descriptions)."""
        chunks = self.rag.split_data(document_text)
        if not chunks:
            return
        metas = [{"source": source_label, "chunk_id": i} for i in range(len(chunks))]
        self.add_texts(chunks, metas)

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Performs semantic similarity search for a query against indexed chunks."""
        if self.embeddings is None or len(self.chunks) == 0:
            return []

        top_k = min(top_k, len(self.chunks))
        query_vec = self.rag.embed([query])

        results = []
        if FAISS_AVAILABLE and self.index is not None:
            distances, indices = self.index.search(query_vec, top_k)
            for dist, idx in zip(distances[0], indices[0]):
                if 0 <= idx < len(self.chunks):
                    results.append({
                        "text": self.chunks[idx],
                        "metadata": self.metadata[idx] if idx < len(self.metadata) else {},
                        "score": float(dist)
                    })
        else:
            # Cosine similarity via NumPy
            scores = np.dot(self.embeddings, query_vec.T).squeeze()
            if scores.ndim == 0:
                top_indices = [0]
            else:
                top_indices = np.argsort(scores)[::-1][:top_k]
            for idx in top_indices:
                score = float(scores[idx]) if scores.ndim > 0 else float(scores)
                results.append({
                    "text": self.chunks[idx],
                    "metadata": self.metadata[idx] if idx < len(self.metadata) else {},
                    "score": score
                })

        return results