#!/usr/bin/env python3
"""
Entity Network Graph Builder for RICO Evidence Processing
Builds network graph from 8,228 entities with co-mention analysis.
"""

import pandas as pd
import networkx as nx
import json
from pathlib import Path
from collections import defaultdict
import pickle

# Paths
BASE_DIR = Path("/Users/breydentaylor/certainly")
DATA_DIR = BASE_DIR / "noteworthy-raw"
OUTPUT_DIR = BASE_DIR / "visualizations"

PEOPLE_PLACES_CSV = DATA_DIR / "people_and_places.csv"
ENTITIES_CSV = DATA_DIR / "entities_extracted.csv"

# Output files
GRAPH_PICKLE = OUTPUT_DIR / "entity_network.gpickle"
NODES_CSV = OUTPUT_DIR / "entity_nodes.csv"
EDGES_CSV = OUTPUT_DIR / "entity_edges.csv"
STATS_JSON = OUTPUT_DIR / "entity_network_stats.json"


def load_data():
    """Load both CSV files into pandas DataFrames."""
    print("Loading data...")

    # Load people and places (type, name, mentions, sources)
    df_people = pd.read_csv(PEOPLE_PLACES_CSV)
    print(f"Loaded {len(df_people)} people/places entities")

    # Load extracted entities (type, value, mentions, sources)
    df_entities = pd.read_csv(ENTITIES_CSV)
    print(f"Loaded {len(df_entities)} extracted entities")

    # Standardize column names - rename 'value' to 'name' for entities
    if 'value' in df_entities.columns:
        df_entities = df_entities.rename(columns={'value': 'name'})

    return df_people, df_entities


def parse_sources(sources_str):
    """Parse semicolon-separated sources string into list."""
    if pd.isna(sources_str):
        return []
    return [s.strip() for s in str(sources_str).split(';') if s.strip()]


def build_graph(df_people, df_entities):
    """Build NetworkX graph with all entities as nodes."""
    print("\nBuilding graph...")
    G = nx.Graph()

    # Track entities by source for co-mention analysis
    source_entities = defaultdict(list)

    # Process people/places entities
    for idx, row in df_people.iterrows():
        entity_id = f"pp_{idx}"
        entity_name = row['name']
        entity_type = row['type']
        mentions = int(row['mentions'])
        sources = parse_sources(row['sources'])

        # Add node with attributes
        G.add_node(
            entity_id,
            label=entity_name,
            type=entity_type,
            mentions=mentions,
            importance=mentions,
            source_dataset='people_and_places'
        )

        # Track for co-mention edges
        for source in sources:
            source_entities[source].append(entity_id)

    # Process extracted entities
    for idx, row in df_entities.iterrows():
        entity_id = f"ee_{idx}"
        entity_name = row['name']
        entity_type = row['type']
        mentions = int(row['mentions'])
        sources = parse_sources(row['sources'])

        # Add node with attributes
        G.add_node(
            entity_id,
            label=entity_name,
            type=entity_type,
            mentions=mentions,
            importance=mentions,
            source_dataset='entities_extracted'
        )

        # Track for co-mention edges
        for source in sources:
            source_entities[source].append(entity_id)

    print(f"Added {G.number_of_nodes()} nodes")

    # Build co-mention edges
    print("Building co-mention edges...")
    edge_weights = defaultdict(lambda: {'weight': 0, 'shared_sources': set()})

    total_sources = len(source_entities)
    source_count = 0

    for source, entities in source_entities.items():
        source_count += 1
        if source_count % 100 == 0:
            print(f"  Processing source {source_count}/{total_sources}...")

        # Create edges between all entities mentioned in the same source
        # Limit to first 100 entities per source to avoid explosion
        entities_subset = entities[:100] if len(entities) > 100 else entities

        for i in range(len(entities_subset)):
            for j in range(i + 1, len(entities_subset)):
                entity1, entity2 = entities_subset[i], entities_subset[j]
                # Use sorted tuple as key to avoid duplicates
                edge_key = tuple(sorted([entity1, entity2]))
                edge_weights[edge_key]['weight'] += 1
                edge_weights[edge_key]['shared_sources'].add(source)

    # Add edges to graph
    for (source, target), data in edge_weights.items():
        G.add_edge(
            source,
            target,
            weight=data['weight'],
            relationship='co-mentioned',
            shared_sources_count=len(data['shared_sources']),
            shared_sources=list(data['shared_sources'])
        )

    print(f"Added {G.number_of_edges()} edges")

    return G


def detect_communities(G):
    """Use Label Propagation for community detection."""
    print("\nDetecting communities with Label Propagation...")

    # Label Propagation is fast and works well for large graphs
    communities = nx.community.label_propagation_communities(G)

    # Assign community IDs to nodes
    community_map = {}
    for comm_id, community in enumerate(communities):
        for node in community:
            community_map[node] = comm_id

    # Add community attribute to nodes
    nx.set_node_attributes(G, community_map, 'community')

    num_communities = len(list(communities))
    print(f"Found {num_communities} communities")

    return num_communities


