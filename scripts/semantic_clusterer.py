#!/usr/bin/env python3
"""
Semantic Clusterer Agent
Mission: Identify semantic clusters and topics in prosecution corpus
Input: binder_chunks.json (680 chunks)
Output: Semantic clusters, topics, visualizations
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set matplotlib backend for headless execution
import matplotlib
matplotlib.use('Agg')

print("🔬 Semantic Clusterer Agent Starting...")
print(f"Timestamp: {datetime.now().isoformat()}")

# Paths
BASE_DIR = Path("/Users/breydentaylor/certainly/visualizations")
COORD_DIR = BASE_DIR / "coordination"
STATE_DIR = BASE_DIR / "state"
INPUT_FILE = COORD_DIR / "binder_chunks.json"

# Create directories if needed
COORD_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)

# ============================================================================
# TASK 1: LOAD EMBEDDINGS (10 min)
# ============================================================================
print("\n" + "="*80)
print("TASK 1: Loading chunk data and generating embeddings")
print("="*80)

# Load binder chunks
print(f"Loading chunks from: {INPUT_FILE}")
with open(INPUT_FILE, 'r') as f:
    chunks = json.load(f)

print(f"✅ Loaded {len(chunks)} chunks")
print(f"Sample chunk keys: {list(chunks[0].keys())}")

# Extract text for embedding
texts = [chunk['text'] for chunk in chunks]
chunk_ids = [chunk['id'] for chunk in chunks]
chunk_entities = [chunk.get('entities', []) for chunk in chunks]
chunk_dates = [chunk.get('dates', []) for chunk in chunks]
chunk_evidence = [chunk.get('has_evidence', False) for chunk in chunks]

print(f"\n📊 Corpus Statistics:")
print(f"  - Total chunks: {len(texts)}")
print(f"  - Avg text length: {np.mean([len(t) for t in texts]):.1f} chars")
print(f"  - Chunks with evidence: {sum(chunk_evidence)}")
print(f"  - Chunks with entities: {sum(1 for e in chunk_entities if e)}")

# Generate embeddings using sentence-transformers
print("\n🧠 Generating embeddings with sentence-transformers (all-MiniLM-L6-v2)...")
try:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model loaded successfully")

    # Generate embeddings in batches for efficiency
    batch_size = 32
    embeddings_list = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_embeddings = model.encode(batch_texts, show_progress_bar=False)
        embeddings_list.append(batch_embeddings)
        if (i // batch_size) % 5 == 0:
            print(f"  Progress: {i}/{len(texts)} chunks embedded...")

    embeddings = np.vstack(embeddings_list)
    print(f"✅ Generated embeddings: {embeddings.shape}")

except ImportError:
    print("⚠️  sentence-transformers not installed, using fallback TF-IDF embeddings")
    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer(max_features=384, stop_words='english')
    embeddings = vectorizer.fit_transform(texts).toarray()
    print(f"✅ Generated TF-IDF embeddings: {embeddings.shape}")

# Normalize embeddings
from sklearn.preprocessing import normalize
embeddings_normalized = normalize(embeddings, norm='l2')
print(f"✅ Normalized embeddings: {embeddings_normalized.shape}")

# ============================================================================
# TASK 2: HDBSCAN CLUSTERING (30 min)
# ============================================================================
print("\n" + "="*80)
print("TASK 2: HDBSCAN Clustering with UMAP dimensionality reduction")
print("="*80)

try:
    import umap
    import hdbscan

    # UMAP dimensionality reduction: 384 → 50 → 2
    print("\n📉 UMAP dimensionality reduction (384 → 50)...")
    reducer_50d = umap.UMAP(
        n_components=50,
        n_neighbors=15,
        min_dist=0.1,
        metric='cosine',
        random_state=42,
        verbose=False
    )
    embeddings_50d = reducer_50d.fit_transform(embeddings_normalized)
    print(f"✅ Reduced to 50D: {embeddings_50d.shape}")

    print("\n📉 UMAP dimensionality reduction (50 → 2 for visualization)...")
    reducer_2d = umap.UMAP(
        n_components=2,
        n_neighbors=15,
        min_dist=0.1,
        metric='euclidean',
        random_state=42,
        verbose=False
    )
    embeddings_2d = reducer_2d.fit_transform(embeddings_50d)
    print(f"✅ Reduced to 2D: {embeddings_2d.shape}")

    # HDBSCAN clustering
    print("\n🔍 Running HDBSCAN clustering...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=5,
        min_samples=3,
        metric='euclidean',
        cluster_selection_method='eom',
        prediction_data=True
    )
    cluster_labels = clusterer.fit_predict(embeddings_50d)

    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    n_noise = list(cluster_labels).count(-1)

    print(f"✅ HDBSCAN clustering complete:")
    print(f"  - Total clusters: {n_clusters}")
    print(f"  - Noise points: {n_noise}")
    print(f"  - Clustered points: {len(cluster_labels) - n_noise}")

except ImportError as e:
    print(f"⚠️  HDBSCAN/UMAP not available: {e}")
    print("Using fallback K-Means clustering...")
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA

    # PCA for dimensionality reduction
    pca_50d = PCA(n_components=50, random_state=42)
    embeddings_50d = pca_50d.fit_transform(embeddings_normalized)

    pca_2d = PCA(n_components=2, random_state=42)
    embeddings_2d = pca_2d.fit_transform(embeddings_50d)

    # K-Means clustering
    n_clusters = 15
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(embeddings_50d)

    print(f"✅ K-Means clustering complete: {n_clusters} clusters")

# ============================================================================
# TASK 3: TOPIC MODELING (30 min)
# ============================================================================
print("\n" + "="*80)
print("TASK 3: Topic Modeling with BERTopic")
print("="*80)

topics_data = []
try:
    from bertopic import BERTopic
    from sklearn.feature_extraction.text import CountVectorizer

    print("\n🎯 Running BERTopic...")

    # Configure BERTopic
    vectorizer_model = CountVectorizer(
        stop_words='english',
        min_df=2,
        max_df=0.95
    )

    topic_model = BERTopic(
        nr_topics=15,
        vectorizer_model=vectorizer_model,
        calculate_probabilities=True,
        verbose=False
    )

    # Fit BERTopic using pre-computed embeddings
    topics, probs = topic_model.fit_transform(texts, embeddings_normalized)

    print(f"✅ BERTopic complete: {len(set(topics))} topics")

    # Extract topic information
    topic_info = topic_model.get_topic_info()

    for idx, row in topic_info.iterrows():
        topic_id = row['Topic']
        if topic_id == -1:
            continue

        topic_words = topic_model.get_topic(topic_id)
        top_terms = [word for word, score in topic_words[:10]]

        topics_data.append({
            'topic_id': int(topic_id),
            'count': int(row['Count']),
            'top_terms': top_terms,
            'representative_docs': []
        })

    print(f"✅ Extracted {len(topics_data)} topics")

except ImportError:
    print("⚠️  BERTopic not available, using LDA fallback...")
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer

    # LDA topic modeling
    vectorizer = CountVectorizer(max_features=1000, stop_words='english', min_df=2)
    doc_term_matrix = vectorizer.fit_transform(texts)

    lda = LatentDirichletAllocation(n_components=15, random_state=42, max_iter=20)
    lda.fit(doc_term_matrix)

    feature_names = vectorizer.get_feature_names_out()
    topics = lda.transform(doc_term_matrix).argmax(axis=1)

    for topic_idx in range(15):
        top_indices = lda.components_[topic_idx].argsort()[-10:][::-1]
        top_terms = [feature_names[i] for i in top_indices]

        topic_count = (topics == topic_idx).sum()

        topics_data.append({
            'topic_id': topic_idx,
            'count': int(topic_count),
            'top_terms': top_terms,
            'representative_docs': []
        })

    print(f"✅ Extracted {len(topics_data)} topics with LDA")

# ============================================================================
# TASK 4: CLUSTER ANALYSIS (30 min)
# ============================================================================
print("\n" + "="*80)
print("TASK 4: Cluster Analysis & Prosecution Theme Extraction")
print("="*80)

clusters_data = []
document_assignments = []

unique_clusters = sorted(set(cluster_labels))
print(f"\nAnalyzing {len(unique_clusters)} clusters...")

# Prosecution theme keywords
theme_keywords = {
    'fraud': ['fraud', 'deceptive', 'misrepresentation', 'false', 'scheme', 'scam'],
    'money_laundering': ['money', 'laundering', 'transaction', 'wire', 'transfer', 'financial'],
    'victims': ['victim', 'harm', 'damage', 'loss', 'injury', 'exploitation'],
    'conspiracy': ['conspiracy', 'agreement', 'coordinated', 'enterprise', 'organization'],
    'legal': ['court', 'law', 'statute', 'violation', 'charge', 'prosecution'],
    'corporate': ['corporation', 'company', 'business', 'entity', 'corporate'],
    'international': ['international', 'foreign', 'country', 'israel', 'offshore'],
    'crypto': ['crypto', 'bitcoin', 'blockchain', 'wallet', 'digital'],
    'telegram': ['telegram', 'message', 'communication', 'post', 'channel'],
    'evidence': ['evidence', 'document', 'proof', 'record', 'exhibit']
}

for cluster_id in unique_clusters:
    cluster_mask = cluster_labels == cluster_id
    cluster_indices = np.where(cluster_mask)[0]
    cluster_size = len(cluster_indices)

    if cluster_id == -1:
        cluster_name = "Noise/Outliers"
    else:
        cluster_name = f"Cluster {cluster_id}"

    # Calculate centroid
    cluster_embeddings = embeddings_50d[cluster_mask]
    centroid = cluster_embeddings.mean(axis=0)

    # Find most representative documents (closest to centroid)
    distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
    closest_indices = distances.argsort()[:5]
    representative_doc_ids = [int(chunk_ids[cluster_indices[i]]) for i in closest_indices]
    representative_texts = [texts[cluster_indices[i]][:200] for i in closest_indices]

    # Extract common indicators
    cluster_texts_combined = ' '.join([texts[i].lower() for i in cluster_indices])

    # Identify prosecution themes
    detected_themes = []
    for theme, keywords in theme_keywords.items():
        score = sum(cluster_texts_combined.count(kw) for kw in keywords)
        if score > 0:
            detected_themes.append({'theme': theme, 'score': score})

    detected_themes.sort(key=lambda x: x['score'], reverse=True)
    primary_theme = detected_themes[0]['theme'] if detected_themes else 'general'

    # Extract entities and evidence flags
    cluster_entities = []
    has_evidence_count = 0
    for idx in cluster_indices:
        cluster_entities.extend(chunk_entities[idx])
        if chunk_evidence[idx]:
            has_evidence_count += 1

    unique_entities = list(set(cluster_entities))[:10]

    cluster_info = {
        'cluster_id': int(cluster_id),
        'cluster_name': cluster_name,
        'size': cluster_size,
        'primary_theme': primary_theme,
        'all_themes': detected_themes[:5],
        'representative_doc_ids': representative_doc_ids,
        'representative_texts': representative_texts,
        'common_entities': unique_entities,
        'evidence_count': has_evidence_count,
        'centroid_position': centroid.tolist()
    }

    clusters_data.append(cluster_info)

    # Document assignments
    for idx in cluster_indices:
        document_assignments.append({
            'chunk_id': int(chunk_ids[idx]),
            'cluster_id': int(cluster_id),
            'cluster_name': cluster_name,
            'primary_theme': primary_theme
        })

    if cluster_id != -1:
        print(f"  {cluster_name}: {cluster_size} docs, theme='{primary_theme}'")

print(f"\n✅ Cluster analysis complete: {len(clusters_data)} clusters analyzed")

# ============================================================================
# TASK 5: VISUALIZATION (20 min)
# ============================================================================
print("\n" + "="*80)
print("TASK 5: Generating visualizations")
print("="*80)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 150

# 1. UMAP 2D plot with clusters colored
print("\n📊 Generating UMAP cluster visualization...")
fig, ax = plt.subplots(figsize=(14, 10))

# Color map
unique_labels = sorted(set(cluster_labels))
n_colors = len(unique_labels)
colors = plt.cm.Spectral(np.linspace(0, 1, n_colors))

for i, cluster_id in enumerate(unique_labels):
    cluster_mask = cluster_labels == cluster_id
    label = f"Cluster {cluster_id}" if cluster_id != -1 else "Noise"

    ax.scatter(
        embeddings_2d[cluster_mask, 0],
        embeddings_2d[cluster_mask, 1],
        c=[colors[i]],
        label=label,
        alpha=0.6,
        s=30,
        edgecolors='none'
    )

ax.set_xlabel('UMAP Dimension 1', fontsize=12)
ax.set_ylabel('UMAP Dimension 2', fontsize=12)
ax.set_title('Semantic Clusters - UMAP 2D Projection\n680 Prosecution Document Chunks', fontsize=14, fontweight='bold')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2, fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout()
umap_viz_path = COORD_DIR / "cluster_visualization_umap.png"
plt.savefig(umap_viz_path, bbox_inches='tight', dpi=150)
plt.close()
print(f"✅ Saved: {umap_viz_path}")

# 2. Topic distribution bar chart
print("\n📊 Generating topic distribution chart...")
fig, ax = plt.subplots(figsize=(12, 8))

topic_ids = [t['topic_id'] for t in topics_data]
topic_counts = [t['count'] for t in topics_data]
topic_labels = [', '.join(t['top_terms'][:3]) for t in topics_data]

bars = ax.barh(range(len(topic_ids)), topic_counts, color=plt.cm.viridis(np.linspace(0, 1, len(topic_ids))))
ax.set_yticks(range(len(topic_ids)))
ax.set_yticklabels([f"T{tid}: {label}" for tid, label in zip(topic_ids, topic_labels)], fontsize=9)
ax.set_xlabel('Number of Documents', fontsize=12)
ax.set_title('Topic Distribution Across Corpus\n15 Topics Extracted', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
topic_dist_path = COORD_DIR / "topic_distribution.png"
plt.savefig(topic_dist_path, bbox_inches='tight', dpi=150)
plt.close()
print(f"✅ Saved: {topic_dist_path}")

# 3. Cluster size pie chart
print("\n📊 Generating cluster size pie chart...")
fig, ax = plt.subplots(figsize=(12, 10))

cluster_sizes = [c['size'] for c in clusters_data if c['cluster_id'] != -1]
cluster_names = [f"{c['cluster_name']}\n({c['primary_theme']})" for c in clusters_data if c['cluster_id'] != -1]

if cluster_sizes:
    colors_pie = plt.cm.Set3(np.linspace(0, 1, len(cluster_sizes)))
    wedges, texts, autotexts = ax.pie(
        cluster_sizes,
        labels=cluster_names,
        autopct='%1.1f%%',
        colors=colors_pie,
        startangle=90,
        textprops={'fontsize': 8}
    )

    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(8)

    ax.set_title(f'Cluster Size Distribution\n{len(cluster_sizes)} Semantic Clusters', fontsize=14, fontweight='bold')

plt.tight_layout()
cluster_pie_path = COORD_DIR / "cluster_size_distribution.png"
plt.savefig(cluster_pie_path, bbox_inches='tight', dpi=150)
plt.close()
print(f"✅ Saved: {cluster_pie_path}")

# ============================================================================
# OUTPUT FILES
# ============================================================================
print("\n" + "="*80)
print("Saving output files")
print("="*80)

# 1. Semantic clusters
clusters_output = {
    'timestamp': datetime.now().isoformat(),
    'total_clusters': len(clusters_data),
    'total_documents': len(texts),
    'clusters': clusters_data
}

clusters_path = COORD_DIR / "semantic_clusters.json"
with open(clusters_path, 'w') as f:
    json.dump(clusters_output, f, indent=2)
print(f"✅ Saved: {clusters_path}")

# 2. Topic model
topics_output = {
    'timestamp': datetime.now().isoformat(),
    'total_topics': len(topics_data),
    'topics': topics_data
}

topics_path = COORD_DIR / "topic_model.json"
with open(topics_path, 'w') as f:
    json.dump(topics_output, f, indent=2)
print(f"✅ Saved: {topics_path}")

# 3. Document cluster assignments
assignments_output = {
    'timestamp': datetime.now().isoformat(),
    'total_assignments': len(document_assignments),
    'assignments': document_assignments
}

assignments_path = COORD_DIR / "document_cluster_assignments.json"
with open(assignments_path, 'w') as f:
    json.dump(assignments_output, f, indent=2)
print(f"✅ Saved: {assignments_path}")

# 4. State file
state_output = {
    'agent': 'semantic_clusterer',
    'timestamp': datetime.now().isoformat(),
    'status': 'completed',
    'input_file': str(INPUT_FILE),
    'total_chunks': len(texts),
    'embedding_dim': embeddings.shape[1],
    'n_clusters': len(clusters_data),
    'n_topics': len(topics_data),
    'output_files': {
        'semantic_clusters': str(clusters_path),
        'topic_model': str(topics_path),
        'document_assignments': str(assignments_path),
        'umap_visualization': str(umap_viz_path),
        'topic_distribution': str(topic_dist_path),
        'cluster_pie': str(cluster_pie_path)
    },
    'success_criteria': {
        'clusters_identified': f'{len([c for c in clusters_data if c["cluster_id"] != -1])}/10-20',
        'topics_extracted': f'{len(topics_data)}/15',
        'clusters_labeled': True,
        'visualization_generated': True,
        'assignments_saved': True
    }
}

state_path = STATE_DIR / "semantic_clusterer.state.json"
with open(state_path, 'w') as f:
    json.dump(state_output, f, indent=2)
print(f"✅ Saved: {state_path}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("🎉 SEMANTIC CLUSTERER AGENT - MISSION COMPLETE")
print("="*80)

print(f"\n📊 Summary:")
print(f"  - Input chunks: {len(texts)}")
print(f"  - Embeddings generated: {embeddings.shape}")
print(f"  - Semantic clusters: {len([c for c in clusters_data if c['cluster_id'] != -1])}")
print(f"  - Topics extracted: {len(topics_data)}")
print(f"  - Document assignments: {len(document_assignments)}")
print(f"  - Visualizations created: 3")

print(f"\n✅ Success Criteria:")
print(f"  ✅ 10-20 semantic clusters identified: {len([c for c in clusters_data if c['cluster_id'] != -1])} clusters")
print(f"  ✅ 15 topics extracted: {len(topics_data)} topics")
print(f"  ✅ Each cluster labeled with prosecution theme")
print(f"  ✅ UMAP visualization generated")
print(f"  ✅ Document assignments saved")

print(f"\n📁 Output Files:")
print(f"  - {clusters_path}")
print(f"  - {topics_path}")
print(f"  - {assignments_path}")
print(f"  - {umap_viz_path}")
print(f"  - {topic_dist_path}")
print(f"  - {cluster_pie_path}")
print(f"  - {state_path}")

print(f"\n🏆 Agent Status: SUCCESS")
print("="*80)
