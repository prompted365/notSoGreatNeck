# Directory Tree - notSoGreatNeck Investigation

**Generated**: 2025-11-21
**Total Size**: ~456 MB (outputs) + 1.6 GB (corpus)
**Structure**: Organized by function (evidence, analysis, automation, documentation)

---

## 📁 **ROOT STRUCTURE**

```
visualizations/
├── README.md                          # Main project documentation
├── AI_AGENT_README.md                # AI agent operational guide
├── DIRECTORY_TREE.md                 # This file
├── .gitignore                        # Git ignore rules
├── requirements.txt                   # Python dependencies
├── venv/                             # Python virtual environment (not in git)
│
├── coordination/                     # 🔴 PRIMARY OUTPUTS (56 MB, 48 files)
│   ├── Evidence Catalogs
│   ├── Semantic Analysis
│   ├── Visualizations
│   ├── Network Analysis
│   └── Citations & Provenance
│
├── handoff-binder/                   # 🔴 PROSECUTION DELIVERABLES (8 files)
│   ├── evidence_inventory.json
│   ├── subpoena_package_final.md
│   ├── prosecution_readiness_report.json
│   └── PHASE4_EXECUTIVE_SUMMARY.md
│
├── state/                            # 🟡 AGENT STATES (144 KB, 21 files)
│   ├── autonomous_phases.json
│   ├── cert_analytics_state.json
│   └── [agent].state.json files
│
├── scripts/                          # 🟢 AUTOMATION (712 KB, 30+ files)
│   ├── Semantic Search
│   ├── Agent Deployment
│   ├── Analysis Pipelines
│   └── Background Monitors
│
├── qdrant_db/                        # 🟣 VECTOR DATABASE (400 MB)
│   └── 88,721 semantic embeddings
│
├── agents/                           # 🔵 AGENT CONTEXTS (10 directories)
│   ├── Pillar_Scout/
│   ├── Gap_Filler/
│   └── [agent directories]
│
└── docs/                             # 📚 DOCUMENTATION (15+ files)
    ├── Mission Reports
    ├── Technical Guides
    └── Integration Summaries
```

---

## 📂 **DETAILED BREAKDOWN**

### **`/coordination/` - Primary Evidence Outputs (48 files, 56 MB)**

#### **Evidence Catalogs**
```
coordination/
├── evidence_inventory_v4.json          # Master catalog (1,113 items, 418 KB)
├── evidence_inventory_v3_victim_entry.json
├── evidence_inventory_v2.json
├── PILLAR_01_blockchain_transactions.json  # 774 blockchain items
├── PILLAR_02_shadowlens_summaries.json     # 47 AI summaries
├── PILLAR_05_url_fraud_patterns.json       # 26 URL patterns
├── PILLAR_08_content_analysis.json         # 25+ YouTube videos
├── PILLAR_09_LEGAL_PROCEEDINGS.json        # 7 court cases (NEW)
├── PILLAR_10_SOCIAL_MEDIA_COMPLAINTS.json  # 18 complaints (NEW)
├── PILLAR_11_REGULATORY_VIOLATIONS.json    # 23 violations (NEW)
└── pillar_*.json                           # 11 pillars total
```

#### **Semantic Analysis**
```
coordination/
├── cert_file_chunks.json               # 124 files, 202 MB organized
├── html_word_frequencies.json          # 2.0 MB, top 500 terms/doc
├── html_indicator_counts.json          # 32 indicators × 83 docs
├── html_tfidf_scores.json              # 628 KB, 5,000 vocabulary
├── html_cooccurrence_network.json      # 367 co-occurrence edges
├── html_indicator_matrix.csv           # Spreadsheet format
├── html_top_tfidf_terms.csv            # Ranked terms
├── html_cooccurrence_edges.csv         # Network edge list
├── semantic_clusters.json              # 15 clusters, 52 KB
├── topic_model.json                    # 15 topics via LDA
└── document_cluster_assignments.json   # 680 doc→cluster mappings
```

