#!/usr/bin/env python3
"""
Generate canonical evidence manifest for prosecution.

Purpose:
- Extract ONLY admitted evidence (corpus-backed, validated)
- Format for prosecution readiness
- Add cross-references and RICO predicate mappings

Why this matters:
- This becomes the "ground truth" for Phase 3 swarm
- ReasoningBank_Manager loads ONLY items from this manifest
- Prosecutors use this as final evidence list
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def build_evidence_manifest(validation_results: Dict) -> Dict:
    """Build prosecution-ready evidence manifest from admitted items."""

    admitted = validation_results["admitted"]

    # Sort by TIER priority (TIER 1 = highest)
    tier_order = {"TIER 1": 1, "TIER 2": 2, "TIER 3": 3, "TIER 4": 4, "TIER 5": 5}
    sorted_evidence = sorted(
        admitted.items(),
        key=lambda x: tier_order.get(x[1].get("tier", "TIER 5"), 5)
    )

    manifest = {
        "manifest_metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_evidence": len(admitted),
            "validation_source": "validated_evidence.json",
            "purpose": "Prosecution-ready evidence with corpus backing"
        },
        "evidence_by_tier": {},
        "evidence_by_category": {},
        "rico_predicate_mapping": {},
        "top_entities": [],
        "evidence_items": {}
    }

    # Build evidence items with enhanced metadata
    for evidence_id, evidence in sorted_evidence:
        tier = evidence.get("tier", "TIER 5")
        category = evidence.get("category", "unknown")

        # Add to tier bucket
        if tier not in manifest["evidence_by_tier"]:
            manifest["evidence_by_tier"][tier] = []
        manifest["evidence_by_tier"][tier].append(evidence_id)

        # Add to category bucket
        if category not in manifest["evidence_by_category"]:
            manifest["evidence_by_category"][category] = []
        manifest["evidence_by_category"][category].append(evidence_id)

        # Map to RICO predicates
        predicates = []
        if category == "blockchain":
            predicates.append("money_laundering")
        if category in ["telegram", "urls"]:
            predicates.append("wire_fraud")
        if "medical" in str(evidence.get("metadata", {})).lower():
            predicates.extend(["wire_fraud", "fraudulent_claims"])

        for predicate in predicates:
            if predicate not in manifest["rico_predicate_mapping"]:
                manifest["rico_predicate_mapping"][predicate] = []
            manifest["rico_predicate_mapping"][predicate].append(evidence_id)

        # Store evidence with prosecution metadata
        manifest["evidence_items"][evidence_id] = {
            "tier": tier,
            "category": category,
            "rico_predicates": predicates,
            "metadata": evidence.get("metadata", {}),
            "corpus_sources": evidence.get("validation", {}).get("corpus_sources", []),
            "source_count": evidence.get("validation", {}).get("source_count", 0),
            "prosecution_ready": evidence.get("validation", {}).get("source_count", 0) >= 3
        }

    # Calculate TIER distribution
    manifest["tier_distribution"] = {
        tier: len(items) for tier, items in manifest["evidence_by_tier"].items()
    }

    # Calculate prosecution readiness
    prosecution_ready = sum(
        1 for ev in manifest["evidence_items"].values()
        if ev.get("prosecution_ready", False)
    )

    manifest["prosecution_metrics"] = {
        "total_evidence": len(admitted),
        "prosecution_ready": prosecution_ready,
        "prosecution_readiness_pct": prosecution_ready / len(admitted) * 100 if admitted else 0,
        "tier_1_count": len(manifest["evidence_by_tier"].get("TIER 1", [])),
        "tier_2_count": len(manifest["evidence_by_tier"].get("TIER 2", [])),
        "tier_3_count": len(manifest["evidence_by_tier"].get("TIER 3", [])),
        "wire_fraud_count": len(manifest["rico_predicate_mapping"].get("wire_fraud", [])),
        "money_laundering_count": len(manifest["rico_predicate_mapping"].get("money_laundering", []))
    }

    return manifest


def main():
    # Paths
    validation_path = "/Users/breydentaylor/certainly/visualizations/coordination/validated_evidence.json"
    manifest_path = "/Users/breydentaylor/certainly/visualizations/memory/evidence_manifest.json"

    # Ensure directory exists
    Path(manifest_path).parent.mkdir(parents=True, exist_ok=True)

    # Load validation results
    print(f"Loading validation results from: {validation_path}")
    with open(validation_path, 'r') as f:
        validation_results = json.load(f)

    # Build manifest
    print("\n📋 Building evidence manifest...")
    manifest = build_evidence_manifest(validation_results)

    # Write manifest
    print(f"✅ Writing evidence manifest to: {manifest_path}")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Print summary
    print(f"\n📊 Evidence Manifest Summary:")
    print(f"   Total evidence: {manifest['prosecution_metrics']['total_evidence']}")
    print(f"   Prosecution ready: {manifest['prosecution_metrics']['prosecution_ready']} ({manifest['prosecution_metrics']['prosecution_readiness_pct']:.1f}%)")
    print(f"\n   TIER Distribution:")
    for tier in ["TIER 1", "TIER 2", "TIER 3"]:
        count = manifest['tier_distribution'].get(tier, 0)
        pct = count / manifest['prosecution_metrics']['total_evidence'] * 100 if manifest['prosecution_metrics']['total_evidence'] else 0
        print(f"      {tier}: {count} ({pct:.1f}%)")

    print(f"\n   RICO Predicates:")
    print(f"      Wire fraud: {manifest['prosecution_metrics']['wire_fraud_count']} pieces")
    print(f"      Money laundering: {manifest['prosecution_metrics']['money_laundering_count']} pieces")

    return 0


if __name__ == "__main__":
    sys.exit(main())
