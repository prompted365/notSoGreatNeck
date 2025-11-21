#!/usr/bin/env python3
"""
Binder Chunker Agent for RICO Evidence Processing
Chunks binder.txt into semantic segments, generates embeddings, and performs DBSCAN clustering.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import umap
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Configuration
BINDER_PATH = "/Users/breydentaylor/certainly/noteworthy-raw/binder.txt"
OUTPUT_DIR = "/Users/breydentaylor/certainly/visualizations"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "binder_chunks"
DBSCAN_EPS = 0.3
DBSCAN_MIN_SAMPLES = 3

def load_binder_content():
    """Load the binder.txt file content."""
    print(f"Loading binder content from {BINDER_PATH}...")
    with open(BINDER_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"Loaded {len(content)} characters")
    return content

def chunk_text(content):
    """Split text into semantic chunks using RecursiveCharacterTextSplitter."""
    print(f"\nChunking text with chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = text_splitter.split_text(content)
    print(f"Created {len(chunks)} chunks")
    return chunks

def generate_embeddings(chunks):
    """Generate embeddings for chunks using sentence-transformers."""
    print(f"\nGenerating embeddings using {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(chunks, show_progress_bar=True)
    print(f"Generated {len(embeddings)} embeddings with dimension {embeddings.shape[1]}")
    return embeddings, model

def setup_qdrant_collection(embeddings):
    """Create in-memory Qdrant collection."""
    print(f"\nSetting up in-memory Qdrant collection '{COLLECTION_NAME}'...")
    client = QdrantClient(":memory:")

    # Create collection
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=embeddings.shape[1], distance=Distance.COSINE),
    )
    print(f"Created collection with {embeddings.shape[1]}-dimensional vectors")
    return client

def upload_chunks_to_qdrant(client, chunks, embeddings):
    """Upload chunks with embeddings to Qdrant."""
    print(f"\nUploading {len(chunks)} chunks to Qdrant...")

    points = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point = PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={"text": chunk, "chunk_id": idx}
        )
        points.append(point)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"Uploaded {len(points)} points to collection")
    return points

def perform_dbscan_clustering(embeddings):
    """Run DBSCAN clustering on embeddings."""
    print(f"\nPerforming DBSCAN clustering (eps={DBSCAN_EPS}, min_samples={DBSCAN_MIN_SAMPLES})...")

    dbscan = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES, metric='cosine')
    cluster_labels = dbscan.fit_predict(embeddings)

    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    n_noise = list(cluster_labels).count(-1)

    print(f"Found {n_clusters} clusters")
    print(f"Noise points (cluster -1): {n_noise}")

    return cluster_labels

def label_clusters_with_tfidf(chunks, cluster_labels, top_n=5):
    """Label each cluster using TF-IDF top keywords."""
    print(f"\nLabeling clusters using TF-IDF (top {top_n} keywords)...")

    unique_clusters = set(cluster_labels)
    cluster_data = {}

    for cluster_id in unique_clusters:
        # Get chunks for this cluster
        cluster_chunks = [chunks[i] for i, label in enumerate(cluster_labels) if label == cluster_id]

        if not cluster_chunks:
            continue

        # Combine chunks for TF-IDF
        combined_text = " ".join(cluster_chunks)

        # Extract top keywords using TF-IDF
        vectorizer = TfidfVectorizer(max_features=top_n, stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform([combined_text])
            feature_names = vectorizer.get_feature_names_out()

            # Get top keywords
            tfidf_scores = tfidf_matrix.toarray()[0]
            top_indices = tfidf_scores.argsort()[-top_n:][::-1]
            top_keywords = [feature_names[i] for i in top_indices]

            # Generate label from top 2-3 keywords
            label = " ".join(top_keywords[:3]).upper()

            cluster_data[int(cluster_id)] = {
                "cluster_id": int(cluster_id),
                "label": label,
                "top_keywords": top_keywords,
                "chunk_count": len(cluster_chunks)
            }
        except Exception as e:
            print(f"Warning: Could not process cluster {cluster_id}: {e}")
            cluster_data[int(cluster_id)] = {
                "cluster_id": int(cluster_id),
                "label": f"CLUSTER_{cluster_id}",
                "top_keywords": [],
                "chunk_count": len(cluster_chunks)
            }

    print(f"Labeled {len(cluster_data)} clusters")
    return cluster_data

def create_umap_visualization(embeddings, cluster_labels, output_path):
    """Generate UMAP 2D visualization and save as PNG."""
    print(f"\nCreating UMAP 2D visualization...")

    # Reduce to 2D using UMAP
    reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
    embedding_2d = reducer.fit_transform(embeddings)

    # Create visualization
    plt.figure(figsize=(16, 12))

    # Get unique clusters
    unique_labels = set(cluster_labels)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

    for label, color in zip(unique_labels, colors):
        if label == -1:
            # Noise points in black
            color = 'k'
            marker = 'x'
            label_text = 'Noise'
        else:
            marker = 'o'
            label_text = f'Cluster {label}'

        mask = cluster_labels == label
        plt.scatter(
            embedding_2d[mask, 0],
            embedding_2d[mask, 1],
            c=[color],
            label=label_text,
            alpha=0.6,
            s=50,
            marker=marker
        )

    plt.title('DBSCAN Clustering of Binder Chunks (UMAP 2D Projection)', fontsize=16, fontweight='bold')
    plt.xlabel('UMAP Dimension 1', fontsize=12)
    plt.ylabel('UMAP Dimension 2', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved UMAP visualization to {output_path}")
    plt.close()

def save_outputs(chunks, embeddings, cluster_labels, cluster_data, output_dir):
    """Save all outputs to files."""
    print(f"\nSaving outputs to {output_dir}...")

    output_dir = Path(output_dir)

    # Save chunks with embeddings
    chunks_output = []
    for idx, (chunk, embedding, label) in enumerate(zip(chunks, embeddings, cluster_labels)):
        chunks_output.append({
            "chunk_id": idx,
            "text": chunk,
            "embedding": embedding.tolist(),
            "cluster_id": int(label)
        })

    chunks_file = output_dir / "binder_chunks.json"
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_output, f, indent=2)
    print(f"Saved {len(chunks_output)} chunks to {chunks_file}")

    # Save cluster labels
    labels_file = output_dir / "binder_cluster_labels.json"
    with open(labels_file, 'w', encoding='utf-8') as f:
        json.dump(list(cluster_data.values()), f, indent=2)
    print(f"Saved cluster labels to {labels_file}")

    # Create UMAP visualization
    viz_file = output_dir / "binder_clusters_umap.png"
    create_umap_visualization(embeddings, cluster_labels, viz_file)

    return chunks_file, labels_file, viz_file

def main():
    """Main execution function."""
    print("=" * 80)
    print("BINDER CHUNKER AGENT - RICO EVIDENCE PROCESSING")
    print("=" * 80)

    # Step 1: Load content
    content = load_binder_content()

    # Step 2: Chunk text
    chunks = chunk_text(content)

    # Step 3: Generate embeddings
    embeddings, model = generate_embeddings(chunks)

    # Step 4: Setup Qdrant
    client = setup_qdrant_collection(embeddings)

    # Step 5: Upload to Qdrant
    points = upload_chunks_to_qdrant(client, chunks, embeddings)

    # Step 6: DBSCAN clustering
    cluster_labels = perform_dbscan_clustering(embeddings)

    # Step 7: Label clusters
    cluster_data = label_clusters_with_tfidf(chunks, cluster_labels)

    # Step 8: Save outputs
    chunks_file, labels_file, viz_file = save_outputs(
        chunks, embeddings, cluster_labels, cluster_data, OUTPUT_DIR
    )

    # Final summary
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE - SUMMARY")
    print("=" * 80)
    print(f"Total chunks created: {len(chunks)}")
    print(f"Number of clusters found: {len([c for c in cluster_data.keys() if c != -1])}")
    print(f"Noise points: {list(cluster_labels).count(-1)}")
    print(f"\nTop 5 Cluster Labels:")

    # Sort by chunk count and show top 5
    sorted_clusters = sorted(cluster_data.values(), key=lambda x: x['chunk_count'], reverse=True)
    for i, cluster in enumerate(sorted_clusters[:5], 1):
        print(f"  {i}. {cluster['label']} ({cluster['chunk_count']} chunks)")
        print(f"     Keywords: {', '.join(cluster['top_keywords'])}")

    print(f"\nFiles created:")
    print(f"  - {chunks_file}")
    print(f"  - {labels_file}")
    print(f"  - {viz_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
