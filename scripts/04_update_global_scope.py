#!/usr/bin/env python3
"""
Update global scope state for next agent run.

Purpose:
- Read validation results (admitted/rejected/flagged)
- Write coordination files that Phase 3 agents will read
- Update agent constraints based on validation outcomes
- Track data quality issues

Why this matters:
- Agents need to know what to focus on (validated items only)
- Prevents rework on rejected evidence
- Documents gaps for manual investigation
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def generate_agent_constraints(validation_results: Dict) -> Dict:
    """Generate agent-specific constraints based on validation results."""

    admitted = validation_results["admitted"]
    rejected = validation_results["rejected"]
    flagged = validation_results["flagged"]

    constraints = {}

    # Blockchain_Forensics constraints
    blockchain_admitted = [
        eid for eid, ev in admitted.items()
        if ev.get("category") == "blockchain"
    ]
    blockchain_rejected = [
        eid for eid, ev in rejected.items()
        if ev.get("category") == "blockchain"
    ]

    constraints["Blockchain_Forensics"] = {
        "focus_on": blockchain_admitted,
        "skip": blockchain_rejected,
        "requirement": "Extract tx_hash for all transactions - missing tx_hash caused rejections",
        "stats": {
            "admitted": len(blockchain_admitted),
            "rejected": len(blockchain_rejected)
        }
    }

    # Entity_Linker constraints
    entity_admitted = [
        eid for eid, ev in admitted.items()
        if ev.get("category") == "entities"
    ]

    constraints["Entity_Linker"] = {
        "validated_entities": [
            ev["metadata"]["entity_name"]
            for ev in admitted.values()
            if "entity_name" in ev.get("metadata", {})
        ],
        "requirement": "Focus only on entities with 3+ corpus mentions",
        "stats": {
            "validated_entities": len(entity_admitted)
        }
    }

    # TIER_Auditor constraints
    constraints["TIER_Auditor"] = {
        "pre_approved": list(admitted.keys()),
        "manual_review_queue": list(flagged.keys()),
        "auto_reject": list(rejected.keys()),
        "requirement": "Deep dive only on flagged items - admitted items are corpus-backed",
        "stats": {
            "pre_approved": len(admitted),
            "needs_review": len(flagged),
            "auto_rejected": len(rejected)
        }
    }

    # URL_Analyst constraints
    url_admitted = [
        eid for eid, ev in admitted.items()
        if ev.get("category") == "urls"
    ]

    constraints["URL_Analyst"] = {
        "validated_urls": url_admitted,
        "requirement": "URLs already validated - focus on new URLs only",
        "stats": {
            "validated": len(url_admitted)
        }
    }

    return constraints


def identify_data_quality_issues(validation_results: Dict) -> List[Dict]:
    """Identify patterns in rejected evidence."""

    rejected = validation_results["rejected"]
    issues = []

    # Issue 1: Missing tx_hash (blockchain)
    missing_tx_hash = [
        eid for eid, ev in rejected.items()
        if ev.get("category") == "blockchain"
        and "tx_hash" not in ev.get("metadata", {})
    ]

    if missing_tx_hash:
        issues.append({
            "issue": "Missing tx_hash in blockchain evidence",
            "count": len(missing_tx_hash),
            "severity": "high",
            "action": "Re-run Blockchain_Forensics with tx_hash extraction from CSVs",
            "affected_evidence": missing_tx_hash[:10]  # Sample
        })

    # Issue 2: Placeholder evidence (zero amounts)
    placeholder_evidence = [
        eid for eid, ev in rejected.items()
        if ev.get("metadata", {}).get("amount_usd") == 0
        or ev.get("metadata", {}).get("total_volume") == 0
    ]

    if placeholder_evidence:
        issues.append({
            "issue": "Placeholder evidence with zero amounts",
            "count": len(placeholder_evidence),
            "severity": "medium",
            "action": "Remove placeholder items or populate with real data",
            "affected_evidence": placeholder_evidence[:10]
        })

    # Issue 3: Unknown entities/platforms
    unknown_items = [
        eid for eid, ev in rejected.items()
        if ev.get("metadata", {}).get("entity_name") == "unknown"
        or ev.get("metadata", {}).get("exchange") == "unknown"
    ]

    if unknown_items:
        issues.append({
            "issue": "Evidence with 'unknown' identifiers",
            "count": len(unknown_items),
            "severity": "low",
            "action": "Improve entity extraction or remove if no attribution possible",
            "affected_evidence": unknown_items[:10]
        })

    return issues


def main():
    # Paths
    validation_path = "/Users/breydentaylor/certainly/visualizations/coordination/validated_evidence.json"
    global_scope_path = "/Users/breydentaylor/certainly/visualizations/coordination/global_scope_state.json"
    checkpoint_path = "/Users/breydentaylor/certainly/visualizations/memory/validation_checkpoint.json"

    # Ensure directories exist
    Path(global_scope_path).parent.mkdir(parents=True, exist_ok=True)
    Path(checkpoint_path).parent.mkdir(parents=True, exist_ok=True)

    # Load validation results
    print(f"Loading validation results from: {validation_path}")
    with open(validation_path, 'r') as f:
        validation_results = json.load(f)

    # Generate agent constraints
    print("\n📋 Generating agent constraints...")
    agent_constraints = generate_agent_constraints(validation_results)

    # Identify data quality issues
    print("🔍 Identifying data quality issues...")
    quality_issues = identify_data_quality_issues(validation_results)

    # Build global scope state
    global_scope = {
        "last_updated": datetime.now().isoformat(),
        "validation_summary": validation_results["validation_metadata"],
        "agent_constraints": agent_constraints,
        "data_quality_issues": quality_issues,
        "next_phase_ready": len(validation_results["admitted"]) > 0,
        "manual_review_required": len(validation_results["flagged"]) > 0
    }

    # Write global scope state
    print(f"\n✅ Writing global scope state to: {global_scope_path}")
    with open(global_scope_path, 'w') as f:
        json.dump(global_scope, f, indent=2)

    # Write checkpoint for agents
    checkpoint = {
        "validation_phase_complete": True,
        "timestamp": datetime.now().isoformat(),
        "admitted_evidence_count": len(validation_results["admitted"]),
        "flagged_evidence_count": len(validation_results["flagged"]),
        "rejected_evidence_count": len(validation_results["rejected"]),
        "ready_for_phase3": True
    }

    print(f"✅ Writing validation checkpoint to: {checkpoint_path}")
    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)

    # Print summary
    print(f"\n📊 Global Scope Summary:")
    print(f"   Validation complete: {checkpoint['validation_phase_complete']}")
    print(f"   Admitted evidence: {checkpoint['admitted_evidence_count']}")
    print(f"   Flagged for review: {checkpoint['flagged_evidence_count']}")
    print(f"   Rejected: {checkpoint['rejected_evidence_count']}")
    print(f"   Ready for Phase 3: {checkpoint['ready_for_phase3']}")

    if quality_issues:
        print(f"\n⚠️  Data Quality Issues Identified: {len(quality_issues)}")
        for issue in quality_issues:
            print(f"   - {issue['issue']}: {issue['count']} items ({issue['severity']} severity)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
