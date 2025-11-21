#!/usr/bin/env python3
"""
Quick Search Utility for Qdrant Corpus
Usage: python3 search_corpus.py "your search query"
"""

import sys
import json
from pathlib import Path
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Configuration
QDRANT_DB_PATH = Path("/Users/breydentaylor/certainly/visualizations/qdrant_db")
COLLECTION_NAME = "shurka_corpus"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def search(query: str, limit: int = 10):
    """Perform semantic search on the corpus"""
    print(f"\n🔍 Searching for: '{query}'")
    print("=" * 70)

    # Initialize
    client = QdrantClient(path=str(QDRANT_DB_PATH))
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Generate query embedding
    query_embedding = model.encode(query).tolist()

    # Search
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit
    ).points

    if not results:
        print("No results found.")
        return []

    # Display results
    print(f"\nFound {len(results)} results:\n")

    formatted_results = []
    for i, result in enumerate(results, 1):
        score = result.score
        filename = result.payload.get("filename", "Unknown")
        chunk_num = result.payload.get("chunk_number", "?")
        priority = result.payload.get("priority", "N/A")
        evidence_types = ", ".join(result.payload.get("evidence_types", []))
        text_preview = result.payload.get("text_preview", "")[:200]

        print(f"[{i}] Score: {score:.4f} | Priority: {priority}")
        print(f"    File: {filename} (chunk {chunk_num})")
        print(f"    Evidence: {evidence_types}")
        print(f"    Preview: {text_preview}...")
        print()

        formatted_results.append({
            "rank": i,
            "score": float(score),
            "filename": filename,
            "chunk_number": chunk_num,
            "priority": priority,
            "evidence_types": evidence_types,
            "preview": text_preview
        })

    return formatted_results

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 search_corpus.py \"your search query\" [limit]")
        print("\nExamples:")
        print('  python3 search_corpus.py "Jason Shurka fraud"')
        print('  python3 search_corpus.py "cryptocurrency wallet" 20')
        print('  python3 search_corpus.py "victim complaint UNIFYD"')
        sys.exit(1)

    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    results = search(query, limit)

    print("=" * 70)
    print(f"✅ Search complete. Found {len(results)} results.")

if __name__ == "__main__":
    main()
