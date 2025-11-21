# USER GUIDE - CERT Analytics Investigation System

**Version**: 1.0
**Date**: 2025-11-21
**For**: Legal Team & Authorized Users

---

## 🚨 BEFORE YOU BEGIN

**REQUIRED READING**: Please read `LEGAL_DISCLAIMER.md` before using this system.

**Key Points**:
- ✅ All data from OSINT (open-source) only
- ✅ Confidential - not for public dissemination
- ✅ AI-generated hypotheses may appear as facts but require verification
- ✅ Designed for legal team use only

---

## 📚 TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Searching Evidence](#searching-evidence)
4. [Viewing Visualizations](#viewing-visualizations)
5. [Understanding Evidence Tiers](#understanding-evidence-tiers)
6. [Working with Citations](#working-with-citations)
7. [Network Analysis](#network-analysis)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)
10. [Support & Resources](#support--resources)

---

## 🚀 QUICK START

### **5-Minute Setup**

```bash
# 1. Navigate to project directory
cd /Users/breydentaylor/certainly/visualizations

# 2. Activate Python environment
source venv/bin/activate

# 3. Run a semantic search
python scripts/search_corpus.py "Jason Shurka fraud" 10

# 4. View word cloud
open coordination/wordcloud_global_all_chunks.png

# 5. Open interactive network
open coordination/network_interactive.html
```

**That's it!** You're now searching 88,721 embedded documents and viewing prosecution-ready visualizations.

---

## 🏗️ SYSTEM OVERVIEW

### **What This System Does**

The CERT Analytics system provides:

1. **Semantic Search**: Query 88,721 document embeddings in natural language
2. **Evidence Catalog**: 22+ evidence items organized by tier and pillar
3. **Visualizations**: 17 print-ready charts and networks (300 DPI)
4. **Citations**: 327 citations with SHA-256 integrity verification
5. **Network Analysis**: RICO enterprise structure with 50 nodes, 22 communities
6. **Provenance Tracking**: Full chain of custody for all evidence

### **System Architecture**

```
User Query → Semantic Search (Qdrant) → Results + Citations
                ↓
         Evidence Catalog
                ↓
    Network Graph + Word Clouds
                ↓
      Trial-Ready Package
```

### **Key Technologies**

- **Python 3.11**: Core automation and analysis
- **Qdrant**: Vector database for semantic search
- **sentence-transformers**: Natural language embeddings
- **NetworkX**: Graph analysis
- **matplotlib/seaborn**: Statistical visualizations
- **Git**: Version control and collaboration

---

## 🔍 SEARCHING EVIDENCE

### **Semantic Search (Recommended)**

**Basic Search**:
```bash
python scripts/search_corpus.py "cryptocurrency wallet transactions" 20
```

**Parameters**:
- **Query**: Natural language question or keywords
- **Limit**: Number of results (default: 10, max: 100)

**Example Queries**:
```bash
# Find victim complaints
python scripts/search_corpus.py "victim complaint UNIFYD" 15

# Blockchain evidence
python scripts/search_corpus.py "wallet address crypto laundering" 25

# Medical fraud
python scripts/search_corpus.py "healing frequency medical claims" 10

# Entity relationships
python scripts/search_corpus.py "Shurka family connections Israel" 20
```

**Output Format**:
```
Result 1 (Score: 0.8234):
  File: /path/to/document.html
  Chunk: 512 tokens starting at char 1024
  Preview: "Jason Shurka promoted UNIFYD healing centers..."

Result 2 (Score: 0.7891):
  ...
```

### **Advanced Search (Python API)**

For AI agents or custom scripts, see `AI_AGENT_README.md` section 2.

---

## 📊 VIEWING VISUALIZATIONS

### **Word Clouds (17 files)**

**Global Overview**:
```bash
open coordination/wordcloud_global_all_chunks.png
# 5.9 MB, 8376×6482px - Shows entire investigation scope
```

**By Evidence Type**:
```bash
open coordination/wordcloud_chunk_01_telegram.png  # Communications
open coordination/wordcloud_chunk_02_blockchain.png  # Financial
open coordination/wordcloud_chunk_03_legal.png  # Court documents
```

**Color Coding**:
- 🔴 **Red**: Fraud terms (fraud, scam, fake, stolen)
- 🟠 **Orange**: Victim terms (victim, complaint, loss, harm)
- 🟢 **Green**: Money terms (USD, BTC, ETH, wallet, crypto)
- 🔵 **Blue**: Entity terms (Jason, Shurka, UNIFYD, TLS)

**Usage Tips**:
- Zoom in to see low-frequency terms
- Look for unexpected co-locations (e.g., "healing" + "millions")
- Compare across chunks to identify patterns

### **Statistical Charts**

```bash
# Indicator frequency
open coordination/indicator_barchart.png

# Co-occurrence heatmap
open coordination/indicator_cooccurrence_heatmap.png

# Cluster distribution
open coordination/cluster_size_distribution.png
```

### **Network Graphs**

```bash
# Interactive (best for exploration)
open coordination/network_interactive.html

# Static (best for printing)
open coordination/network_entity_clusters.png
open coordination/network_communities.png
```

**Network Features**:
- **Hover**: See entity metadata
- **Drag**: Rearrange nodes
- **Zoom**: Focus on specific clusters
- **Color**: Communities detected by Louvain algorithm

---

## 🎯 UNDERSTANDING EVIDENCE TIERS

### **Tier System**

| Tier | Priority | Criteria | Use Case |
|------|----------|----------|----------|
| **1** | Critical | Direct proof of RICO predicates | Trial evidence |
| **2** | High | Strong corroborative value | Grand jury presentation |
| **3** | Medium | Supporting context | Expert witness prep |
| **4** | Low | Background information | Discovery response |
| **5** | Minimal | Tangential relevance | Completeness |

### **Current Inventory (v6)**

```json
{
  "tier1_items": 0,
  "tier2_items": 8,
  "tier3_items": 14,
  "prosecution_readiness_pct": 36.4
}
```

**Interpreting Tiers**:
- ✅ Tier 2+ = Ready for prosecution review
- ⚠️ Tier 3+ = Needs corroboration
- ℹ️ Tier 4-5 = Context only

**⚠️ Important**: Tier ≠ Admissibility. All evidence requires legal review before trial use.

---

## 📚 WORKING WITH CITATIONS

### **Citation Database**

```bash
# View all citations
cat coordination/citation_database.json | jq '.citations | length'
# Output: 327

# Find citations for specific entity
cat coordination/citation_database.json | jq '.citations[] | select(.entity == "Jason Shurka")'

# Verify document integrity
cat coordination/citation_database.json | jq '.citations[] | {file: .file_path, hash: .sha256}'
```

### **Provenance Chains**

```bash
# View provenance chains
cat coordination/provenance_chains.json | jq '.chains[] | {claim, evidence_count}'

# Trace specific claim
cat coordination/provenance_chains.json | jq '.chains[] | select(.claim | contains("2002 agreement"))'
```

### **Citation Master Index**

```bash
# Alphabetical index
cat coordination/citation_master_index.md

# Search for term
grep -i "blockchain" coordination/citation_master_index.md
```

**Citation Format**:
```json
{
  "citation_id": "CITE-DOC-001",
  "file_path": "/path/to/source.html",
  "sha256": "a1b2c3...",
  "tier": 2,
  "prosecution_value": 8,
  "cited_in": ["evidence_item_123"]
}
```

---

## 🕸️ NETWORK ANALYSIS

### **Interactive Network**

**Opening**:
```bash
open coordination/network_interactive.html
```

**Features**:
- **50 nodes**: Entities, wallets, organizations
- **48 edges**: Relationships (ownership, transactions, family)
- **22 communities**: Detected sub-groups
- **Centrality metrics**: Importance scores

**Key Entities**:
```json
{
  "Jason Shurka": {"centrality": 0.4898, "connections": 35},
  "TLS (The Light System)": {"centrality": 0.3421, "connections": 28},
  "UNIFYD": {"centrality": 0.2987, "connections": 22}
}
```

### **Advanced Analysis (Gephi)**

For complex network analysis:

```bash
# Export to Gephi
open coordination/network_graph.graphml
# Use Gephi (https://gephi.org/) to:
# - Run additional layout algorithms
# - Calculate betweenness centrality
# - Identify bridge entities
# - Export high-res visualizations
```

### **Network Statistics**

```bash
# View centrality measures
cat coordination/network_statistics.json | jq '.centrality'

# Community structure
cat coordination/network_statistics.json | jq '.communities'
```

---

## ✅ COMMON TASKS

### **Task 1: Find Evidence for Specific Entity**

```bash
# Semantic search
python scripts/search_corpus.py "Manny Shurka connections" 20

# Check evidence inventory
cat coordination/evidence_inventory_v6.json | jq '.evidence[] | select(.description | contains("Manny"))'

# View network connections
open coordination/network_interactive.html
# Search for "Manny" in browser
```

### **Task 2: Prepare Trial Exhibit**

```bash
# 1. Find relevant word cloud
open coordination/wordcloud_chunk_03_legal.png

# 2. Get citation
cat coordination/citation_database.json | jq '.citations[] | select(.file_path | contains("legal"))'

# 3. Verify integrity
shasum -a 256 /path/to/source/file
# Compare with citation SHA-256
```

### **Task 3: Respond to Discovery Request**

```bash
# Example: "Produce all documents mentioning cryptocurrency"

# 1. Semantic search
python scripts/search_corpus.py "cryptocurrency bitcoin ethereum wallet" 100 > crypto_results.txt

# 2. Extract file paths
cat crypto_results.txt | grep "File:" | sort -u > crypto_files.txt

# 3. Check evidence inventory
cat coordination/evidence_inventory_v6.json | jq '.evidence[] | select(.cert_analytics.indicator_type == "wallet_addresses")'

# 4. Compile production list with citations
```

### **Task 4: Generate Expert Witness Report**

```bash
# 1. Export statistics
cat coordination/html_indicator_counts.json > expert_report_data.json

# 2. Include visualizations
cp coordination/indicator_barchart.png expert_report/
cp coordination/indicator_cooccurrence_heatmap.png expert_report/

# 3. Add network analysis
cp coordination/network_statistics.json expert_report/
cp coordination/network_entity_clusters.png expert_report/

# 4. Cite methodology
cp LEGAL_DISCLAIMER.md expert_report/methodology.md
```

---

## 🔧 TROUBLESHOOTING

### **Semantic Search Not Working**

```bash
# Check Qdrant database
ls -lh qdrant_db/
# Should show ~400 MB

# Reinstall dependencies
source venv/bin/activate
pip install --upgrade qdrant-client sentence-transformers

# Test search
python scripts/search_corpus.py "test query" 5
```

### **Visualizations Won't Open**

```bash
# macOS
open coordination/wordcloud_global_all_chunks.png

# Linux
xdg-open coordination/wordcloud_global_all_chunks.png

# Windows
start coordination\\wordcloud_global_all_chunks.png

# If image viewer missing, try browser
python -m http.server 8000
# Navigate to http://localhost:8000/coordination/
```

### **File Not Found Errors**

```bash
# Verify file existence
find . -name "evidence_inventory_v6.json"

# Check if coordination/ is in .gitignore
cat .gitignore | grep coordination

# Files in coordination/ are NOT in git (too large)
# They are generated by CERT agents
# Run scripts to regenerate if missing
```

### **Permission Denied**

```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/*.py

# Check file ownership
ls -la scripts/
```

---

## 📞 SUPPORT & RESOURCES

### **Documentation Files**

| File | Purpose | Audience |
|------|---------|----------|
| `USER_GUIDE.md` | This file - User interaction guide | Legal team |
| `AI_AGENT_README.md` | Technical API documentation | AI agents, developers |
| `LEGAL_DISCLAIMER.md` | Confidentiality and methodology | **REQUIRED READING** |
| `DIRECTORY_TREE.md` | File navigation | All users |
| `README.md` | Project overview | All users |
| `CERT_ANALYTICS_PACKAGE_README.md` | CERT system guide | Technical users |

### **Key Scripts**

```bash
# Semantic search
scripts/search_corpus.py

# Corpus mapping
scripts/02_corpus_mapper.py

# Evidence integration
scripts/evidence_integrator.py

# Auto sync (file discovery, git push)
scripts/auto_sync.sh
```

### **State Files**

Check agent completion status:
```bash
cat state/cert_analytics_state.json | jq '.agents'
cat state/evidence_integrator.state.json
```

### **Reporting Issues**

If you encounter technical issues:

1. **Check state files** for agent status
2. **Review logs** in `/tmp/`:
   ```bash
   ls -lt /tmp/*_output.log | head -10
   ```
3. **Verify dependencies**:
   ```bash
   source venv/bin/activate
   pip list | grep -E "qdrant|sentence|networkx"
   ```
4. **Document error** with screenshots and exact commands

---

## 🎓 BEST PRACTICES

### **Evidence Management**

✅ **DO**:
- Verify all evidence before citing in legal documents
- Use SHA-256 hashes to check document integrity
- Track provenance chains for admissibility
- Maintain confidentiality of all materials
- Document search methodology for expert reports

❌ **DON'T**:
- Rely on AI-generated hypotheses without verification
- Share materials outside authorized legal team
- Use tier assignments as proof of admissibility
- Assume semantic search results are exhaustive
- Forget to read LEGAL_DISCLAIMER.md

### **Search Strategies**

✅ **Effective Queries**:
- Use specific entity names: "Jason Shurka" not "JS"
- Combine concepts: "blockchain wallet laundering"
- Try synonyms: "cryptocurrency" AND "digital assets"
- Use victim terms: "complaint harm loss victim"

❌ **Ineffective Queries**:
- Single words: "fraud" (too broad)
- Acronyms without expansion: "RICO"
- Vague concepts: "bad things"
- Questions: "did Jason commit fraud?" (use keywords instead)

### **Workflow Recommendations**

1. **Start broad**: Semantic search for entity/concept
2. **Narrow focus**: Review top 20 results
3. **Verify sources**: Check citations and SHA-256 hashes
4. **Cross-reference**: Use network graph to find connections
5. **Document findings**: Track which searches yielded results
6. **Escalate questions**: Consult legal team for interpretation

---

## 📅 SYSTEM UPDATES

### **Auto-Sync**

To update file tree and sync to GitHub:
```bash
bash scripts/auto_sync.sh
```

This will:
- ✅ Discover new files
- ✅ Update DIRECTORY_TREE.md
- ✅ Stage changes
- ✅ Commit with auto-generated message
- ✅ Push to GitHub

### **Version History**

Check system version:
```bash
cat coordination/evidence_inventory_v6.json | jq '.version, .created'
```

---

## 🔐 SECURITY REMINDERS

- 🔒 **Never share this system publicly**
- 🔒 **Use secure network connections only**
- 🔒 **Encrypt files when transmitting**
- 🔒 **Log out of shared computers**
- 🔒 **Report suspicious access immediately**

---

## ✅ QUICK REFERENCE CARD

```bash
# SEARCH
python scripts/search_corpus.py "query" 10

# VISUALIZE
open coordination/wordcloud_global_all_chunks.png
open coordination/network_interactive.html

# EVIDENCE
cat coordination/evidence_inventory_v6.json | jq '.summary'

# CITATIONS
cat coordination/citation_database.json | jq '.citations | length'

# SYNC
bash scripts/auto_sync.sh

# DOCUMENTATION
cat LEGAL_DISCLAIMER.md  # REQUIRED READING
cat USER_GUIDE.md         # This file
cat AI_AGENT_README.md    # Technical API
```

---

**END OF USER GUIDE**

For technical details, see `AI_AGENT_README.md`.
For legal context, see `LEGAL_DISCLAIMER.md`.
For file locations, see `DIRECTORY_TREE.md`.
