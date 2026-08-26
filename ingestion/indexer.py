from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Optional

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None


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

        # Ingest syllabus microtopics if available
        syllabus_path = ROOT / "data" / "upsc_syllabus_microtopics.json"
        if syllabus_path.exists():
            try:
                with open(syllabus_path, encoding="utf-8") as sf:
                    s_data = json.load(sf)
                for paper, pdata in s_data.items():
                    for subj_key, sdata in pdata.get("subjects", {}).items():
                        for top_key, tdata in sdata.get("topics", {}).items():
                            topic_name = tdata.get("title", top_key)
                            for micro in tdata.get("microtopics", []):
                                record_id = f"sys_{paper}_{subj_key}_{topic_name}_{micro[:15]}".lower().replace(" ", "_")
                                self.records.append({
                                    "id": record_id,
                                    "category": "academic",
                                    "intent": "notes_or_explain_topic",
                                    "priority": 40,
                                    "question": f"Explain UPSC syllabus topic {micro} under {topic_name}",
                                    "question_variants": [
                                        micro,
                                        f"Notes on {micro}",
                                        f"What is {micro} in UPSC {paper}?",
                                        f"Explain {micro} ({sdata.get('title', subj_key)})"
                                    ],
                                    "answer_content": f"UPSC GS Mains Syllabus Microtopic: {micro}. Topic: {topic_name}. Subject: {sdata.get('title', subj_key)}. Paper: {paper}.",
                                    "metadata": {
                                        "subject": sdata.get("title", subj_key),
                                        "paper": paper,
                                        "syllabus_topic": topic_name,
                                        "microtopic": micro
                                    }
                                })
            except Exception:
                pass

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
        if not self.vectorizer or self.matrix is None or cosine_similarity is None:
            return []

        try:
            query_vec = self.vectorizer.transform([query])
            scores = cosine_similarity(query_vec, self.matrix).flatten()
        except Exception:
            return []

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