#### **Visualizations (17 PNG files, 35 MB)**
```
coordination/
├── wordcloud_chunk_01_telegram.png     # 3.6 MB, 5604×4403px
├── wordcloud_chunk_02_blockchain.png   # 3.5 MB
├── wordcloud_chunk_03_legal.png        # 3.4 MB
├── wordcloud_chunk_04_financial.png    # 3.4 MB
├── wordcloud_chunk_05_websites.png     # 3.1 MB
├── wordcloud_chunk_06_communications.png # 3.3 MB
├── wordcloud_chunk_07_documents.png    # 3.5 MB
├── wordcloud_chunk_08_data.png         # 3.4 MB
├── wordcloud_global_all_chunks.png     # 5.9 MB, 8376×6482px
├── indicator_barchart.png              # 164 KB
├── indicator_cooccurrence_heatmap.png  # 324 KB
├── cluster_visualization_umap.png      # 225 KB
├── topic_distribution.png              # 83 KB
├── cluster_size_distribution.png       # 193 KB
├── network_entity_clusters.png         # 213 KB
├── network_document_topics.png         # 180 KB
└── network_communities.png             # 265 KB
```

#### **Network Analysis**
```
coordination/
├── network_interactive.html            # 23 KB, interactive RICO network
├── network_graph.graphml               # 40 KB, Gephi-compatible
├── network_statistics.json             # 6.3 KB, centrality measures
├── network_entity_clusters.png         # 213 KB
├── network_document_topics.png         # 180 KB
└── network_communities.png             # 265 KB
```

#### **Citations & Provenance**
```
coordination/
├── citation_database.json              # 371 KB, 327 citations + SHA-256
├── citation_index.json                 # 85 KB, forward/reverse lookup
├── provenance_chains.json              # 50 KB, 10 claim→evidence chains
├── citation_report_entities.md         # 4.3 KB, 12 priority entities
├── citation_report_clusters.md         # 21 KB, 28 clusters
└── citation_master_index.md            # 39 KB, alphabetical index
```

#### **Reddit Victim Analysis**
```
coordination/
├── reddit_victim_low_strain35_analysis.json      # 8.2 KB
├── victim_outreach_message.md                    # 7.3 KB
├── victim_corroboration.json                     # 9.5 KB
├── victim_impact_analysis.json                   # 13 KB
├── reddit_thread_1o6a60x_full.json              # 439 KB
├── reddit_comment_low_strain35_nju1r8g.json     # 14 KB
└── REDDIT_VICTIM_OUTREACH_EXECUTIVE_SUMMARY.md  # 14 KB
```

#### **YouTube Analysis**
```
coordination/
├── youtube_target_videos.json          # 414 lines, 25 videos
├── youtube_metadata.json               # 342 lines, 10 videos detailed
├── youtube_fraud_analysis.json         # 328 lines, 206 violations
├── video_archive_manifest.json         # 26 lines
├── YOUTUBE_ARCHIVAL_MISSION_REPORT.md  # 16 KB
└── YOUTUBE_EXECUTION_GUIDE.md          # 12 KB
```

#### **Integration Reports**
```
coordination/
├── CERT_MISSION_COMPLETE.md            # 25 KB, executive summary
├── CERT_ANALYTICS_PACKAGE_README.md    # 18 KB, user guide
├── INTELLIGENCE_REPORT_INTEGRATION_SUMMARY.md  # 15 KB
├── HTML_ANALYSIS_README.md             # 8.2 KB
├── WORD_CLOUD_GENERATOR_REPORT.md      # 10 KB
├── QDRANT_COMPLETION_REPORT.md         # 12 KB
├── QDRANT_QUICK_START.md               # 5 KB
├── SEMANTIC_CLUSTERER_COMPLETION_REPORT.txt  # 12 KB
├── NETWORK_GRAPHER_COMPLETION_REPORT.md      # 17 KB
└── CITATION_LINKER_EXECUTIVE_SUMMARY.md      # 17 KB
```

---

### **`/handoff-binder/` - Final Prosecution Package (8 files)**

```
handoff-binder/
├── evidence_inventory.json             # 418 KB, sorted by tier
├── subpoena_package_final.md           # 17 KB, legal language
├── subpoena_targets.json               # 19 KB, prioritized targets
├── prosecution_readiness_report.json   # 7 KB, metrics vs targets
├── PHASE4_EXECUTIVE_SUMMARY.md         # 16 KB, comprehensive guide
├── rico_timeline_visual.json           # 16 KB, 1993-2025 timeline
├── loop_summary.json                   # 10 KB, process documentation
└── quality_assurance_report.json       # 4 KB, QA results
```

