#!/usr/bin/env python3
"""
Generate gaps report - what's missing, needs OSINT, or requires manual investigation.

Purpose:
- Identify rejected evidence that might be salvageable with more OSINT
- Document flagged items requiring manual review
- Highlight data quality issues
- Suggest Phase 3 focus areas

Why this matters:
- Guides manual investigation (where to look next)
- Informs Phase 3 agent deployment (what gaps to fill)
- Prevents premature closure (might be missing key evidence)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def identify_gaps(validation_results: Dict, global_scope: Dict) -> Dict:
    """Identify evidence gaps and investigation priorities."""

    rejected = validation_results["rejected"]
    flagged = validation_results["flagged"]

    gaps = {
        "gaps_metadata": {
            "generated_at": datetime.now().isoformat(),
            "purpose": "Evidence gaps requiring OSINT or manual investigation"
        },
        "high_priority_gaps": [],
        "flagged_items_needing_review": [],
        "data_quality_issues": global_scope.get("data_quality_issues", []),
        "missing_evidence_types": [],
        "osint_opportunities": []
    }

    # Gap 1: Rejected blockchain evidence (might have tx_hash in corpus)
    rejected_blockchain = [
        {"evidence_id": eid, "metadata": ev.get("metadata", {})}
        for eid, ev in rejected.items()
        if ev.get("category") == "blockchain"
    ]

    if rejected_blockchain:
        gaps["high_priority_gaps"].append({
            "gap": "Rejected blockchain transactions",
            "count": len(rejected_blockchain),
            "severity": "high",
            "action": "Search corpus for tx_hash - might be extractable from binder or raw files",
            "affected_evidence": [item["evidence_id"] for item in rejected_blockchain[:10]]
        })

    # Gap 2: Flagged items with 2 sources (close to admission threshold)
    nearly_admitted = [
        {"evidence_id": eid, "source_count": ev.get("validation", {}).get("source_count", 0)}
        for eid, ev in flagged.items()
        if ev.get("validation", {}).get("source_count", 0) == 2
    ]

    if nearly_admitted:
        gaps["flagged_items_needing_review"].append({
            "category": "Near-threshold evidence (2 sources)",
            "count": len(nearly_admitted),
            "action": "Manual review - might find 3rd source with deeper corpus search",
            "items": [item["evidence_id"] for item in nearly_admitted[:10]]
        })

    # Gap 3: Missing evidence types (URL, binder)
    admitted = validation_results["admitted"]
    evidence_by_category = {}
    for ev in admitted.values():
        category = ev.get("category", "unknown")
        evidence_by_category[category] = evidence_by_category.get(category, 0) + 1

    expected_categories = ["blockchain", "entities", "telegram", "urls", "binder"]
    for expected in expected_categories:
        if evidence_by_category.get(expected, 0) == 0:
            gaps["missing_evidence_types"].append({
                "category": expected,
                "status": "No admitted evidence",
                "action": f"Phase 3 agent should focus on {expected} extraction with corpus validation"
            })

    # Gap 4: Entity coverage (entities mentioned but not validated)
    validated_entities = set()
    for ev in admitted.values():
        if "entity_name" in ev.get("metadata", {}):
            validated_entities.add(ev["metadata"]["entity_name"])

    # Assuming we want Jason Shurka, Esther Zernitsky, Ally Thompson, UNIFYD
    key_entities = ["Jason Shurka", "Esther Zernitsky", "Ally Thompson", "UNIFYD", "Light System"]
    missing_key_entities = [e for e in key_entities if e not in validated_entities]

    if missing_key_entities:
        gaps["high_priority_gaps"].append({
            "gap": "Missing key entity validation",
            "entities": missing_key_entities,
            "severity": "high",
            "action": "Entity_Linker should focus on corpus mentions of these entities"
        })

    # Gap 5: OSINT opportunities (rejected items with some metadata)
    osint_candidates = [
        {"evidence_id": eid, "metadata": ev.get("metadata", {})}
        for eid, ev in rejected.items()
        if ev.get("metadata", {}).get("from_address")  # Has wallet but no corpus match
        or ev.get("metadata", {}).get("url")  # Has URL but not in corpus
    ]

    if osint_candidates:
        gaps["osint_opportunities"].append({
            "category": "Rejected items with partial metadata",
            "count": len(osint_candidates),
            "action": "Manual OSINT search for wallet addresses/URLs in blockchain explorers, web archives",
            "sample_items": [item["evidence_id"] for item in osint_candidates[:5]]
        })

    # Summary stats
    gaps["summary"] = {
        "total_gaps_identified": (
            len(gaps["high_priority_gaps"]) +
            len(gaps["missing_evidence_types"]) +
            len(gaps["osint_opportunities"])
        ),
        "flagged_items_count": len(flagged),
        "rejected_items_count": len(rejected),
        "recommended_next_steps": [
            "Run manual review on flagged items (Script 5)",
            "Deploy Phase 3 agents with focus on missing evidence types",
            "Conduct OSINT on rejected blockchain/URL evidence",
            "Re-run extraction with improved corpus validation"
        ]
    }

    return gaps


def main():
    # Paths
    validation_path = "/Users/breydentaylor/certainly/visualizations/coordination/validated_evidence.json"
    global_scope_path = "/Users/breydentaylor/certainly/visualizations/coordination/global_scope_state.json"
    gaps_path = "/Users/breydentaylor/certainly/visualizations/memory/gaps.json"

    # Ensure directory exists
    Path(gaps_path).parent.mkdir(parents=True, exist_ok=True)

    # Load validation results
    print(f"Loading validation results from: {validation_path}")
    with open(validation_path, 'r') as f:
        validation_results = json.load(f)

    # Load global scope
    print(f"Loading global scope from: {global_scope_path}")
    with open(global_scope_path, 'r') as f:
        global_scope = json.load(f)

    # Identify gaps
    print("\n🔍 Identifying evidence gaps...")
    gaps = identify_gaps(validation_results, global_scope)

    # Write gaps
    print(f"✅ Writing gaps report to: {gaps_path}")
    with open(gaps_path, 'w') as f:
        json.dump(gaps, f, indent=2)

    # Print summary
    print(f"\n📊 Gaps Summary:")
    print(f"   Total gaps identified: {gaps['summary']['total_gaps_identified']}")
    print(f"   Flagged items: {gaps['summary']['flagged_items_count']}")
    print(f"   Rejected items: {gaps['summary']['rejected_items_count']}")

    if gaps["high_priority_gaps"]:
        print(f"\n   ⚠️  High Priority Gaps:")
        for gap in gaps["high_priority_gaps"]:
            print(f"      - {gap['gap']}: {gap.get('count', 'N/A')} items")

    if gaps["missing_evidence_types"]:
        print(f"\n   📋 Missing Evidence Types:")
        for missing in gaps["missing_evidence_types"]:
            print(f"      - {missing['category']}")

    print(f"\n   🎯 Recommended Next Steps:")
    for step in gaps["summary"]["recommended_next_steps"]:
        print(f"      - {step}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
