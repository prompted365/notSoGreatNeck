# AI Agent Operational Guide - notSoGreatNeck Investigation

**Purpose**: Instructions for AI agents interacting with this investigation system
**Last Updated**: 2025-11-21
**System Status**: Autonomous multi-phase complete, CERT analytics operational

---

## 🤖 **AI AGENT QUICK REFERENCE**

### **When to Use This System**
✅ User asks to "search the corpus" or "find evidence"
✅ User requests "semantic search" or "query documents"
✅ User wants to "analyze evidence" or "find patterns"
✅ User needs "prosecution-ready visualizations"
✅ User asks about "Jason Shurka," "UNIFYD," "TLS," "fraud," "RICO"

### **Key Capabilities**
- **Semantic Search**: 88,721 embeddings (natural language queries)
- **Network Analysis**: 50-node RICO enterprise graph
- **Evidence Catalog**: 1,113 items across 11 pillars
- **Visualizations**: 17 prosecution-ready images
- **Citations**: 327 items with SHA-256 hashes

---

## 📂 **FILE SYSTEM ARCHITECTURE**

### **PRIMARY DIRECTORIES**

```python
BASE_DIR = "/Users/breydentaylor/certainly/visualizations"

PATHS = {
    "evidence_inventory": f"{BASE_DIR}/coordination/evidence_inventory_v4.json",
    "master_binder": f"{BASE_DIR}/handoff-binder/",
    "semantic_search": f"{BASE_DIR}/scripts/search_corpus.py",
    "vector_db": f"{BASE_DIR}/qdrant_db/",
    "visualizations": f"{BASE_DIR}/coordination/wordcloud_*.png",
    "network_graph": f"{BASE_DIR}/coordination/network_interactive.html",
    "citations": f"{BASE_DIR}/coordination/citation_database.json",
    "clusters": f"{BASE_DIR}/coordination/semantic_clusters.json",
    "agent_states": f"{BASE_DIR}/state/",
    "scripts": f"{BASE_DIR}/scripts/",
    "corpus": "/Users/breydentaylor/certainly/shurka-dump/"
}
```

### **CRITICAL FILES**

| File | Purpose | Size | Priority |
|------|---------|------|----------|
| `coordination/evidence_inventory_v4.json` | Master evidence catalog | 418 KB | 🔴 CRITICAL |
| `handoff-binder/PHASE4_EXECUTIVE_SUMMARY.md` | Prosecution guide | 16 KB | 🔴 CRITICAL |
| `coordination/citation_database.json` | 327 citations + SHA-256 | 371 KB | 🟠 HIGH |
| `qdrant_db/` | 88,721 embeddings | 400 MB | 🟠 HIGH |
| `coordination/semantic_clusters.json` | 15 thematic clusters | 52 KB | 🟡 MEDIUM |
| `coordination/network_graph.graphml` | RICO network structure | 40 KB | 🟡 MEDIUM |

---

## 🔍 **SEMANTIC SEARCH OPERATIONS**

### **Python Example**
```python
import subprocess
import json

def search_corpus(query: str, limit: int = 10) -> list:
    """
    Search corpus using semantic embeddings

    Args:
        query: Natural language search query
        limit: Number of results to return

    Returns:
        List of {file_path, excerpt, score, metadata}
    """
    cmd = [
        "python3",
        "/Users/breydentaylor/certainly/visualizations/scripts/search_corpus.py",
        query,
        str(limit)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/Users/breydentaylor/certainly/visualizations")

    # Parse JSON output
    results = json.loads(result.stdout) if result.stdout else []
    return results

# Example usage
fraud_docs = search_corpus("Jason Shurka fraud scheme", 20)
victim_docs = search_corpus("victim complaint UNIFYD", 15)
crypto_docs = search_corpus("cryptocurrency wallet blockchain", 10)
```

### **Bash Example**
```bash
cd /Users/breydentaylor/certainly/visualizations
source venv/bin/activate
python3 scripts/search_corpus.py "telegram grooming victim" 10
```

