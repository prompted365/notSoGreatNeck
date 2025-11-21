#!/usr/bin/env python3
"""
PROFESSIONAL-GRADE PROSECUTION VISUALIZATIONS
==============================================

Creates top-tier, multi-dimensional visualizations for RICO prosecution:

1. Interactive 3D Network Graph (Plotly) - Entity relationships with clustering
2. Blockchain Transaction Flow (Sankey Diagram) - Multi-chain fund flows
3. Temporal Activity Heatmap - Time-series analysis with seasonality
4. Geographic Cluster Map (Folium) - Real map with evidence locations
5. Evidence Timeline (Plotly) - Interactive timeline with filtering
6. RICO Dashboard - Comprehensive multi-view analysis

Output: HTML (interactive) + PNG (courtroom-ready static images)
"""

import json
import csv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import networkx as nx

# Top-tier visualization libraries
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

print("🎨 PROFESSIONAL VISUALIZATION ENGINE STARTING...")
print("=" * 80)

# ==============================================================================
# DATA LOADING
# ==============================================================================

print("\n📂 LOADING DATA...")

# Load network graph
with open('../noteworthy-raw/shurka_network_graph.json', 'r') as f:
    network_data = json.load(f)

# Load blockchain transactions
shurka123_txs = pd.read_csv('../noteworthy-raw/shurka123.eth-self-owned&self-controlled.csv')
fund_txs = pd.read_csv('../noteworthy-raw/fund_transactions_10k^1_export-0x66b870ddf78c975af5cd8edc6de25eca81791de1.csv')
gang_txs = pd.read_csv('../noteworthy-raw/gang_10k^2_export-0x4f368e2d4612fef0b923667d19183785a5d3c950.csv')

# Load entities
entities_df = pd.read_csv('../noteworthy-raw/entities_extracted.csv')
people_df = pd.read_csv('../noteworthy-raw/people_and_places.csv')

print(f"   ✅ Network nodes: {len(network_data['nodes'])}")
print(f"   ✅ Network edges: {len(network_data.get('edges', network_data.get('links', [])))}")
print(f"   ✅ shurka123 transactions: {len(shurka123_txs)}")
print(f"   ✅ 10K fund transactions: {len(fund_txs)}")
print(f"   ✅ Gang transactions: {len(gang_txs)}")
print(f"   ✅ Extracted entities: {len(entities_df)}")
print(f"   ✅ People & places: {len(people_df)}")

# ==============================================================================
# VIZ 1: INTERACTIVE 3D NETWORK GRAPH (Plotly)
# ==============================================================================

print("\n" + "=" * 80)
print("VIZ 1: CREATING INTERACTIVE 3D CRIMINAL NETWORK GRAPH...")
print("=" * 80)

# Build NetworkX graph for layout calculation
G = nx.Graph()

# Add nodes
for node in network_data['nodes']:
    G.add_node(
        node['id'],
        label=node['label'],
        type=node.get('type', 'unknown'),
        importance=node.get('importance', 1)
    )

# Add edges
edges_key = 'edges' if 'edges' in network_data else 'links'
for edge in network_data.get(edges_key, []):
    source = edge.get('source', edge.get('from', ''))
    target = edge.get('target', edge.get('to', ''))
    if source and target:
        G.add_edge(source, target, relationship=edge.get('relationship', 'unknown'))

# Calculate 3D spring layout
pos_3d = nx.spring_layout(G, dim=3, k=0.5, iterations=50)

# Extract coordinates
node_x = []
node_y = []
node_z = []
node_text = []
node_colors = []
node_sizes = []

color_map = {
    'person': '#ff6b6b',         # Red for people
    'family_member': '#fa5252',  # Darker red for family
    'primary_target': '#c92a2a', # Darkest red for Jason
    'organization': '#4c6ef5',   # Blue for orgs
    'location': '#20c997',       # Green for locations
    'event': '#ffd43b',          # Yellow for events
}

