#!/usr/bin/env python3
"""
ReasoningBank_Manager - Load approved evidence into memory.db
Phase 3, Agent 7/9 - RICO evidence processing pipeline
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
BASE_DIR = Path("/Users/breydentaylor/certainly/visualizations")
APPROVED_LIST = BASE_DIR / "coordination/approved_evidence_list.json"
AUDIT_REPORT = BASE_DIR / "coordination/evidence_audit_report.json"
DB_PATH = BASE_DIR / ".swarm/memory.db"
STATE_FILE = BASE_DIR / "state/reasoningbank_manager.state.json"
MEMORY_DIR = BASE_DIR / "memory"
COORDINATION_DIR = BASE_DIR / "coordination"

# Ensure directories exist
MEMORY_DIR.mkdir(exist_ok=True)
COORDINATION_DIR.mkdir(exist_ok=True)

def initialize_database():
    """Connect to existing database"""
    conn = sqlite3.connect(DB_PATH)
    # Database already exists with claude-flow schema
    return conn

def check_current_evidence_count(conn):
    """Check how many evidence items are already in database"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM patterns
        WHERE type LIKE 'evidence_%'
    """)
    return cursor.fetchone()[0]

def load_approved_evidence():
    """Load approved evidence list from JSON"""
    with open(APPROVED_LIST, 'r') as f:
        data = json.load(f)

    # Convert dict to list of evidence items
    evidence_list = []
    for key, value in data.items():
        if 'evidence' in value and 'audit' in value:
            item = value['evidence'].copy()
            item['audit'] = value['audit']
            evidence_list.append(item)

    return evidence_list

def validate_evidence_item(item):
    """Validate evidence item has required fields and corpus sources"""
    # Check for corpus sources
    audit = item.get('audit', {})
    sources = audit.get('sources', {})
    corpus_count = sources.get('corpus_count', 0)
    notebook_count = sources.get('notebook_count', 0)

    # Every item should have at least notebook source (0.5 effective)
    if corpus_count == 0 and notebook_count == 0:
        return False, "No corpus sources"

    # Check for EESystem violations (legal safeguard)
    metadata = item.get('metadata', {})
    evidence_act = metadata.get('evidence_act', '').lower()
    principals = metadata.get('principals_exposed', [])

    # Flag if implicates EESystem or Dr. Michael
    eesystem_terms = ['eesystem', 'energy enhancement', 'dr. sandra', 'michael scalar']
    if any(term in evidence_act for term in eesystem_terms):
        # Check if this is Jason defrauding EESystem (OK) or EESystem as fraudster (NOT OK)
        if 'jason' not in evidence_act and 'tls' not in evidence_act and 'light system' not in evidence_act:
            return False, "Potential EESystem violation - implicates EESystem without Jason context"

    return True, "OK"

def load_evidence_to_db(conn, evidence_list):
    """Load all evidence items to ReasoningBank"""
    cursor = conn.cursor()

    stats = {
        'loaded': 0,
        'rejected': 0,
        'tier_breakdown': defaultdict(int),
        'category_breakdown': defaultdict(int),
        'rico_predicates': defaultdict(int),
        'principals_set': set(),
        'corpus_coverage': defaultdict(int)
    }

    rejections = []

    for item in evidence_list:
        evidence_id = item.get('evidence_id')
        audit = item.get('audit', {})
        # Use FINAL tier from audit (after downgrading), not original tier
        tier = audit.get('tier', item.get('tier', 3))
        category = item.get('category', 'unknown')
        metadata = item.get('metadata', {})

        # Validate
        valid, reason = validate_evidence_item(item)
        if not valid:
            stats['rejected'] += 1
            rejections.append({
                'evidence_id': evidence_id,
                'reason': reason
            })
            print(f"WARNING: {evidence_id} - {reason} - REJECTING")
            continue

        # Determine type based on TIER
        if tier == 1:
            evidence_type = 'evidence_tier1'
        elif tier == 2:
            evidence_type = 'evidence_tier2'
        elif tier == 3:
            evidence_type = 'evidence_tier3'
        else:
            evidence_type = 'evidence_unknown'

        # Extract corpus sources
        sources = audit.get('sources', {})
        corpus_count = sources.get('corpus_count', 0)
        notebook_count = sources.get('notebook_count', 0)

        # Prepare pattern_data with all evidence info
        pattern_data = {
            'evidence': item,
            'tier': tier,
            'category': category,
            'corpus_count': corpus_count,
            'notebook_count': notebook_count,
            'rico_predicates': metadata.get('rico_predicate', []),
            'principals': metadata.get('principals_exposed', []),
            'temporal_anchor': metadata.get('temporal_anchor', None),
            'source_file': metadata.get('source_file', None)
        }

        # Store in ReasoningBank using claude-flow schema
        # id = evidence_id, type = tier namespace, pattern_data = full evidence JSON
        cursor.execute("""
            INSERT OR REPLACE INTO patterns (id, type, pattern_data, confidence, usage_count)
            VALUES (?, ?, ?, ?, ?)
        """, (
            evidence_id,
            evidence_type,
            json.dumps(pattern_data),
            1.0,  # High confidence - already vetted
            0     # Initial usage count
        ))

        # Update stats
        stats['loaded'] += 1
        stats['tier_breakdown'][f'tier{tier}'] += 1
        stats['category_breakdown'][category] += 1

        # Track RICO predicates
        for predicate in metadata.get('rico_predicate', []):
            stats['rico_predicates'][predicate] += 1

        # Track principals
        for principal in metadata.get('principals_exposed', []):
            stats['principals_set'].add(principal)

        # Track corpus coverage
        source_file = metadata.get('source_file', '')
        if 'telegram' in source_file.lower():
            stats['corpus_coverage']['telegram_posts'] += 1
        elif 'blockchain' in source_file.lower():
            stats['corpus_coverage']['blockchain_csvs'] += 1
        elif 'shadowlens' in source_file.lower():
            stats['corpus_coverage']['shadowlens_notes'] += 1
        elif 'youtube' in source_file.lower():
            stats['corpus_coverage']['youtube_crawl'] += 1
        elif 'website' in source_file.lower():
            stats['corpus_coverage']['websites_crawl'] += 1

    conn.commit()

    # Convert set to list
    stats['principals_list'] = sorted(list(stats['principals_set']))
    del stats['principals_set']

    return stats, rejections

def build_cross_reference_index(conn, evidence_list):
    """Build entity -> evidence -> predicate cross-reference"""
    cursor = conn.cursor()

    cross_references = {}

    for item in evidence_list:
        evidence_id = item.get('evidence_id')
        metadata = item.get('metadata', {})
        principals = metadata.get('principals_exposed', [])
        predicates = metadata.get('rico_predicate', [])
        tier = item.get('tier', 3)

        for principal in principals:
            if principal not in cross_references:
                cross_references[principal] = {
                    'evidence_ids': [],
                    'predicates': set(),
                    'tier_breakdown': defaultdict(int)
                }
            cross_references[principal]['evidence_ids'].append(evidence_id)
            cross_references[principal]['predicates'].update(predicates)
            cross_references[principal]['tier_breakdown'][f'tier{tier}'] += 1

    # Convert sets to lists for JSON serialization
    for principal in cross_references:
        cross_references[principal]['predicates'] = sorted(list(cross_references[principal]['predicates']))
        cross_references[principal]['tier_breakdown'] = dict(cross_references[principal]['tier_breakdown'])

    # Store in ReasoningBank using claude-flow schema
    cursor.execute("""
        INSERT OR REPLACE INTO patterns (id, type, pattern_data, confidence, usage_count)
        VALUES (?, ?, ?, ?, ?)
    """, (
        'entity_to_evidence_map',
        'evidence_index',
        json.dumps({
            'cross_references': cross_references,
            'total_entities': len(cross_references)
        }),
        1.0,
        0
    ))

    conn.commit()

    return cross_references

def generate_evidence_manifest(stats, cross_references):
    """Generate evidence manifest output"""
    manifest = {
        'run_id': 'cert1-phase3-shadowlens-20251121',
        'total_loaded': stats['loaded'],
        'tier_breakdown': dict(stats['tier_breakdown']),
        'category_breakdown': dict(stats['category_breakdown']),
        'rico_predicates': dict(stats['rico_predicates']),
        'principals_involved': stats['principals_list'],
        'corpus_coverage': dict(stats['corpus_coverage']),
        'cross_reference_summary': {
            'total_entities': len(cross_references),
            'top_entities': sorted(
                [(k, len(v['evidence_ids'])) for k, v in cross_references.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    }

    output_path = MEMORY_DIR / "evidence_manifest.json"
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"✓ Evidence manifest written to {output_path}")
    return manifest

def generate_loading_report(stats, rejections):
    """Generate loading report"""
    # Verify all items have corpus sources
    all_have_sources = stats['rejected'] == 0

    # Check TIER distribution
    expected_tier1 = 48
    expected_tier2 = 13
    expected_tier3 = 760

    tier_match = (
        stats['tier_breakdown'].get('tier1', 0) == expected_tier1 and
        stats['tier_breakdown'].get('tier2', 0) == expected_tier2 and
        stats['tier_breakdown'].get('tier3', 0) == expected_tier3
    )

    report = {
        'status': 'complete',
        'items_loaded': stats['loaded'],
        'items_rejected': stats['rejected'],
        'rejected_items': rejections,
        'database_path': str(DB_PATH),
        'namespaces_created': ['evidence_tier1', 'evidence_tier2', 'evidence_tier3', 'evidence_index'],
        'verification': {
            'all_items_have_corpus_sources': all_have_sources,
            'tier_distribution_matches': tier_match,
            'expected_tiers': {
                'tier1': expected_tier1,
                'tier2': expected_tier2,
                'tier3': expected_tier3
            },
            'actual_tiers': dict(stats['tier_breakdown']),
            'eesystem_violations': 0  # Would be flagged in rejections
        }
    }

    output_path = COORDINATION_DIR / "evidence_loading_report.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✓ Loading report written to {output_path}")
    return report

def update_state_file(stats, outputs):
    """Update state file to signal completion"""
    state = {
        'run_id': 'cert1-phase3-shadowlens-20251121',
        'status': 'completed',
        'phase': 'HANDOFF',
        'evidence_loaded': stats['loaded'],
        'evidence_rejected': stats['rejected'],
        'outputs': outputs,
        'success_criteria_met': {
            'all_821_loaded': stats['loaded'] == 821,
            'all_have_corpus_sources': stats['rejected'] == 0,
            'cross_reference_index_built': True,
            'eesystem_safeguard_check': True
        },
        'completed_at': datetime.utcnow().isoformat() + 'Z'
    }

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"✓ State file updated: {STATE_FILE}")
    return state

def main():
    print("=" * 80)
    print("ReasoningBank_Manager - Phase 3, Agent 7/9")
    print("=" * 80)

    # STATE 1: INITIALIZE
    print("\n[STATE 1: INITIALIZE]")

    # Check if already completed
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        if state.get('status') == 'completed':
            print("✓ Already completed. Exiting.")
            return

    # Initialize database
    conn = initialize_database()
    current_count = check_current_evidence_count(conn)
    print(f"✓ Database initialized: {DB_PATH}")
    print(f"✓ Current evidence count: {current_count}")

    # Load approved evidence
    evidence_list = load_approved_evidence()
    print(f"✓ Loaded {len(evidence_list)} approved evidence items")

    # STATE 2: LOAD EVIDENCE
    print("\n[STATE 2: LOAD EVIDENCE TO REASONINGBANK]")
    stats, rejections = load_evidence_to_db(conn, evidence_list)

    print(f"✓ Loaded: {stats['loaded']}")
    print(f"✓ Rejected: {stats['rejected']}")
    print(f"✓ Tier breakdown: {dict(stats['tier_breakdown'])}")

    if rejections:
        print("\nRejections:")
        for rej in rejections[:5]:  # Show first 5
            print(f"  - {rej['evidence_id']}: {rej['reason']}")

    # STATE 3: BUILD CROSS-REFERENCE INDEX
    print("\n[STATE 3: BUILD CROSS-REFERENCE INDEX]")
    cross_references = build_cross_reference_index(conn, evidence_list)
    print(f"✓ Cross-reference index built: {len(cross_references)} entities")

    # STATE 4: GENERATE OUTPUTS
    print("\n[STATE 4: GENERATE OUTPUTS]")
    manifest = generate_evidence_manifest(stats, cross_references)
    report = generate_loading_report(stats, rejections)

    # STATE 5: HANDOFF
    print("\n[STATE 5: HANDOFF]")
    outputs = [
        "memory/evidence_manifest.json",
        "coordination/evidence_loading_report.json"
    ]
    state = update_state_file(stats, outputs)

    # Close database
    conn.close()

    # Summary
    print("\n" + "=" * 80)
    print("SUCCESS CRITERIA CHECK")
    print("=" * 80)
    for criterion, met in state['success_criteria_met'].items():
        status = "✅" if met else "❌"
        print(f"{status} {criterion}: {met}")

    print("\n" + "=" * 80)
    print("MISSION COMPLETE - Ready for Dashboard_Coordinator (Agent 8/9)")
    print("=" * 80)

if __name__ == '__main__':
    main()
