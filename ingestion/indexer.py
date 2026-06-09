from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "data" / "qa_corpus.json"
INDEX_PATH = ROOT / "data" / "vector_index.pkl"


class VectorIndex:
    def __init__(self):
        self.records: list[dict[str, Any]] = []
        self.documents: list[str] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None

    def _record_text(self, record: dict) -> str:
        parts = [
            record.get("question", ""),
            " ".join(record.get("question_variants", [])),
            record.get("answer_content", ""),
            record.get("answer_template", ""),
            record.get("metadata", {}).get("syllabus_topic", ""),
            record.get("metadata", {}).get("subject", ""),
        ]
        return " ".join(p for p in parts if p)

    def build(self, corpus_path: Path = CORPUS_PATH) -> None:
        with open(corpus_path, encoding="utf-8") as f:
            self.records = json.load(f)

        self.documents = [self._record_text(r) for r in self.records]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.documents)

    def save(self, path: Path = INDEX_PATH) -> None:
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "records": self.records,
                    "documents": self.documents,
                    "vectorizer": self.vectorizer,
                    "matrix": self.matrix,
                },
                f,
            )

    def load(self, path: Path = INDEX_PATH) -> None:
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.records = data["records"]
        self.documents = data["documents"]
        self.vectorizer = data["vectorizer"]
        self.matrix = data["matrix"]

    def search(self, query: str, top_k: int = 3, category: Optional[str] = None) -> list[dict]:
        if not self.vectorizer or self.matrix is None:
            raise RuntimeError("Index not built. Run ingestion first.")

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()

        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True,
        )

        results = []
        for idx, score in ranked:
            record = self.records[idx]
            if category and record.get("category") != category:
                continue
            results.append({"record": record, "score": float(score)})
            if len(results) >= top_k:
                break
        return results

    def get_by_intent(self, intent: str) -> Optional[dict]:
        for record in self.records:
            if record.get("intent") == intent:
                return record
        return None


def build_index() -> VectorIndex:
    index = VectorIndex()
    index.build()
    index.save()
    return index


def load_index() -> VectorIndex:
    index = VectorIndex()
    if INDEX_PATH.exists():
        index.load()
    else:
        index = build_index()
    return index
