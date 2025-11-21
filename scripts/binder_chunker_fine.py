#!/usr/bin/env python3
"""
Binder_Chunker Agent - FINE-GRAINED Semantic Chunking
Adjusted chunk size to reach 500-1000 target
"""

import json
import re
from pathlib import Path
from typing import List, Dict
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# ADJUSTED Configuration for finer granularity
CHUNK_SIZE = 600  # Reduced from 1000
OVERLAP = 150     # Reduced from 200
BINDER_PATH = "/Users/breydentaylor/certainly/noteworthy-raw/binder.txt"
OUTPUT_DIR = "/Users/breydentaylor/certainly/visualizations"
COORD_DIR = f"{OUTPUT_DIR}/coordination"
STATE_DIR = f"{OUTPUT_DIR}/state"

ENTITIES = ["Esther", "Talia", "Efraim", "Manny", "Jason", "Shurka", "Havakok", "Gadish"]
SHADOWLENS_PATTERNS = [
    r"shadowLens", r"court\s+doc", r"evidence\s+\d+", r"exhibit\s+[A-Z0-9-]+",
    r"filing", r"analysis"
]
DOLLAR_PATTERN = r"\$[\d,]+(?:\.\d{2})?"
DATE_PATTERN = r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|\w+\s+\d{1,2},?\s+\d{4})\b"
LEGAL_CITATION_PATTERN = r"\b\d+\s+U\.S\.C\.\s+§?\s*\d+|\b\d+\s+F\.\s*(?:2d|3d)\s+\d+"