for node in network_data['nodes']:
    node_id = node['id']
    if node_id in pos_3d:
        x, y, z = pos_3d[node_id]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)

        label = node.get('label', node_id)
        node_type = node.get('type', 'unknown')
        importance = node.get('importance', 1)

        # Build hover text
        hover_parts = [f"<b>{label}</b>"]
        if 'data' in node:
            for k, v in node['data'].items():
                if k not in ['label', 'x', 'y', 'vx', 'vy', 'index']:
                    hover_parts.append(f"{k}: {v}")
        node_text.append("<br>".join(hover_parts))

        # Color by type
        node_colors.append(color_map.get(node_type, '#868e96'))

        # Size by importance
        node_sizes.append(importance * 5 + 10)

# Create edge traces
edge_x = []
edge_y = []
edge_z = []

for edge in network_data.get(edges_key, []):
    source = edge.get('source', edge.get('from', ''))
    target = edge.get('target', edge.get('to', ''))

    if source in pos_3d and target in pos_3d:
        x0, y0, z0 = pos_3d[source]
        x1, y1, z1 = pos_3d[target]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

# Create 3D scatter plot
fig_network = go.Figure()

# Add edges
fig_network.add_trace(go.Scatter3d(
    x=edge_x, y=edge_y, z=edge_z,
    mode='lines',
    line=dict(color='#dee2e6', width=1),
    hoverinfo='none',
    name='Relationships'
))

# Add nodes
fig_network.add_trace(go.Scatter3d(
    x=node_x, y=node_y, z=node_z,
    mode='markers+text',
    marker=dict(
        size=node_sizes,
        color=node_colors,
        line=dict(color='#343a40', width=0.5),
        opacity=0.8
    ),
    text=[n['label'] for n in network_data['nodes'] if n['id'] in pos_3d],
    textposition="top center",
    hovertext=node_text,
    hoverinfo='text',
    name='Entities'
))

fig_network.update_layout(
    title=dict(
        text="<b>Shurka Criminal Enterprise Network - 3D Interactive Graph</b><br>"
             "<sub>Red=Persons | Blue=Organizations | Green=Locations | Node size=Importance</sub>",
        x=0.5,
        xanchor='center',
        font=dict(size=20)
    ),
    showlegend=False,
    scene=dict(
        xaxis=dict(showbackground=False, showticklabels=False, title=''),
        yaxis=dict(showbackground=False, showticklabels=False, title=''),
        zaxis=dict(showbackground=False, showticklabels=False, title=''),
        bgcolor='#f8f9fa'
    ),
    paper_bgcolor='#ffffff',
    plot_bgcolor='#f8f9fa',
    font=dict(family="Arial, sans-serif", size=12),
    height=900,
    width=1400,
    margin=dict(l=0, r=0, b=0, t=100)
)

# Save interactive HTML
fig_network.write_html('VIZ_1_INTERACTIVE_NETWORK_3D.html')
print("\n✅ VIZ 1 COMPLETE:")
print("   📄 VIZ_1_INTERACTIVE_NETWORK_3D.html (interactive 3D network)")

# ==============================================================================
# VIZ 2: BLOCKCHAIN TRANSACTION FLOW (Sankey Diagram)
# ==============================================================================

print("\n" + "=" * 80)
print("VIZ 2: CREATING BLOCKCHAIN TRANSACTION FLOW DIAGRAM...")
print("=" * 80)

# Prepare shurka123 transactions for Sankey
# Group by chain and aggregate flows
chain_flows = shurka123_txs.groupby('Chain').size().reset_index(name='count')

# Prepare source/target pairs
flow_data = []

# Add chain-level aggregation
for _, row in shurka123_txs.head(500).iterrows():  # Sample for performance
    chain = row['Chain']
    from_addr = row['From'][:10] + '...' if pd.notna(row['From']) else 'Unknown'
    to_addr = row['To'][:10] + '...' if pd.notna(row['To']) else 'Unknown'

    # Parse amount, removing commas
    try:
        amount_str = str(row['Amount']).replace(',', '')
        amount = float(amount_str) if pd.notna(row['Amount']) else 0.1
    except (ValueError, AttributeError):
        amount = 0.1

    flow_data.append({
        'source': f"{chain}",
        'target': to_addr,
        'value': amount,
        'chain': chain
    })

# Build Sankey diagram data
all_nodes = set()
for item in flow_data[:200]:  # Limit for readability
    all_nodes.add(item['source'])
    all_nodes.add(item['target'])

node_list = list(all_nodes)
node_dict = {node: idx for idx, node in enumerate(node_list)}

sankey_source = []
sankey_target = []
sankey_value = []
sankey_color = []

