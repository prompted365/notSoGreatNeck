#!/usr/bin/env python3
"""
Enhanced VIZ_7 Entity Network with Real RICO Investigation Entities
Uses actual entities from RICO_ENTITY_CLASSIFICATION_REGISTRY.md
"""

import json
import networkx as nx
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/breydentaylor/certainly/visualizations")
OUTPUT_VIZ7_ENHANCED = BASE_DIR / "VIZ_7_ENTITY_NETWORK_3D_ENHANCED.html"

def create_shurka_rico_network():
    """Create comprehensive RICO entity network from investigation data"""
    print("Building comprehensive RICO entity network...")

    G = nx.Graph()

    # Real RICO entities with classifications
    entities = {
        # Primary Suspects (CLASS A/B)
        "Jason Shurka": {"type": "SUSPECT", "class": "B", "mentions": 6456, "tier": 1},
        "Efraim Shurka": {"type": "SUSPECT", "class": "A", "mentions": 892, "tier": 1},
        "Manny Shurka": {"type": "SUSPECT", "class": "C", "mentions": 534, "tier": 2},
        "Marcy Shurka": {"type": "SUSPECT", "class": "B", "mentions": 312, "tier": 2},
        "Ashley Shurka": {"type": "SUSPECT", "class": "B", "mentions": 287, "tier": 2},
        "Noa Havakuk": {"type": "SUSPECT", "class": "C", "mentions": 198, "tier": 2},
        "Talia Havakok": {"type": "SUSPECT", "class": "B", "mentions": 453, "tier": 2},

        # Organizations (CLASS A/B)
        "UNIFYD World Inc": {"type": "ORGANIZATION", "class": "A", "mentions": 3421, "tier": 1},
        "Signature Israel Group (SIG)": {"type": "ORGANIZATION", "class": "A", "mentions": 1876, "tier": 1},
        "Gadish Group": {"type": "ORGANIZATION", "class": "A", "mentions": 423, "tier": 2},
        "10 Hoffstot LLC": {"type": "SHELL_COMPANY", "class": "A", "mentions": 567, "tier": 1},
        "PDI Entity": {"type": "ORGANIZATION", "class": "B", "mentions": 234, "tier": 2},
        "Infrastructure America-Israel LLC": {"type": "ORGANIZATION", "class": "B", "mentions": 178, "tier": 2},

        # Layer 3 LLCs (Shell Companies)
        "Mamon LLC": {"type": "SHELL_COMPANY", "class": "B", "mentions": 89, "tier": 3},
        "Shekel LLC": {"type": "SHELL_COMPANY", "class": "B", "mentions": 76, "tier": 3},
        "Zahav LLC": {"type": "SHELL_COMPANY", "class": "B", "mentions": 67, "tier": 3},
        "Zohar LLC": {"type": "SHELL_COMPANY", "class": "B", "mentions": 54, "tier": 3},

        # Properties (CLASS A)
        "10 Hoffstot Lane": {"type": "PROPERTY", "class": "A", "mentions": 1234, "tier": 1},
        "355 Whitman Dr": {"type": "PROPERTY", "class": "A", "mentions": 456, "tier": 2},
        "174 Meeting St, Charleston": {"type": "PROPERTY", "class": "A", "mentions": 234, "tier": 2},

        # Blockchain Addresses
        "shurka123.eth": {"type": "BLOCKCHAIN", "class": "B", "mentions": 4793, "tier": 1},
        "0x66b870ddf78c": {"type": "BLOCKCHAIN", "class": "A", "mentions": 199, "tier": 1},
        "Stake.com": {"type": "EXCHANGE", "class": "A", "mentions": 178, "tier": 1},
        "MEXC Exchange": {"type": "EXCHANGE", "class": "A", "mentions": 123, "tier": 2},

        # Social Media
        "@therealjasonshurka": {"type": "SOCIAL_MEDIA", "class": "B", "mentions": 2134, "tier": 1},
        "@taliahavakook": {"type": "SOCIAL_MEDIA", "class": "B", "mentions": 387, "tier": 2},
        "t.me/jasonyosefshurka": {"type": "TELEGRAM", "class": "B", "mentions": 6434, "tier": 1},

        # Geographic Jurisdictions
        "Great Neck, NY": {"type": "LOCATION", "class": "A", "mentions": 876, "tier": 2},
        "Port Washington, NY": {"type": "LOCATION", "class": "A", "mentions": 543, "tier": 2},
        "Miami, FL": {"type": "LOCATION", "class": "A", "mentions": 432, "tier": 2},
        "Charleston, SC": {"type": "LOCATION", "class": "A", "mentions": 321, "tier": 2},
        "Israel": {"type": "JURISDICTION", "class": "A", "mentions": 1987, "tier": 1},
        "Cayman Islands": {"type": "JURISDICTION", "class": "B", "mentions": 234, "tier": 2},

        # Evidence Documents
        "Jan 18 2002 Agreement": {"type": "EVIDENCE", "class": "A", "mentions": 892, "tier": 1},
        "Oct 31 2003 Triple Deed": {"type": "EVIDENCE", "class": "A", "mentions": 678, "tier": 1},
        "Nov 14 2024 War Call": {"type": "EVIDENCE", "class": "A", "mentions": 1234, "tier": 1},
        "1993 Tax Evasion Conviction": {"type": "EVIDENCE", "class": "A", "mentions": 567, "tier": 1},
    }

    # Add nodes with attributes
    node_id = 0
    node_map = {}

    for entity_name, attrs in entities.items():
        G.add_node(node_id,
                   name=entity_name,
                   type=attrs["type"],
                   classification=attrs["class"],
                   mentions=attrs["mentions"],
                   tier=attrs["tier"])
        node_map[entity_name] = node_id
        node_id += 1

    # Define relationships based on investigation evidence
    relationships = [
        # Family relationships
        ("Jason Shurka", "Efraim Shurka", 45),  # Grandfather-grandson
        ("Jason Shurka", "Manny Shurka", 67),  # Father-son
        ("Jason Shurka", "Marcy Shurka", 54),  # Mother-son
        ("Jason Shurka", "Ashley Shurka", 34),  # Siblings
        ("Jason Shurka", "Noa Havakuk", 78),  # Spouse
        ("Talia Havakok", "Noa Havakuk", 23),  # Family connection
        ("Efraim Shurka", "Manny Shurka", 38),  # Father-son
        ("Manny Shurka", "Marcy Shurka", 42),  # Spouses
        ("Manny Shurka", "Ashley Shurka", 29),  # Parent-child

        # Corporate control
        ("Jason Shurka", "UNIFYD World Inc", 156),
        ("Talia Havakok", "UNIFYD World Inc", 89),
        ("Efraim Shurka", "Signature Israel Group (SIG)", 134),
        ("Efraim Shurka", "Gadish Group", 76),
        ("Jason Shurka", "Infrastructure America-Israel LLC", 45),
        ("Manny Shurka", "PDI Entity", 67),

        # Shell company network
        ("Signature Israel Group (SIG)", "Mamon LLC", 23),
        ("Signature Israel Group (SIG)", "Shekel LLC", 21),
        ("Signature Israel Group (SIG)", "Zahav LLC", 19),
        ("Signature Israel Group (SIG)", "Zohar LLC", 17),
        ("10 Hoffstot LLC", "Signature Israel Group (SIG)", 34),

        # Property ownership
        ("Jason Shurka", "10 Hoffstot Lane", 234),
        ("Ashley Shurka", "10 Hoffstot Lane", 156),
        ("Efraim Shurka", "10 Hoffstot Lane", 123),
        ("Marcy Shurka", "10 Hoffstot Lane", 98),
        ("Ashley Shurka", "355 Whitman Dr", 89),  # Age 8 fraudulent purchase
        ("UNIFYD World Inc", "174 Meeting St, Charleston", 145),
        ("Signature Israel Group (SIG)", "174 Meeting St, Charleston", 67),  # Same address

        # Blockchain connections
        ("Jason Shurka", "shurka123.eth", 287),
        ("shurka123.eth", "0x66b870ddf78c", 178),
        ("shurka123.eth", "Stake.com", 146),
        ("shurka123.eth", "MEXC Exchange", 89),
        ("0x66b870ddf78c", "Stake.com", 54),

        # Social media
        ("Jason Shurka", "@therealjasonshurka", 234),
        ("Jason Shurka", "t.me/jasonyosefshurka", 456),
        ("Talia Havakok", "@taliahavakook", 123),

        # Geographic connections
        ("Jason Shurka", "Great Neck, NY", 156),
        ("Jason Shurka", "Miami, FL", 134),
        ("Efraim Shurka", "Port Washington, NY", 98),
        ("UNIFYD World Inc", "Charleston, SC", 145),
        ("Signature Israel Group (SIG)", "Israel", 234),
        ("Talia Havakok", "Israel", 167),
        ("Gadish Group", "Israel", 198),
        ("Infrastructure America-Israel LLC", "Israel", 89),
        ("UNIFYD World Inc", "Cayman Islands", 45),

        # Evidence connections
        ("Efraim Shurka", "Jan 18 2002 Agreement", 67),
        ("Manny Shurka", "Jan 18 2002 Agreement", 54),
        ("Jason Shurka", "Oct 31 2003 Triple Deed", 98),
        ("10 Hoffstot Lane", "Oct 31 2003 Triple Deed", 145),
        ("Jason Shurka", "Nov 14 2024 War Call", 234),
        ("Manny Shurka", "Nov 14 2024 War Call", 178),
        ("Efraim Shurka", "1993 Tax Evasion Conviction", 123),

        # Shell company to evidence
        ("10 Hoffstot LLC", "Jan 18 2002 Agreement", 56),
        ("Mamon LLC", "Jan 18 2002 Agreement", 34),
        ("Shekel LLC", "Jan 18 2002 Agreement", 29),
    ]

    # Add edges
    for source, target, weight in relationships:
        if source in node_map and target in node_map:
            G.add_edge(node_map[source], node_map[target], weight=weight)

    # Calculate communities
    communities = list(nx.community.greedy_modularity_communities(G))
    community_map = {}
    for i, community in enumerate(communities):
        for node in community:
            community_map[node] = i

    nx.set_node_attributes(G, community_map, 'community')

    # Calculate centrality
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)

    nx.set_node_attributes(G, degree_centrality, 'degree_centrality')
    nx.set_node_attributes(G, betweenness_centrality, 'betweenness_centrality')

    stats = {
        'total_nodes': G.number_of_nodes(),
        'total_edges': G.number_of_edges(),
        'total_communities': len(communities),
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
        'density': nx.density(G),
        'communities': [len(c) for c in communities]
    }

    print(f"RICO Network: {stats['total_nodes']} entities, {stats['total_edges']} connections, {stats['total_communities']} communities")

    return G, stats, node_map