def calculate_centrality(G):
    """Calculate degree and betweenness centrality."""
    print("\nCalculating centrality metrics...")

    # Degree centrality (fast)
    degree_centrality = nx.degree_centrality(G)
    nx.set_node_attributes(G, degree_centrality, 'degree_centrality')
    print("✓ Degree centrality calculated")

    # Betweenness centrality - use approximate version for speed
    # For large graphs with many edges, exact betweenness is too slow
    # Use k=500 for sampling approximation
    print("  Computing approximate betweenness centrality (sampling 500 nodes)...")
    betweenness_centrality = nx.betweenness_centrality(G, k=500, normalized=True)
    nx.set_node_attributes(G, betweenness_centrality, 'betweenness_centrality')
    print("✓ Approximate betweenness centrality calculated")


def save_outputs(G):
    """Generate and save all output files."""
    print("\nSaving outputs...")

    # 1. Save graph as pickle
    with open(GRAPH_PICKLE, 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
    print(f"✓ Saved graph: {GRAPH_PICKLE}")

    # 2. Save nodes CSV
    nodes_data = []
    for node, attrs in G.nodes(data=True):
        nodes_data.append({
            'id': node,
            'label': attrs.get('label', ''),
            'type': attrs.get('type', ''),
            'mentions': attrs.get('mentions', 0),
            'community': attrs.get('community', -1),
            'degree_centrality': attrs.get('degree_centrality', 0),
            'betweenness_centrality': attrs.get('betweenness_centrality', 0)
        })

    df_nodes = pd.DataFrame(nodes_data)
    df_nodes.to_csv(NODES_CSV, index=False)
    print(f"✓ Saved nodes: {NODES_CSV} ({len(df_nodes)} nodes)")

    # 3. Save edges CSV
    edges_data = []
    for source, target, attrs in G.edges(data=True):
        edges_data.append({
            'source': source,
            'target': target,
            'weight': attrs.get('weight', 1),
            'relationship': attrs.get('relationship', 'co-mentioned'),
            'shared_sources_count': attrs.get('shared_sources_count', 1)
        })

    df_edges = pd.DataFrame(edges_data)
    df_edges.to_csv(EDGES_CSV, index=False)
    print(f"✓ Saved edges: {EDGES_CSV} ({len(df_edges)} edges)")

    # 4. Generate statistics
    df_nodes_sorted = df_nodes.sort_values('degree_centrality', ascending=False)
    top_10_degree = df_nodes_sorted.head(10)[['label', 'type', 'mentions', 'degree_centrality']].to_dict('records')

    df_nodes_sorted = df_nodes.sort_values('betweenness_centrality', ascending=False)
    top_10_betweenness = df_nodes_sorted.head(10)[['label', 'type', 'mentions', 'betweenness_centrality']].to_dict('records')

    stats = {
        'total_nodes': G.number_of_nodes(),
        'total_edges': G.number_of_edges(),
        'density': nx.density(G),
        'communities_count': len(set(nx.get_node_attributes(G, 'community').values())),
        'top_10_by_degree': top_10_degree,
        'top_10_by_betweenness': top_10_betweenness,
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
        'graph_diameter': 'N/A (too large to compute efficiently)',
        'largest_component_size': len(max(nx.connected_components(G), key=len))
    }

    with open(STATS_JSON, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Saved stats: {STATS_JSON}")

    return stats


def main():
    """Main execution flow."""
    print("=" * 70)
    print("ENTITY NETWORK GRAPH BUILDER")
    print("=" * 70)

    # Load data
    df_people, df_entities = load_data()

    # Build graph
    G = build_graph(df_people, df_entities)

    # Detect communities
    detect_communities(G)

    # Calculate centrality
    calculate_centrality(G)

    # Save outputs
    stats = save_outputs(G)

    # Print summary
    print("\n" + "=" * 70)
    print("NETWORK STATS SUMMARY")
    print("=" * 70)
    print(f"Total Nodes: {stats['total_nodes']:,}")
    print(f"Total Edges: {stats['total_edges']:,}")
    print(f"Communities: {stats['communities_count']}")
    print(f"Average Degree: {stats['avg_degree']:.2f}")
    print(f"Network Density: {stats['density']:.6f}")
    print(f"Largest Component: {stats['largest_component_size']:,} nodes")

    print("\n" + "-" * 70)
    print("TOP 10 ENTITIES BY DEGREE CENTRALITY")
    print("-" * 70)
    for i, entity in enumerate(stats['top_10_by_degree'], 1):
        print(f"{i:2d}. {entity['label']:<40} ({entity['type']:<15}) "
              f"Mentions: {entity['mentions']:>5}  Degree: {entity['degree_centrality']:.4f}")

    print("\n" + "-" * 70)
    print("TOP 10 ENTITIES BY BETWEENNESS CENTRALITY")
    print("-" * 70)
    for i, entity in enumerate(stats['top_10_by_betweenness'], 1):
        print(f"{i:2d}. {entity['label']:<40} ({entity['type']:<15}) "
              f"Mentions: {entity['mentions']:>5}  Between: {entity['betweenness_centrality']:.4f}")

    print("\n" + "=" * 70)
    print("FILE CREATION CONFIRMED")
    print("=" * 70)
    print(f"✓ {GRAPH_PICKLE}")
    print(f"✓ {NODES_CSV}")
    print(f"✓ {EDGES_CSV}")
    print(f"✓ {STATS_JSON}")
    print("=" * 70)


if __name__ == "__main__":
    main()