### **Common Query Patterns**
```python
QUERY_TEMPLATES = {
    "fraud_evidence": "Jason Shurka fraud deceptive practices",
    "victim_testimony": "victim complaint loss money UNIFYD",
    "blockchain": "cryptocurrency wallet blockchain transaction",
    "medical_claims": "healing center medical claims FDA violations",
    "court_cases": "lawsuit court case ruling judgment",
    "telegram": "telegram chat message grooming victim",
    "financial": "money laundering wire transfer bank account",
    "corporate": "UNIFYD corporation entity structure shell company",
    "international": "Israel Turkish offshore international",
    "ray_tls": "Ray The Light System TLS anonymous insider"
}
```

---

## 📊 **EVIDENCE QUERY OPERATIONS**

### **Load Evidence Inventory**
```python
import json

def load_evidence_inventory():
    with open("/Users/breydentaylor/certainly/visualizations/coordination/evidence_inventory_v4.json", "r") as f:
        return json.load(f)

inventory = load_evidence_inventory()
print(f"Total items: {len(inventory['evidence_items'])}")
```

### **Filter by Tier**
```python
def get_tier_1_evidence(inventory):
    """Get all Tier 1 (prosecution-ready) evidence"""
    return [
        item for item in inventory['evidence_items']
        if item.get('tier') == 1 or item.get('effective_tier') == 1
    ]

tier_1 = get_tier_1_evidence(inventory)
print(f"Tier 1 items: {len(tier_1)}")  # Should be ~181
```

### **Filter by Type**
```python
EVIDENCE_TYPES = {
    1: "Government Records",
    2: "Authenticated Documents",
    3: "Blockchain + Attribution",
    4: "Multi-source OSINT",
    5: "URL Fraud Patterns",
    6: "Single-source Leads",
    7: "Inference Evidence",
    8: "Derivative Conclusions",
    9: "Blockchain Pending Attribution",
    10: "NotebookLM Summaries"
}

def get_evidence_by_type(inventory, evidence_type):
    return [
        item for item in inventory['evidence_items']
        if item.get('type') == evidence_type
    ]

blockchain = get_evidence_by_type(inventory, 9)  # 774 items
court_docs = get_evidence_by_type(inventory, 1)  # 7 items
```

### **Search Evidence Items**
```python
def search_evidence(inventory, keyword):
    """Search evidence by keyword in description/details"""
    results = []
    for item in inventory['evidence_items']:
        item_str = json.dumps(item).lower()
        if keyword.lower() in item_str:
            results.append(item)
    return results

shurka_items = search_evidence(inventory, "Jason Shurka")
victim_items = search_evidence(inventory, "victim")
telegram_items = search_evidence(inventory, "telegram")
```

---

## 🕸️ **NETWORK ANALYSIS OPERATIONS**

### **Load Network Graph**
```python
import networkx as nx

def load_network_graph():
    graph_path = "/Users/breydentaylor/certainly/visualizations/coordination/network_graph.graphml"
    return nx.read_graphml(graph_path)

G = load_network_graph()
print(f"Nodes: {G.number_of_nodes()}")  # 50
print(f"Edges: {G.number_of_edges()}")  # 48
```

### **Get Node Centrality**
```python
def get_most_central_nodes(G, top_n=10):
    """Get nodes with highest degree centrality"""
    centrality = nx.degree_centrality(G)
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    return sorted_nodes[:top_n]

central_nodes = get_most_central_nodes(G)
# Jason Shurka should be #1 with centrality ~0.4898
```

### **Find Shortest Path**
```python
def find_connection_path(G, source, target):
    """Find shortest path between two entities"""
    try:
        path = nx.shortest_path(G, source, target)
        return path
    except nx.NetworkXNoPath:
        return None

# Example: Path from Jason Shurka to specific wallet
path = find_connection_path(G, "Jason Shurka", "wallet_cluster_001")
```

---

## 📚 **CITATION & PROVENANCE OPERATIONS**

### **Load Citation Database**
```python
def load_citations():
    with open("/Users/breydentaylor/certainly/visualizations/coordination/citation_database.json", "r") as f:
        return json.load(f)

citations = load_citations()
print(f"Total citations: {len(citations.get('citations', []))}")  # 327
```