**Purpose**: Ready-to-deliver prosecution package for legal team
**Status**: ✅ 100% QA validated
**Use Case**: Trial preparation, subpoena filing, expert testimony

---

### **`/state/` - Agent Execution States (21 files, 144 KB)**

```
state/
├── autonomous_phases.json              # Overall phase controller state
├── cert_analytics_state.json           # CERT mission state
├── global_scope_state.json             # Global investigation state
├── corpus_validator.state.json
├── gap_filler.state.json
├── subpoena_coordinator.state.json
├── blockchain_forensics.state.json
├── entity_linker.state.json
├── tier_auditor.state.json
├── evidence_synthesizer.state.json
├── final_packager.state.json
├── pillar_scout.state.json
├── reddit_outreach.state.json
├── youtube_archival.state.json
├── html_analyzer.state.json
├── word_cloud_generator.state.json
├── qdrant_manager.state.json
├── semantic_clusterer.state.json
├── network_grapher.state.json
├── citation_linker.state.json
└── evidence_integrator.state.json
```

**Purpose**: Track agent completion, enable resume capability
**Format**: JSON with status, timestamps, metrics, outputs
**Use Case**: System monitoring, debugging, continuation logic

---

### **`/scripts/` - Automation & Analysis (30+ files, 712 KB)**

#### **Semantic Search**
```
scripts/
├── search_corpus.py                    # Quick search utility
├── qdrant_manager.py                   # Vector DB setup
├── qdrant_test_and_save.py            # Search testing
└── 02_corpus_mapper.py                 # Corpus citation mapper
```

#### **Agent Deployment**
```
scripts/
├── 00_cert_background_monitor.sh       # 7-minute monitor
├── 01_chunk_identifier.py              # File chunking
├── html_analyzer.py                    # NLP analysis
├── word_cloud_generator.py             # Visualization
├── semantic_clusterer.py               # Clustering
└── autonomous_phase_controller.sh      # Phase controller
```

#### **YouTube & Reddit**
```
scripts/
├── youtube_archival.sh                 # yt-dlp automation
└── run_continuous_loop.sh              # Continuous discovery
```

**Purpose**: Automation, reproducibility, continuous operation
**Language**: Python 3.11, Bash
**Dependencies**: requirements.txt

---

### **`/qdrant_db/` - Vector Database (400 MB)**

```
qdrant_db/
├── collection/                         # Embedding vectors
├── meta.json                           # Collection metadata
└── storage/                            # Persistent storage
```

**Contents**: 88,721 semantic embeddings (384-dimensional)
**Model**: sentence-transformers/all-MiniLM-L6-v2
**Purpose**: Natural language corpus search
**Query Time**: <1 second

---

### **`/agents/` - Agent Context Files (10 directories)**

```
agents/
├── Pillar_Scout/
│   └── CONTEXT-PILLAR_SCOUT.md         # Pillar discovery mission
├── Gap_Filler/
│   └── CONTEXT-GAP_FILLER.md           # Gap filling instructions
├── Subpoena_Coordinator/
│   └── CONTEXT-SUBPOENA_COORDINATOR.md
├── Corpus_Validator/
├── Blockchain_Forensics/
├── Entity_Linker/
├── TIER_Auditor/
├── Evidence_Synthesizer/
├── Final_Packager/
└── Gap_Filler_Reactive/
    └── [Complete reactive system]
```

**Purpose**: Agent instructions, context, mission parameters
**Format**: Markdown with structured tasks
**Use Case**: Agent deployment, reproducibility

---

### **`/docs/` - Documentation (15+ files)**

```
docs/
├── Mission Reports
│   ├── CERT_MISSION_COMPLETE.md
│   ├── PHASE4_EXECUTIVE_SUMMARY.md
│   └── INTELLIGENCE_REPORT_INTEGRATION_SUMMARY.md
│
├── Technical Guides
│   ├── HTML_ANALYSIS_README.md
│   ├── QDRANT_QUICK_START.md
│   ├── NETWORK_GRAPHER_COMPLETION_REPORT.md
│   └── CITATION_LINKER_EXECUTIVE_SUMMARY.md
│
└── Architecture
    ├── AUTONOMOUS_MULTI_PHASE_ARCHITECTURE.md
    ├── CONTINUOUS_LOOP_README.md
    └── CERT_ANALYTICS_PACKAGE_README.md
```

