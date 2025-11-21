#!/usr/bin/env python3
"""
Evidence Integrator - Merges CERT analytics into master evidence inventory
Version: 6.0
Mission: Create evidence_inventory_v6.json with full CERT enrichments
"""

import json
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path("/Users/breydentaylor/certainly/visualizations")
COORD_DIR = BASE_DIR / "coordination"
STATE_DIR = BASE_DIR / "state"

# Input files
EVIDENCE_V4 = COORD_DIR / "evidence_inventory_v4.json"
CORPUS_MAPPING = COORD_DIR / "evidence_to_corpus_mapping.json"
SEMANTIC_CLUSTERS = COORD_DIR / "semantic_clusters.json"
NETWORK_STATS = COORD_DIR / "network_statistics.json"
CITATION_DB = COORD_DIR / "citation_database.json"
WORD_FREQ = COORD_DIR / "html_word_frequencies.json"
INDICATOR_COUNTS = COORD_DIR / "html_indicator_counts.json"

# Output
EVIDENCE_V6 = COORD_DIR / "evidence_inventory_v6.json"
STATE_FILE = STATE_DIR / "evidence_integrator.state.json"

def load_json(path):
    """Load JSON file with error handling"""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  File not found: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON decode error in {path}: {e}")
        return None

def save_json(data, path):
    """Save JSON with formatting"""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved: {path}")