class BinderChunker:
    """Fine-grained semantic chunker for prosecution binder."""

    def __init__(self):
        self.chunks = []
        self.clusters = None
        self.cluster_labels = {}
        self.state = {
            "run_id": "cert1-phase3-shadowlens-20251121-fine",
            "agent": "Binder_Chunker",
            "version": "fine-grained",
            "timestamp": datetime.now().isoformat(),
            "input_file": BINDER_PATH,
            "chunk_size": CHUNK_SIZE,
            "overlap": OVERLAP,
            "chunk_count": 0,
            "cluster_count": 0,
            "status": "initialized"
        }

    def load_binder(self) -> str:
        print(f"📖 Loading binder from: {BINDER_PATH}")
        with open(BINDER_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        print(f"✓ Loaded {len(content):,} characters")
        self.state["input_size_chars"] = len(content)
        return content

    def create_chunks(self, text: str) -> List[Dict]:
        print(f"\n🔪 Fine-grained chunking: size={CHUNK_SIZE}, overlap={OVERLAP}")
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + CHUNK_SIZE
            chunk_text = text[start:end]
            metadata = self.extract_metadata(chunk_text, chunk_id, start)

            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "start_pos": start,
                "end_pos": end,
                **metadata
            })

            chunk_id += 1
            start += (CHUNK_SIZE - OVERLAP)

        print(f"✓ Created {len(chunks)} chunks")
        self.chunks = chunks
        self.state["chunk_count"] = len(chunks)
        return chunks

    def extract_metadata(self, text: str, chunk_id: int, start_pos: int) -> Dict:
        metadata = {
            "entities": [],
            "shadowlens_mentions": [],
            "dollar_amounts": [],
            "dates": [],
            "legal_citations": [],
            "has_evidence": False
        }

        for entity in ENTITIES:
            if re.search(rf'\b{entity}\b', text, re.IGNORECASE):
                metadata["entities"].append(entity)

        for pattern in SHADOWLENS_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                metadata["shadowlens_mentions"].extend(matches)
                metadata["has_evidence"] = True

        metadata["dollar_amounts"] = re.findall(DOLLAR_PATTERN, text)[:5]
        metadata["dates"] = re.findall(DATE_PATTERN, text)[:5]
        metadata["legal_citations"] = re.findall(LEGAL_CITATION_PATTERN, text)[:3]

        return metadata

    def cluster_chunks(self) -> Dict[int, List[int]]:
        print(f"\n🔬 Clustering chunks with DBSCAN")
        texts = [chunk["text"] for chunk in self.chunks]

        vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )

        print("  • Computing TF-IDF vectors...")
        tfidf_matrix = vectorizer.fit_transform(texts)

        print("  • Running DBSCAN clustering...")
        dbscan = DBSCAN(eps=0.5, min_samples=3, metric='cosine')
        cluster_labels = dbscan.fit_predict(tfidf_matrix)

        self.feature_names = vectorizer.get_feature_names_out()
        self.tfidf_matrix = tfidf_matrix

        clusters = defaultdict(list)
        for idx, label in enumerate(cluster_labels):
            clusters[int(label)].append(idx)
            self.chunks[idx]["cluster"] = int(label)

        n_clusters = len([k for k in clusters.keys() if k != -1])
        n_noise = len(clusters.get(-1, []))

        print(f"✓ Found {n_clusters} clusters ({n_noise} noise points)")
        self.state["cluster_count"] = n_clusters
        self.state["noise_points"] = n_noise
        self.clusters = dict(clusters)
        return self.clusters

    def label_clusters(self) -> Dict[int, Dict]:
        print(f"\n🏷️  Labeling clusters with TF-IDF keywords")
        cluster_labels = {}

        for cluster_id, chunk_indices in self.clusters.items():
            if cluster_id == -1:
                continue

            cluster_vectors = self.tfidf_matrix[chunk_indices]
            mean_tfidf = np.asarray(cluster_vectors.mean(axis=0)).flatten()
            top_indices = mean_tfidf.argsort()[-10:][::-1]
            top_keywords = [self.feature_names[i] for i in top_indices]

            entity_counts = Counter()
            shadowlens_count = 0
            evidence_count = 0

            for idx in chunk_indices:
                chunk = self.chunks[idx]
                entity_counts.update(chunk["entities"])
                shadowlens_count += len(chunk["shadowlens_mentions"])
                if chunk["has_evidence"]:
                    evidence_count += 1

            label = self.generate_label(top_keywords, entity_counts)

            cluster_labels[cluster_id] = {
                "label": label,
                "keywords": top_keywords[:5],
                "size": len(chunk_indices),
                "entities": dict(entity_counts.most_common(3)),
                "shadowlens_mentions": shadowlens_count,
                "evidence_chunks": evidence_count,
                "chunk_ids": chunk_indices[:30]
            }

            print(f"  • Cluster {cluster_id:2d}: {label:30s} (size={len(chunk_indices):3d}, evidence={evidence_count})")

        self.cluster_labels = cluster_labels
        return cluster_labels

    def generate_label(self, keywords: List[str], entities: Counter) -> str:
        keywords_str = ' '.join(keywords).lower()

        if 'sig' in keywords_str or 'signature investment' in keywords_str:
            return "SIG OPERATIONS"
        elif 'unifyd' in keywords_str:
            return "UNIFYD FRAUD"
        elif 'blockchain' in keywords_str or 'crypto' in keywords_str:
            return "BLOCKCHAIN EVIDENCE"
        elif 'court' in keywords_str or 'filing' in keywords_str:
            return "COURT DOCUMENTS"
        elif 'child' in keywords_str or 'grooming' in keywords_str:
            return "CHILD EXPLOITATION"
        elif 'israel' in keywords_str or 'mossad' in keywords_str:
            return "ISRAELI INTELLIGENCE"
        elif 'havakok' in keywords_str:
            return "HAVAKOK NETWORK"
        elif entities and entities.most_common(1)[0][1] > 2:
            top_entity = entities.most_common(1)[0][0]
            return f"{top_entity.upper()} RELATED"
        else:
            return ' '.join(keywords[:2]).upper()

    def create_visualization(self):
        print(f"\n📊 Creating t-SNE visualization")
        try:
            tsne = TSNE(n_components=2, random_state=42, perplexity=30)
            coords_2d = tsne.fit_transform(self.tfidf_matrix.toarray())

            fig, ax = plt.subplots(figsize=(16, 12))
            cluster_ids = [chunk["cluster"] for chunk in self.chunks]
            unique_clusters = set(cluster_ids)
            colors = plt.cm.tab20(np.linspace(0, 1, len(unique_clusters)))

            for i, cluster_id in enumerate(unique_clusters):
                if cluster_id == -1:
                    continue
                mask = np.array(cluster_ids) == cluster_id
                label = self.cluster_labels.get(cluster_id, {}).get("label", f"Cluster {cluster_id}")
                size = self.cluster_labels.get(cluster_id, {}).get("size", 0)
                ax.scatter(coords_2d[mask, 0], coords_2d[mask, 1],
                          c=[colors[i]], label=f"{label} ({size})", alpha=0.6, s=30)

            ax.set_title("Binder Chunks - Fine-Grained Semantic Clustering (t-SNE)",
                        fontsize=16, fontweight='bold')
            ax.set_xlabel("t-SNE Dimension 1")
            ax.set_ylabel("t-SNE Dimension 2")
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()

            output_path = f"{OUTPUT_DIR}/binder_clusters_umap.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"✓ Saved visualization to: {output_path}")
            self.state["visualization_created"] = True

        except Exception as e:
            print(f"⚠️  Visualization failed: {e}")
            self.state["visualization_created"] = False

    def save_outputs(self):
        print(f"\n💾 Saving outputs")

        chunks_path = f"{COORD_DIR}/binder_chunks.json"
        with open(chunks_path, 'w') as f:
            json.dump(self.chunks, f, indent=2)
        print(f"  • Saved {len(self.chunks)} chunks to: {chunks_path}")

        labels_path = f"{COORD_DIR}/binder_cluster_labels.json"
        with open(labels_path, 'w') as f:
            json.dump(self.cluster_labels, f, indent=2)
        print(f"  • Saved cluster labels to: {labels_path}")

        self.state["status"] = "completed"
        self.state["completed_at"] = datetime.now().isoformat()
        state_path = f"{STATE_DIR}/binder_chunker.state.json"
        with open(state_path, 'w') as f:
            json.dump(self.state, f, indent=2)
        print(f"  • Saved state to: {state_path}")

    def print_summary(self):
        print(f"\n{'='*70}")
        print(f"🎯 BINDER_CHUNKER MISSION COMPLETE (FINE-GRAINED)")
        print(f"{'='*70}")
        print(f"Run ID: {self.state['run_id']}")
        print(f"Chunk size: {CHUNK_SIZE} chars (overlap: {OVERLAP})")
        print(f"Chunks created: {self.state['chunk_count']}")
        print(f"Clusters found: {self.state['cluster_count']}")
        print(f"Noise points: {self.state['noise_points']}")

        largest = max(self.cluster_labels.items(), key=lambda x: x[1]['size'])
        print(f"\n📊 Largest Cluster:")
        print(f"  • ID: {largest[0]}")
        print(f"  • Label: {largest[1]['label']}")
        print(f"  • Size: {largest[1]['size']} chunks")
        print(f"  • Evidence chunks: {largest[1]['evidence_chunks']}")

        total_shadowlens = sum(c.get('shadowlens_mentions', 0)
                              for c in self.cluster_labels.values())
        total_evidence_chunks = sum(1 for c in self.chunks if c.get('has_evidence', False))

        print(f"\n🔍 ShadowLens Evidence:")
        print(f"  • Total mentions: {total_shadowlens}")
        print(f"  • Evidence chunks: {total_evidence_chunks}")

        print(f"\n✅ Success Criteria:")
        success = True

        if self.state['chunk_count'] >= 500:
            print(f"  ✓ Chunks: {self.state['chunk_count']} (≥500)")
        else:
            print(f"  ⚠️  Chunks: {self.state['chunk_count']} (target: ≥500)")
            success = False

        if 10 <= self.state['cluster_count'] <= 20:
            print(f"  ✓ Clusters: {self.state['cluster_count']} (10-20)")
        else:
            print(f"  ⚠️  Clusters: {self.state['cluster_count']} (target: 10-20)")

        if largest[1]['label'] in ['SIG OPERATIONS', 'UNIFYD FRAUD']:
            print(f"  ✓ Largest cluster: {largest[1]['label']}")
        else:
            print(f"  ⚠️  Largest cluster: {largest[1]['label']}")

        print(f"\n{'='*70}")
        print(f"Mission status: {'SUCCESS ✓' if success else 'PARTIAL SUCCESS ⚠️'}")
        print(f"{'='*70}\n")

    def run(self):
        print(f"\n🚀 Starting Binder_Chunker Agent (FINE-GRAINED)")
        print(f"Run ID: {self.state['run_id']}\n")

        text = self.load_binder()
        self.create_chunks(text)
        self.cluster_chunks()
        self.label_clusters()
        self.create_visualization()
        self.save_outputs()
        self.print_summary()


def main():
    chunker = BinderChunker()
    chunker.run()


if __name__ == "__main__":
    main()