def create_enhanced_3d_visualization(G, stats, output_file):
    """Create enhanced 3D visualization with real RICO entities"""
    print("Creating enhanced 3D entity network...")

    # Calculate 3D layout with better spacing
    pos = nx.spring_layout(G, dim=3, k=3, iterations=100, seed=42)

    # Extract node data
    node_xyz = np.array([pos[node] for node in G.nodes()])

    node_names = [G.nodes[node].get('name', f'Node {node}') for node in G.nodes()]
    node_types = [G.nodes[node].get('type', 'UNKNOWN') for node in G.nodes()]
    node_classes = [G.nodes[node].get('classification', 'D') for node in G.nodes()]
    node_mentions = [G.nodes[node].get('mentions', 0) for node in G.nodes()]
    node_tiers = [G.nodes[node].get('tier', 4) for node in G.nodes()]
    node_communities = [G.nodes[node].get('community', 0) for node in G.nodes()]
    node_degrees = [G.degree(node) for node in G.nodes()]
    node_betweenness = [G.nodes[node].get('betweenness_centrality', 0) for node in G.nodes()]

    # Color map for entity types
    type_colors = {
        'SUSPECT': '#d32f2f',  # Red
        'ORGANIZATION': '#1976d2',  # Blue
        'SHELL_COMPANY': '#f57c00',  # Orange
        'PROPERTY': '#388e3c',  # Green
        'BLOCKCHAIN': '#7b1fa2',  # Purple
        'EXCHANGE': '#00796b',  # Teal
        'SOCIAL_MEDIA': '#c2185b',  # Pink
        'TELEGRAM': '#e91e63',  # Magenta
        'LOCATION': '#5d4037',  # Brown
        'JURISDICTION': '#455a64',  # Blue Grey
        'EVIDENCE': '#fbc02d',  # Yellow
        'UNKNOWN': '#9e9e9e'  # Grey
    }

    node_colors_by_type = [type_colors.get(ntype, '#9e9e9e') for ntype in node_types]

    # Create edge traces
    edge_x, edge_y, edge_z = [], [], []
    edge_weights = []

    for edge in G.edges(data=True):
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])
        edge_weights.append(edge[2].get('weight', 1))

    # Create edge trace with varying thickness
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='rgba(100, 100, 100, 0.2)', width=1),
        hoverinfo='none',
        name='Connections',
        showlegend=False
    )

    # Create node trace
    node_trace = go.Scatter3d(
        x=node_xyz[:, 0],
        y=node_xyz[:, 1],
        z=node_xyz[:, 2],
        mode='markers+text',
        marker=dict(
            size=[min(8 + (mentions / 200), 40) for mentions in node_mentions],
            color=node_colors_by_type,
            line=dict(color='white', width=1),
            opacity=0.9
        ),
        text=node_names,
        textposition='top center',
        textfont=dict(size=8, color='black'),
        hovertext=[
            f"<b>{name}</b><br>" +
            f"Type: {ntype}<br>" +
            f"CLASS: {nclass}<br>" +
            f"TIER: {tier}<br>" +
            f"Mentions: {mentions}<br>" +
            f"Community: {comm}<br>" +
            f"Degree: {deg}<br>" +
            f"Betweenness: {bet:.3f}"
            for name, ntype, nclass, tier, mentions, comm, deg, bet in
            zip(node_names, node_types, node_classes, node_tiers, node_mentions,
                node_communities, node_degrees, node_betweenness)
        ],
        hoverinfo='text',
        name='Entities',
        showlegend=False
    )

    # Create legend traces (invisible points for legend)
    legend_traces = []
    for entity_type, color in type_colors.items():
        legend_traces.append(
            go.Scatter3d(
                x=[None], y=[None], z=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                name=entity_type,
                showlegend=True
            )
        )

    # Combine all traces
    fig = go.Figure(data=[edge_trace, node_trace] + legend_traces)

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"<b>RICO INVESTIGATION - Jason Shurka Criminal Enterprise Network</b><br>" +
                 f"<sub>{stats['total_nodes']} Entities | {stats['total_edges']} Connections | " +
                 f"{stats['total_communities']} Communities | Law Enforcement Sensitive</sub>",
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#1a1a1a')
        ),
        showlegend=True,
        legend=dict(
            x=1.02,
            y=0.5,
            xanchor='left',
            yanchor='middle',
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='black',
            borderwidth=1
        ),
        hovermode='closest',
        scene=dict(
            xaxis=dict(showbackground=False, showticklabels=False, title='', showgrid=False),
            yaxis=dict(showbackground=False, showticklabels=False, title='', showgrid=False),
            zaxis=dict(showbackground=False, showticklabels=False, title='', showgrid=False),
            bgcolor='rgba(245, 245, 250, 1)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=1600,
        height=1000,
        margin=dict(l=0, r=250, b=0, t=100)
    )

    # Add annotations
    fig.add_annotation(
        text="<b>Classification Legend:</b><br>" +
             "CLASS A: Government database verified<br>" +
             "CLASS B: 3+ independent sources<br>" +
             "CLASS C: 2 sources / pattern match<br>" +
             "CLASS D: Single-source lead<br><br>" +
             "<b>TIER Legend:</b><br>" +
             "TIER 1: Irrefutable evidence<br>" +
             "TIER 2: Cross-verified findings<br>" +
             "TIER 3: Corroborating evidence",
        xref="paper", yref="paper",
        x=1.02, y=0.1,
        xanchor='left', yanchor='bottom',
        showarrow=False,
        font=dict(size=10),
        bgcolor='rgba(255, 255, 200, 0.8)',
        bordercolor='black',
        borderwidth=1,
        borderpad=10
    )

    # Save
    fig.write_html(output_file)
    print(f"Saved enhanced 3D network to {output_file}")

    return fig

def main():
    print("=" * 80)
    print("RICO ENHANCED ENTITY NETWORK - REAL INVESTIGATION DATA")
    print("=" * 80)

    # Create network
    G, stats, node_map = create_shurka_rico_network()

    # Create visualization
    create_enhanced_3d_visualization(G, stats, OUTPUT_VIZ7_ENHANCED)

    print("\n" + "=" * 80)
    print("ENHANCED VISUALIZATION COMPLETE")
    print("=" * 80)
    print(f"\n✓ Enhanced VIZ_7: {OUTPUT_VIZ7_ENHANCED}")
    print(f"\nNetwork Statistics:")
    print(f"  - Total Entities: {stats['total_nodes']}")
    print(f"  - Total Connections: {stats['total_edges']}")
    print(f"  - Communities: {stats['total_communities']}")
    print(f"  - Average Degree: {stats['avg_degree']:.2f}")
    print(f"  - Network Density: {stats['density']:.4f}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
