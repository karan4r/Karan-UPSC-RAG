#!/usr/bin/env python3
"""Build vector index from qa_corpus.json."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestion.indexer import build_index

if __name__ == "__main__":
    index = build_index()
    print(f"Indexed {len(index.records)} records -> data/vector_index.pkl")