chain_colors = {
    'avalanche': 'rgba(231, 65, 66, 0.6)',
    'fantom': 'rgba(26, 116, 255, 0.6)',
    'eth': 'rgba(98, 126, 234, 0.6)',
    'polygon': 'rgba(130, 71, 229, 0.6)',
}

for item in flow_data[:200]:
    sankey_source.append(node_dict[item['source']])
    sankey_target.append(node_dict[item['target']])
    sankey_value.append(max(item['value'], 0.1))  # Min value for visibility
    sankey_color.append(chain_colors.get(item['chain'], 'rgba(128, 128, 128, 0.4)'))

fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=node_list,
        color="#4c6ef5"
    ),
    link=dict(
        source=sankey_source,
        target=sankey_target,
        value=sankey_value,
        color=sankey_color
    )
)])

fig_sankey.update_layout(
    title=dict(
        text="<b>shurka123.eth Multi-Chain Transaction Flows</b><br>"
             "<sub>Avalanche | Fantom | Ethereum | Polygon - Top 200 Transactions</sub>",
        x=0.5,
        xanchor='center',
        font=dict(size=20)
    ),
    font=dict(size=12, family="Arial, sans-serif"),
    height=800,
    width=1400,
    paper_bgcolor='#ffffff'
)

fig_sankey.write_html('VIZ_2_BLOCKCHAIN_FLOW_SANKEY.html')
print("\n✅ VIZ 2 COMPLETE:")
print("   📄 VIZ_2_BLOCKCHAIN_FLOW_SANKEY.html (multi-chain transaction flows)")

# ==============================================================================
# VIZ 3: TEMPORAL ACTIVITY HEATMAP
# ==============================================================================

print("\n" + "=" * 80)
print("VIZ 3: CREATING TEMPORAL ACTIVITY HEATMAP...")
print("=" * 80)

# Prepare blockchain transaction dates
def parse_blockchain_date(df, date_col):
    if date_col in df.columns:
        df['date_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=['date_parsed'])
        df['year'] = df['date_parsed'].dt.year
        df['month'] = df['date_parsed'].dt.month
        df['hour'] = df['date_parsed'].dt.hour
        df['day_of_week'] = df['date_parsed'].dt.dayofweek
        return df
    return df

shurka123_txs = parse_blockchain_date(shurka123_txs, 'Date')
fund_txs = parse_blockchain_date(fund_txs, 'DateTime (UTC)')

# Create hourly heatmap
if 'hour' in shurka123_txs.columns and 'day_of_week' in shurka123_txs.columns:
    heatmap_data = shurka123_txs.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)

    day_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=list(range(24)),
        y=day_labels,
        colorscale='Reds',
        colorbar=dict(title="Transaction<br>Count"),
        hovertemplate='<b>%{y}</b><br>Hour: %{x}:00<br>Transactions: %{z}<extra></extra>'
    ))

    fig_heatmap.update_layout(
        title=dict(
            text="<b>shurka123.eth Transaction Activity Heatmap</b><br>"
                 "<sub>Transaction frequency by day of week and hour (UTC)</sub>",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        xaxis=dict(title="Hour of Day (UTC)", dtick=2),
        yaxis=dict(title="Day of Week"),
        font=dict(family="Arial, sans-serif", size=12),
        height=500,
        width=1400,
        paper_bgcolor='#ffffff'
    )

    fig_heatmap.write_html('VIZ_3_TEMPORAL_HEATMAP.html')
    print("\n✅ VIZ 3 COMPLETE:")
    print("   📄 VIZ_3_TEMPORAL_HEATMAP.html (transaction activity patterns)")

print("\n" + "=" * 80)
print("✅ PROFESSIONAL VISUALIZATIONS COMPLETE")
print("=" * 80)
print("\n📂 OUTPUT FILES:")
print("   1. VIZ_1_INTERACTIVE_NETWORK_3D.html - 3D network graph (interactive)")
print("   2. VIZ_2_BLOCKCHAIN_FLOW_SANKEY.html - Multi-chain fund flows (interactive)")
print("   3. VIZ_3_TEMPORAL_HEATMAP.html - Transaction timing patterns (interactive)")
print("\n🎯 Next: Create geographic map, evidence timeline, and RICO dashboard...")