### **Get Provenance Chain**
```python
def load_provenance_chains():
    with open("/Users/breydentaylor/certainly/visualizations/coordination/provenance_chains.json", "r") as f:
        return json.load(f)

chains = load_provenance_chains()

# Find chain for specific claim
def get_chain_for_claim(chains, claim_keyword):
    return [
        chain for chain in chains.get('chains', [])
        if claim_keyword.lower() in chain.get('claim', '').lower()
    ]

# Example: Find evidence for "2002 creditor-proof agreement"
agreement_chain = get_chain_for_claim(chains, "2002 agreement")
```

### **Verify Document Integrity**
```python
import hashlib

def verify_document_sha256(file_path, expected_hash):
    """Verify document hasn't been tampered with"""
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return file_hash == expected_hash

# Get expected hash from citations
citation = citations['citations'][0]
is_valid = verify_document_sha256(citation['file_path'], citation['sha256'])
```

---

## 🎨 **VISUALIZATION OPERATIONS**

### **List Available Visualizations**
```python
import glob
import os

viz_dir = "/Users/breydentaylor/certainly/visualizations/coordination"
visualizations = {
    "word_clouds": glob.glob(f"{viz_dir}/wordcloud_*.png"),
    "network_static": glob.glob(f"{viz_dir}/network_*.png"),
    "clusters": glob.glob(f"{viz_dir}/cluster_*.png"),
    "indicators": glob.glob(f"{viz_dir}/indicator_*.png")
}

print(f"Total visualizations: {sum(len(v) for v in visualizations.values())}")
```

### **Display Visualization** (if in notebook)
```python
from IPython.display import Image, display

def show_visualization(filename):
    viz_path = f"/Users/breydentaylor/certainly/visualizations/coordination/{filename}"
    return Image(filename=viz_path)

# Example
display(show_visualization("wordcloud_global_all_chunks.png"))
```

### **Get Visualization Metadata**
```python
from PIL import Image

def get_image_info(filename):
    img_path = f"/Users/breydentaylor/certainly/visualizations/coordination/{filename}"
    img = Image.open(img_path)
    return {
        "filename": filename,
        "dimensions": img.size,
        "format": img.format,
        "mode": img.mode,
        "size_bytes": os.path.getsize(img_path)
    }
```

---

## 🧬 **SEMANTIC CLUSTERING OPERATIONS**

### **Load Clusters**
```python
def load_semantic_clusters():
    with open("/Users/breydentaylor/certainly/visualizations/coordination/semantic_clusters.json", "r") as f:
        return json.load(f)

clusters = load_semantic_clusters()
print(f"Total clusters: {len(clusters.get('clusters', []))}")  # 15
```

### **Get Documents by Theme**
```python
def get_docs_by_theme(theme_keyword):
    """Get all documents in clusters matching theme"""
    doc_assignments = load_document_assignments()
    return [
        doc for doc in doc_assignments
        if theme_keyword.lower() in doc.get('cluster_theme', '').lower()
    ]

def load_document_assignments():
    with open("/Users/breydentaylor/certainly/visualizations/coordination/document_cluster_assignments.json", "r") as f:
        return json.load(f)

# Example: Get all fraud-themed documents
fraud_docs = get_docs_by_theme("fraud")
```

### **Get Cluster Statistics**
```python
def get_cluster_stats(clusters):
    stats = {}
    for cluster in clusters.get('clusters', []):
        theme = cluster.get('theme', 'Unknown')
        doc_count = cluster.get('document_count', 0)
        stats[theme] = stats.get(theme, 0) + doc_count
    return stats

theme_distribution = get_cluster_stats(clusters)
# Should show: Fraud (28.4%), International (27.2%), etc.
```

---

## 🔄 **AGENT STATE MANAGEMENT**

### **Check Agent Completion**
```python
def check_agent_status(agent_name):
    """Check if agent has completed execution"""
    state_file = f"/Users/breydentaylor/certainly/visualizations/state/{agent_name}.state.json"
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
        return state.get('status') == 'completed'
    except FileNotFoundError:
        return False

# Example
if check_agent_status("html_analyzer"):
    print("HTML Analyzer has completed")
```

