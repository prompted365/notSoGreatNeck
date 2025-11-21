#!/usr/bin/env python3
"""
Validation orchestrator - admit/reject/flag evidence based on corpus backing.

Purpose:
- For each evidence piece, count corpus sources
- Apply rules: 3+ sources = admit, 1-2 = flag, 0 = reject
- Update evidence with validation status and corpus citations

Why this matters:
- This is the "final cap" that validates extraction against reality
- Prevents hallucinated evidence from entering ReasoningBank
- Provides chain of custody (evidence → corpus files)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime


def validate_evidence_item(
    evidence_id: str,
    evidence: Dict,
    corpus_mapping: Dict,
    min_sources: int = 3
) -> Dict:
    """
    Validate single evidence item against corpus.

    Returns: {
        "status": "admitted" | "flagged" | "rejected",
        "corpus_sources": [file paths],
        "source_count": int,
        "reason": str
    }
    """
    metadata = evidence.get("metadata", {})

    # Collect unique corpus source files
    corpus_sources = set()
    match_details = []

    # Check wallet addresses (blockchain evidence)
    for field in ["from_address", "to_address"]:
        if field in metadata:
            wallet = metadata[field].lower()
            if wallet in corpus_mapping:
                mapping = corpus_mapping[wallet]
                files = set(m["file"] for m in mapping.get("matches", []))
                corpus_sources.update(files)
                match_details.append({
                    "field": field,
                    "value": wallet,
                    "matches": len(mapping.get("matches", [])),
                    "files": list(files)
                })

    # Check entity names
    if "entity_name" in metadata:
        entity = metadata["entity_name"]
        if entity in corpus_mapping:
            mapping = corpus_mapping[entity]
            files = set(m["file"] for m in mapping.get("matches", []))
            corpus_sources.update(files)
            match_details.append({
                "field": "entity_name",
                "value": entity,
                "matches": len(mapping.get("matches", [])),
                "files": list(files)
            })

    # Check amounts (for verification)
    if "amount_usd" in metadata and metadata["amount_usd"] > 0:
        amount = metadata["amount_usd"]
        if amount in corpus_mapping:
            mapping = corpus_mapping[amount]
            files = set(m["file"] for m in mapping.get("matches", []))
            corpus_sources.update(files)
            match_details.append({
                "field": "amount_usd",
                "value": amount,
                "matches": len(mapping.get("matches", [])),
                "files": list(files)
            })

    # Check URLs
    if "url" in metadata:
        url = metadata["url"]
        if url in corpus_mapping:
            mapping = corpus_mapping[url]
            files = set(m["file"] for m in mapping.get("matches", []))
            corpus_sources.update(files)
            match_details.append({
                "field": "url",
                "value": url,
                "matches": len(mapping.get("matches", [])),
                "files": list(files)
            })

    # Decision logic
    num_sources = len(corpus_sources)

    if num_sources >= min_sources:
        # ADMIT: Sufficient corpus backing
        return {
            "status": "admitted",
            "corpus_sources": sorted(list(corpus_sources)),
            "source_count": num_sources,
            "match_details": match_details,
            "reason": f"Validated across {num_sources} corpus sources (>= {min_sources} required)"
        }

    elif num_sources >= 1:
        # FLAG: Some corpus backing but needs manual review
        return {
            "status": "flagged",
            "corpus_sources": sorted(list(corpus_sources)),
            "source_count": num_sources,
            "match_details": match_details,
            "reason": f"Only {num_sources} source(s), requires manual review (need {min_sources})"
        }

    else:
        # REJECT: No corpus backing
        return {
            "status": "rejected",
            "corpus_sources": [],
            "source_count": 0,
            "match_details": [],
            "reason": "No corpus sources found - possible hallucination or placeholder"
        }


def main():
    # Paths
    evidence_path = "/Users/breydentaylor/certainly/visualizations/evidence_index.json"
    corpus_mapping_path = "/Users/breydentaylor/certainly/visualizations/coordination/evidence_to_corpus_mapping.json"
    output_path = "/Users/breydentaylor/certainly/visualizations/coordination/validated_evidence.json"

    # Load evidence index
    print(f"Loading evidence from: {evidence_path}")
    with open(evidence_path, 'r') as f:
        evidence_index = json.load(f)

    # Load corpus mapping
    print(f"Loading corpus mapping from: {corpus_mapping_path}")
    with open(corpus_mapping_path, 'r') as f:
        corpus_mapping = json.load(f)

    # Remove summary (not searchable)
    corpus_mapping.pop("_summary", None)

    # Validate each evidence item
    print(f"\n🔍 Validating {len(evidence_index)} evidence items...")

    admitted = {}
    rejected = {}
    flagged = {}

    for evidence_id, evidence in evidence_index.items():
        validation = validate_evidence_item(evidence_id, evidence, corpus_mapping)

        # Add validation metadata to evidence
        evidence["validation"] = validation

        # Sort into buckets
        if validation["status"] == "admitted":
            admitted[evidence_id] = evidence
        elif validation["status"] == "rejected":
            rejected[evidence_id] = evidence
        else:  # flagged
            flagged[evidence_id] = evidence

    # Compile results
    results = {
        "validation_metadata": {
            "validated_at": datetime.now().isoformat(),
            "total_evidence": len(evidence_index),
            "admitted": len(admitted),
            "rejected": len(rejected),
            "flagged": len(flagged),
            "admission_rate": len(admitted) / len(evidence_index) * 100 if evidence_index else 0,
            "min_sources_required": 3
        },
        "admitted": admitted,
        "rejected": rejected,
        "flagged": flagged
    }

    # Write output
    print(f"\n✅ Writing validation results to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📊 Validation Results:")
    print(f"   Total evidence: {len(evidence_index)}")
    print(f"   ✅ Admitted: {len(admitted)} ({len(admitted)/len(evidence_index)*100:.1f}%)")
    print(f"   ⚠️  Flagged: {len(flagged)} ({len(flagged)/len(evidence_index)*100:.1f}%)")
    print(f"   ❌ Rejected: {len(rejected)} ({len(rejected)/len(evidence_index)*100:.1f}%)")

    if rejected:
        print(f"\n❌ Top rejection reasons:")
        rejection_reasons = {}
        for eid, ev in rejected.items():
            reason = ev["validation"]["reason"]
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

        for reason, count in sorted(rejection_reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {reason}: {count} items")

    return 0


if __name__ == "__main__":
    sys.exit(main())