---

## 📊 **SIZE BREAKDOWN**

| Directory | Size | Files | Description |
|-----------|------|-------|-------------|
| `/qdrant_db/` | 400 MB | ~100 | Vector database |
| `/coordination/` | 56 MB | 48 | Primary outputs |
| `/handoff-binder/` | ~500 KB | 8 | Prosecution package |
| `/scripts/` | 712 KB | 30+ | Automation |
| `/state/` | 144 KB | 21 | Agent states |
| `/agents/` | ~200 KB | 30+ | Agent contexts |
| `/docs/` | ~300 KB | 15+ | Documentation |
| **TOTAL** | **~456 MB** | **170+** | Full package |

*(Excludes corpus: 1.6 GB in `/Users/breydentaylor/certainly/shurka-dump/`)*

---

## 🔍 **FILE NAMING CONVENTIONS**

### **Evidence Files**
- `evidence_inventory_v{N}.json` - Master evidence catalog
- `PILLAR_{ID}_{name}.json` - Evidence pillar data
- `pillar_{name}.json` - Pillar discovery outputs

### **Analysis Files**
- `cert_file_chunks.json` - CERT file organization
- `html_{type}.json` - NLP analysis outputs
- `semantic_clusters.json` - Clustering results
- `network_*.{format}` - Network analysis

### **Visualizations**
- `wordcloud_{chunk/global}_{name}.png` - Word clouds
- `indicator_{type}.png` - Statistical charts
- `cluster_{type}.png` - Cluster visualizations
- `network_{type}.png` - Network graphs

### **State Files**
- `{agent_name}.state.json` - Individual agent state
- `autonomous_phases.json` - Phase controller
- `cert_analytics_state.json` - CERT mission

### **Documentation**
- `UPPERCASE.md` - Major reports/guides
- `{component}_README.md` - Component guides
- `{agent}_EXECUTIVE_SUMMARY.md` - Agent summaries

---

## 🎯 **KEY FILE LOCATIONS**

| What You Need | File Location |
|---------------|---------------|
| **Master Evidence Catalog** | `coordination/evidence_inventory_v4.json` |
| **Prosecution Package** | `handoff-binder/` (all 8 files) |
| **Semantic Search** | `scripts/search_corpus.py` |
| **Word Clouds** | `coordination/wordcloud_*.png` (17 files) |
| **Interactive Network** | `coordination/network_interactive.html` |
| **Citations** | `coordination/citation_database.json` |
| **Court Cases** | `coordination/PILLAR_09_LEGAL_PROCEEDINGS.json` |
| **Victim Testimony** | `coordination/reddit_victim_*.json` |
| **YouTube Violations** | `coordination/youtube_fraud_analysis.json` |
| **Agent Status** | `state/cert_analytics_state.json` |

---

## 📋 **QUICK NAVIGATION**

### **For Legal Team**
1. Start with `handoff-binder/PHASE4_EXECUTIVE_SUMMARY.md`
2. Review `coordination/evidence_inventory_v4.json`
3. View visualizations in `coordination/wordcloud_*.png`
4. Check court cases in `coordination/PILLAR_09_LEGAL_PROCEEDINGS.json`

### **For Technical Analysis**
1. Use `scripts/search_corpus.py` for semantic search
2. Load `coordination/network_graph.graphml` in Gephi
3. Review `coordination/semantic_clusters.json` for themes
4. Check `coordination/citation_database.json` for provenance

### **For AI Agents**
1. Read `AI_AGENT_README.md` for operational guide
2. Check `state/` for agent completion status
3. Use functions in `AI_AGENT_README.md` for queries
4. Follow agent context files in `agents/`

---

## 🔄 **VERSION HISTORY**

- **v4**: Current (CERT analytics + 3 new pillars)
- **v3**: Reddit victim integration
- **v2**: Phase 4 gap filling complete
- **v1**: Initial Phase 3 validation

---

**Last Updated**: 2025-11-21T09:15:00Z
**Total Files**: 170+
**Total Size**: 456 MB (outputs)
**Status**: Production-ready ✅