def enrich_with_corpus_mapping(items, corpus_mapping):
    """Add corpus source citations to evidence items"""
    enriched = 0
    new_items = []

    for term, data in corpus_mapping.items():
        match_count = data.get('match_count', 0)
        unique_files = data.get('unique_files', 0)

        if match_count > 0:
            # Create new evidence item for high-value corpus findings
            if match_count >= 100 or unique_files >= 3:
                new_items.append({
                    "evidence_id": f"CORPUS_{term.upper().replace(' ', '_')}",
                    "type": "Corpus Analysis - High-Frequency Indicator",
                    "tier": 2 if match_count >= 500 else 3,
                    "pillar": "PILLAR_01_blockchain_transactions" if data['term_type'] == 'wallet_addresses' else "PILLAR_02_shadowlens_summaries",
                    "description": f"Corpus analysis identified '{term}' in {match_count} occurrences across {unique_files} unique files",
                    "prosecution_value": min(10, match_count // 100),
                    "corpus_sources": [
                        {
                            "file": match['file'],
                            "line": match['line'],
                            "context": match['context'][:200]
                        }
                        for match in data.get('matches', [])[:10]  # Top 10 matches
                    ],
                    "cert_analytics": {
                        "indicator_type": data['term_type'],
                        "total_matches": match_count,
                        "unique_files": unique_files,
                        "discovery_method": "CERT Corpus Mapper v2.0"
                    }
                })
                enriched += 1

    return new_items, enriched

def enrich_with_semantic_clusters(items, clusters_data):
    """Add semantic cluster metadata"""
    enriched = 0
    cluster_mapping = {}

    # Build cluster theme map
    for cluster in clusters_data.get('clusters', []):
        theme = cluster.get('primary_theme', 'unknown')
        cluster_mapping[theme] = {
            'cluster_id': cluster.get('cluster_id'),
            'size': cluster.get('size', 0),
            'themes': cluster.get('all_themes', [])
        }

    # Enrich existing items
    for item in items:
        # Match item type to cluster theme
        item_type = item.get('type', '').lower()

        for theme, cluster_info in cluster_mapping.items():
            if theme in item_type or any(t['theme'] in item_type for t in cluster_info['themes']):
                if 'cert_analytics' not in item:
                    item['cert_analytics'] = {}

                item['cert_analytics']['semantic_cluster'] = {
                    'cluster_id': cluster_info['cluster_id'],
                    'primary_theme': theme,
                    'cluster_size': cluster_info['size'],
                    'discovery_method': 'CERT Semantic Clusterer v1.0'
                }
                enriched += 1
                break

    return enriched

def enrich_with_network_stats(items, network_stats):
    """Add network centrality data"""
    if not network_stats:
        return 0

    enriched = 0
    centrality = network_stats.get('centrality', {})

    for item in items:
        # Check if item involves high-centrality entities
        desc = item.get('description', '').lower()

        for entity, score in centrality.get('degree', {}).items():
            if entity.lower() in desc:
                if 'cert_analytics' not in item:
                    item['cert_analytics'] = {}

                item['cert_analytics']['network_analysis'] = {
                    'entity': entity,
                    'centrality_score': score,
                    'network_importance': 'high' if score > 0.3 else 'medium' if score > 0.1 else 'low',
                    'discovery_method': 'CERT Network Grapher v1.0'
                }
                enriched += 1
                break

    return enriched

def enrich_with_citations(items, citation_db):
    """Add citation provenance"""
    if not citation_db:
        return 0

    enriched = 0
    citations = citation_db.get('citations', [])

    for item in items:
        # Match citations to evidence items
        item_id = item.get('evidence_id', '')

        for citation in citations:
            if citation.get('evidence_id') == item_id or citation.get('related_evidence_id') == item_id:
                if 'provenance' not in item:
                    item['provenance'] = []

                item['provenance'].append({
                    'citation_id': citation.get('citation_id'),
                    'file_path': citation.get('file_path'),
                    'sha256': citation.get('sha256'),
                    'discovery_method': 'CERT Citation Linker v1.0'
                })
                enriched += 1

    return enriched

def enrich_with_indicator_analysis(items, word_freq, indicator_counts):
    """Add NLP indicator analysis"""
    if not indicator_counts:
        return 0

    enriched = 0
    indicator_data = indicator_counts.get('indicator_counts', {})

    # Create new evidence items for high-frequency indicators
    new_items = []

    for indicator, count in indicator_data.items():
        if count >= 1000:  # High-frequency threshold
            new_items.append({
                "evidence_id": f"NLP_{indicator.upper().replace(' ', '_')}",
                "type": "NLP Analysis - High-Frequency Indicator",
                "tier": 2 if count >= 10000 else 3,
                "pillar": "PILLAR_02_shadowlens_summaries",
                "description": f"NLP analysis identified '{indicator}' in {count} occurrences across HTML corpus",
                "prosecution_value": min(10, count // 1000),
                "cert_analytics": {
                    "indicator_type": "frequency_analysis",
                    "total_occurrences": count,
                    "discovery_method": "CERT HTML Analyzer v1.0"
                }
            })
            enriched += 1

    return new_items, enriched

def create_v6_inventory():
    """Main integration function"""
    print("🔬 EVIDENCE INTEGRATOR v6.0")
    print("=" * 60)

    # Load all data
    print("\n📥 Loading data files...")
    v4_data = load_json(EVIDENCE_V4)
    corpus_mapping = load_json(CORPUS_MAPPING)
    clusters_data = load_json(SEMANTIC_CLUSTERS)
    network_stats = load_json(NETWORK_STATS)
    citation_db = load_json(CITATION_DB)
    word_freq = load_json(WORD_FREQ)
    indicator_counts = load_json(INDICATOR_COUNTS)

    if not v4_data:
        print("❌ Cannot load v4 evidence inventory!")
        return

    # Extract existing evidence items
    evidence_items = v4_data.get('evidence', [])
    starting_count = len(evidence_items)
    print(f"   Starting with {starting_count} evidence items from v4")

    # Enrichment pipeline
    enrichments = {
        'corpus_mapping': 0,
        'semantic_clusters': 0,
        'network_stats': 0,
        'citations': 0,
        'indicator_analysis': 0,
        'new_items': 0
    }

    # 1. Corpus mapping enrichment
    if corpus_mapping:
        print("\n🔗 Enriching with corpus mapping...")
        new_corpus_items, count = enrich_with_corpus_mapping(evidence_items, corpus_mapping)
        evidence_items.extend(new_corpus_items)
        enrichments['corpus_mapping'] = count
        enrichments['new_items'] += len(new_corpus_items)
        print(f"   Added {len(new_corpus_items)} new corpus-derived evidence items")
        print(f"   Enriched {count} existing items with corpus citations")

    # 2. Semantic cluster enrichment
    if clusters_data:
        print("\n🧬 Enriching with semantic clusters...")
        count = enrich_with_semantic_clusters(evidence_items, clusters_data)
        enrichments['semantic_clusters'] = count
        print(f"   Enriched {count} items with cluster metadata")

    # 3. Network analysis enrichment
    if network_stats:
        print("\n🕸️  Enriching with network statistics...")
        count = enrich_with_network_stats(evidence_items, network_stats)
        enrichments['network_stats'] = count
        print(f"   Enriched {count} items with network centrality")

    # 4. Citation enrichment
    if citation_db:
        print("\n📚 Enriching with citations...")
        count = enrich_with_citations(evidence_items, citation_db)
        enrichments['citations'] = count
        print(f"   Enriched {count} items with provenance citations")

    # 5. Indicator analysis enrichment
    if indicator_counts:
        print("\n📊 Enriching with NLP indicators...")
        new_nlp_items, count = enrich_with_indicator_analysis(evidence_items, word_freq, indicator_counts)
        evidence_items.extend(new_nlp_items)
        enrichments['indicator_analysis'] = count
        enrichments['new_items'] += len(new_nlp_items)
        print(f"   Added {len(new_nlp_items)} new NLP-derived evidence items")

    # Calculate tier distribution
    tier_distribution = {
        'tier1': sum(1 for item in evidence_items if item.get('tier') == 1),
        'tier2': sum(1 for item in evidence_items if item.get('tier') == 2),
        'tier3': sum(1 for item in evidence_items if item.get('tier') == 3),
        'tier4': sum(1 for item in evidence_items if item.get('tier') == 4),
        'tier5': sum(1 for item in evidence_items if item.get('tier') == 5)
    }

    # Calculate prosecution readiness
    prosecution_ready = tier_distribution['tier1'] + tier_distribution['tier2']
    total_items = len(evidence_items)
    readiness_pct = (prosecution_ready / total_items * 100) if total_items > 0 else 0

    # Build v6 inventory
    v6_inventory = {
        "version": "6.0",
        "created": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "phase": "Phase 6: CERT Analytics Integration Complete",
        "agent": "Evidence_Integrator",
        "previous_version": "coordination/evidence_inventory_v4.json",
        "update_type": "Type 6 CERT Analytics Full Integration",

        "summary": {
            "total_items": total_items,
            "items_added": enrichments['new_items'],
            "items_enriched": sum(enrichments.values()) - enrichments['new_items'],
            "tier1_items": tier_distribution['tier1'],
            "tier2_items": tier_distribution['tier2'],
            "tier3_items": tier_distribution['tier3'],
            "tier4_items": tier_distribution['tier4'],
            "tier5_items": tier_distribution['tier5'],
            "prosecution_ready_items": prosecution_ready,
            "prosecution_readiness_pct": round(readiness_pct, 1)
        },

        "cert_analytics_integration": {
            "corpus_mapping_enrichments": enrichments['corpus_mapping'],
            "semantic_cluster_enrichments": enrichments['semantic_clusters'],
            "network_analysis_enrichments": enrichments['network_stats'],
            "citation_enrichments": enrichments['citations'],
            "nlp_indicator_enrichments": enrichments['indicator_analysis'],
            "total_new_evidence_items": enrichments['new_items'],
            "total_enrichments": sum(enrichments.values()) - enrichments['new_items'],

            "data_sources": {
                "corpus_mapper": str(CORPUS_MAPPING),
                "semantic_clusterer": str(SEMANTIC_CLUSTERS),
                "network_grapher": str(NETWORK_STATS),
                "citation_linker": str(CITATION_DB),
                "html_analyzer": str(INDICATOR_COUNTS)
            }
        },

        "evidence": evidence_items
    }

    # Save v6 inventory
    print("\n💾 Saving evidence_inventory_v6.json...")
    save_json(v6_inventory, EVIDENCE_V6)

    # Save state
    state = {
        "agent": "Evidence_Integrator",
        "status": "completed",
        "started_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "completed_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items_processed": total_items,
        "items_added": enrichments['new_items'],
        "enrichments_applied": sum(enrichments.values()) - enrichments['new_items'],
        "output_file": str(EVIDENCE_V6),
        "metrics": enrichments
    }
    save_json(state, STATE_FILE)

    # Print summary
    print("\n" + "=" * 60)
    print("✅ EVIDENCE INTEGRATION COMPLETE")
    print("=" * 60)
    print(f"\n📊 RESULTS:")
    print(f"   Starting items (v4): {starting_count}")
    print(f"   New items added: {enrichments['new_items']}")
    print(f"   Total items (v6): {total_items}")
    print(f"   Items enriched: {sum(enrichments.values()) - enrichments['new_items']}")
    print(f"\n🎯 TIER DISTRIBUTION:")
    print(f"   Tier 1 (Critical): {tier_distribution['tier1']}")
    print(f"   Tier 2 (High): {tier_distribution['tier2']}")
    print(f"   Tier 3 (Medium): {tier_distribution['tier3']}")
    print(f"   Tier 4 (Low): {tier_distribution['tier4']}")
    print(f"   Tier 5 (Minimal): {tier_distribution['tier5']}")
    print(f"\n📈 PROSECUTION READINESS:")
    print(f"   Ready items (T1+T2): {prosecution_ready}")
    print(f"   Readiness: {readiness_pct:.1f}%")
    print(f"\n📁 OUTPUT:")
    print(f"   {EVIDENCE_V6}")
    print(f"   {STATE_FILE}")
    print("\n🎯 CERT ANALYTICS INTEGRATION COMPLETE!\n")

if __name__ == "__main__":
    create_v6_inventory()