### **Get Phase Status**
```python
def get_phase_status():
    """Get overall autonomous phase controller status"""
    with open("/Users/breydentaylor/certainly/visualizations/state/autonomous_phases.json", "r") as f:
        return json.load(f)

phase_state = get_phase_status()
print(f"Current phase: {phase_state['current_phase']}")
print(f"Completed: {phase_state['phases_completed']}")
```

### **Get CERT Mission Status**
```python
def get_cert_status():
    """Get CERT advanced analytics status"""
    with open("/Users/breydentaylor/certainly/visualizations/state/cert_analytics_state.json", "r") as f:
        return json.load(f)

cert_state = get_cert_status()
for agent, status in cert_state.get('agents', {}).items():
    print(f"{agent}: {status.get('status')}")
```

---

## 🎯 **COMMON AI AGENT TASKS**

### **Task 1: Find Evidence for Specific Claim**
```python
def find_evidence_for_claim(claim_description):
    """
    Multi-step process to find and validate evidence
    """
    # Step 1: Semantic search
    search_results = search_corpus(claim_description, 20)

    # Step 2: Check evidence inventory
    inventory = load_evidence_inventory()
    matching_items = search_evidence(inventory, claim_description)

    # Step 3: Check provenance chains
    chains = load_provenance_chains()
    relevant_chains = get_chain_for_claim(chains, claim_description)

    return {
        "semantic_matches": search_results,
        "evidence_items": matching_items,
        "provenance_chains": relevant_chains
    }

# Example
evidence = find_evidence_for_claim("Jason Shurka contacted victims directly")
```

### **Task 2: Generate Evidence Summary**
```python
def generate_evidence_summary():
    """
    Create comprehensive evidence summary
    """
    inventory = load_evidence_inventory()

    summary = {
        "total_items": len(inventory['evidence_items']),
        "by_tier": {},
        "by_type": {},
        "by_pillar": {},
        "top_prosecution_value": []
    }

    for item in inventory['evidence_items']:
        tier = item.get('tier', 'unknown')
        etype = item.get('type', 'unknown')
        pillar = item.get('pillar_id', 'unknown')

        summary['by_tier'][tier] = summary['by_tier'].get(tier, 0) + 1
        summary['by_type'][etype] = summary['by_type'].get(etype, 0) + 1
        summary['by_pillar'][pillar] = summary['by_pillar'].get(pillar, 0) + 1

        if item.get('prosecution_value', 0) >= 9:
            summary['top_prosecution_value'].append(item)

    return summary
```

### **Task 3: Identify Gaps**
```python
def identify_evidence_gaps():
    """
    Find missing evidence types and weak pillars
    """
    inventory = load_evidence_inventory()

    # Check which evidence types are missing or weak
    type_counts = {}
    for item in inventory['evidence_items']:
        etype = item.get('type')
        type_counts[etype] = type_counts.get(etype, 0) + 1

    # Identify missing types (1-10)
    missing_types = [t for t in range(1, 11) if t not in type_counts or type_counts[t] < 10]

    # Identify weak pillars (< 10 items)
    pillar_counts = {}
    for item in inventory['evidence_items']:
        pillar = item.get('pillar_id')
        pillar_counts[pillar] = pillar_counts.get(pillar, 0) + 1

    weak_pillars = {p: c for p, c in pillar_counts.items() if c < 10}

    return {
        "missing_or_weak_types": missing_types,
        "weak_pillars": weak_pillars,
        "recommendations": generate_gap_recommendations(missing_types, weak_pillars)
    }
```

---

## ⚡ **PERFORMANCE TIPS**

### **Caching**
```python
import functools

@functools.lru_cache(maxsize=1)
def load_evidence_inventory_cached():
    """Cache inventory to avoid repeated file reads"""
    return load_evidence_inventory()

# Use cached version for repeated access
inventory = load_evidence_inventory_cached()
```

