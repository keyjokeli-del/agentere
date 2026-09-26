import re
import math
import hashlib
from typing import List, Optional
import httpx
from app.config import settings


class EmbeddingService:
    """Zero-RAM footprint embedding service.
    
    Uses Google Gemini text-embedding-004 API (dim=768) when GEMINI_API_KEY is available.
    Falls back deterministically to a normalized 768-dim token-hashing embedding
    requiring 0 MB of local ML dependencies.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.gemini_api_key

    def embed_text(self, text: str) -> List[float]:
        """Generates a 768-dimensional normalized embedding vector."""
        clean_text = (text or "").strip()
        if not clean_text:
            return self._deterministic_hash_embedding("empty")

        if self.api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"
                payload = {
                    "model": "models/text-embedding-004",
                    "content": {"parts": [{"text": clean_text[:2048]}]}
                }
                with httpx.Client(timeout=6.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        vals = data.get("embedding", {}).get("values")
                        if vals and len(vals) == 768:
                            return [float(v) for v in vals]
            except Exception:
                pass

        return self._deterministic_hash_embedding(clean_text)

    def _deterministic_hash_embedding(self, text: str, dim: int = 768) -> List[float]:
        """Deterministic, sub-millisecond 768-dim normalized vector with 0 MB RAM overhead."""
        vec = [0.0] * dim
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            tokens = ["empty"]

        for token in tokens:
            h_sha = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16)
            h_md5 = int(hashlib.md5(token.encode("utf-8")).hexdigest()[:8], 16)
            vec[h_sha % dim] += 1.0
            vec[h_md5 % dim] += 0.5

            if len(token) > 3:
                for i in range(len(token) - 2):
                    ngram = token[i:i+3]
                    h_ng = int(hashlib.md5(ngram.encode("utf-8")).hexdigest()[:6], 16)
                    vec[h_ng % dim] += 0.3

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            return [x / norm for x in vec]
        vec[0] = 1.0
        return vec

    def format_pgvector(self, embedding: List[float]) -> str:
        """Formats python list as pgvector literal string '[v1,v2,...]'."""
        return "[" + ",".join(f"{x:.6f}" for x in embedding) + "]"


embedding_service = EmbeddingService()
