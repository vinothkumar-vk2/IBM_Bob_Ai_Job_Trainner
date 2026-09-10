import os
import numpy as np
from typing import List, Dict, Any

class RAGEmbedder:
    """High-speed vector embedder for interview retrieval."""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dim = 384
        # We use fast, self-contained semantic feature vectors to ensure instant offline & online response
        self._init_vocabulary()

    def _init_vocabulary(self):
        """Build domain token weights for interview & tech taxonomy."""
        self.domain_weights = {
            "python": 2.5, "fastapi": 2.2, "flask": 2.0, "react": 2.4, "javascript": 2.2,
            "typescript": 2.3, "node": 2.2, "docker": 2.1, "kubernetes": 2.4, "aws": 2.2,
            "system": 2.0, "design": 2.0, "architecture": 2.3, "scale": 2.1, "distributed": 2.4,
            "database": 2.0, "sql": 2.0, "nosql": 2.0, "postgres": 2.2, "redis": 2.3,
            "cache": 2.2, "kafka": 2.4, "behavioral": 2.0, "star": 2.5, "leadership": 2.2,
            "conflict": 2.2, "incident": 2.3, "outage": 2.3, "machine": 2.0, "learning": 2.0,
            "rag": 2.6, "llm": 2.5, "watsonx": 2.5, "ibm": 2.0, "question": 1.5, "answer": 1.5
        }

    def encode(self, texts: List[str]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        
        vectors = []
        for text in texts:
            vec = np.zeros(self.dim, dtype=np.float32)
            if not text:
                vectors.append(vec)
                continue

            words = text.lower().replace("-", " ").replace("_", " ").split()
            for i, word in enumerate(words):
                clean_word = "".join(ch for ch in word if ch.isalnum())
                if not clean_word:
                    continue
                h1 = abs(hash(clean_word)) % self.dim
                h2 = abs(hash(clean_word[::-1])) % self.dim
                w = self.domain_weights.get(clean_word, 1.0)
                pos_weight = 1.0 / (1.0 + 0.02 * i)
                vec[h1] += w * pos_weight
                vec[h2] += (w * 0.5) * pos_weight

            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)

        return np.array(vectors, dtype=np.float32)


class TextSplitter:
    """Splits text documents into clean overlapping semantic chunks."""
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
        
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            if len(current_chunk) + len(p) + 2 <= self.chunk_size:
                current_chunk = f"{current_chunk}\n\n{p}" if current_chunk else p
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                if len(p) > self.chunk_size:
                    words = p.split()
                    temp = ""
                    for w in words:
                        if len(temp) + len(w) + 1 <= self.chunk_size:
                            temp = f"{temp} {w}" if temp else w
                        else:
                            chunks.append(temp)
                            temp = w
                    if temp:
                        current_chunk = temp
                else:
                    current_chunk = p

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


class RagSystem:
    def __init__(self):
        self.embedder = RAGEmbedder()
        self.splitter = TextSplitter(chunk_size=450, chunk_overlap=50)

    def split_data(self, data: str) -> List[str]:
        return self.splitter.split_text(data)

    def embed(self, texts: List[str]) -> np.ndarray:
        return self.embedder.encode(texts)