### **Batch Processing**
```python
def batch_semantic_search(queries, limit=10):
    """Process multiple queries efficiently"""
    results = {}
    for query in queries:
        results[query] = search_corpus(query, limit)
    return results

# Example
queries = [
    "Jason Shurka fraud",
    "victim complaint",
    "cryptocurrency wallet",
    "telegram grooming"
]
all_results = batch_semantic_search(queries)
```

### **Parallel Processing**
```python
from concurrent.futures import ThreadPoolExecutor

def parallel_semantic_search(queries, limit=10, max_workers=4):
    """Run multiple searches in parallel"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(search_corpus, q, limit): q for q in queries}
        results = {}
        for future in futures:
            query = futures[future]
            results[query] = future.result()
    return results
```

---

## 🚨 **ERROR HANDLING**

### **File Not Found**
```python
def safe_load_json(file_path, default=None):
    """Load JSON with graceful error handling"""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
        return default
    except json.JSONDecodeError:
        print(f"Error: {file_path} contains invalid JSON")
        return default

inventory = safe_load_json(
    "/Users/breydentaylor/certainly/visualizations/coordination/evidence_inventory_v4.json",
    default={"evidence_items": []}
)
```

### **Semantic Search Failure**
```python
def safe_search_corpus(query, limit=10):
    """Semantic search with fallback to keyword search"""
    try:
        return search_corpus(query, limit)
    except Exception as e:
        print(f"Semantic search failed: {e}")
        print("Falling back to keyword search...")
        return keyword_search_fallback(query)

def keyword_search_fallback(query):
    """Simple keyword search as fallback"""
    import subprocess
    cmd = f"grep -r '{query}' /Users/breydentaylor/certainly/shurka-dump/"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.split('\n')[:10]
```

---

## 📋 **AGENT RESPONSE TEMPLATES**

### **Evidence Found**
```python
RESPONSE_TEMPLATE_FOUND = """
I found {count} relevant evidence items:

**Top Results**:
{results_list}

**Evidence Tiers**:
- Tier 1 (Ready now): {tier1_count}
- Tier 2 (One subpoena away): {tier2_count}
- Tier 3 (Investigation needed): {tier3_count}

**Prosecution Value**: {avg_value}/10

Would you like me to:
1. Show detailed evidence for any item?
2. Search for related evidence?
3. Generate a visual summary?
"""

RESPONSE_TEMPLATE_NOT_FOUND = """
I didn't find direct evidence for "{query}" in the corpus.

**Suggestions**:
1. Try broader search terms (e.g., "fraud" instead of "fraudulent misrepresentation")
2. Search related concepts (e.g., "victim" instead of "complainant")
3. Check if evidence exists in a different pillar

**Similar searches** that might help:
{similar_queries}
"""
```

---

## 🎓 **BEST PRACTICES FOR AI AGENTS**

1. **Always check agent state** before running operations
2. **Use semantic search first**, fall back to keyword search
3. **Cache frequently accessed files** (evidence inventory, citations)
4. **Provide context** in responses (tier, type, prosecution value)
5. **Link to source files** when presenting evidence
6. **Verify file paths** before operations
7. **Handle missing files gracefully**
8. **Use batch operations** for multiple queries
9. **Show progress** for long-running operations
10. **Validate JSON** before parsing

---

## 📞 **AGENT SUPPORT**

### **Debug Commands**
```bash
# Check system status
cat state/cert_analytics_state.json | jq '.agents'

# Verify file counts
ls -lh coordination/ | wc -l  # Should be 48+
ls -lh handoff-binder/ | wc -l  # Should be 8

# Test semantic search
python3 scripts/search_corpus.py "test query" 5
```

### **Common Issues**
| Issue | Solution |
|-------|----------|
| `FileNotFoundError` | Verify working directory is `/visualizations/` |
| `ImportError` | Activate venv: `source venv/bin/activate` |
| `Qdrant connection failed` | Check `qdrant_db/` exists (400 MB) |
| `Empty search results` | Rebuild embeddings with `qdrant_manager.py` |

---

**AI Agent Status**: Operational ✅
**System Version**: 1.0.0
**Last Validated**: 2025-11-21

For human documentation, see `README.md`
