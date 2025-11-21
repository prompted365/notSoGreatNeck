#!/usr/bin/env python3
"""
Manual review interface for flagged evidence items.

Purpose:
- Present flagged items with corpus context to human reviewer
- Allow admit/reject/skip decisions
- Update validation results with human decisions

Why this matters:
- Some evidence requires human judgment (borderline cases)
- Prevents false rejections (automated rules aren't perfect)
- Provides audit trail of manual decisions
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def present_evidence_item(
    evidence_id: str,
    evidence: Dict,
    corpus_mapping: Dict,
    item_num: int,
    total_items: int
) -> str:
    """
    Display evidence item with corpus context.
    Returns: "admit" | "reject" | "skip"
    """
    print(f"\n{'='*80}")
    print(f"ITEM {item_num}/{total_items}")
    print(f"{'='*80}")

    # Evidence details
    print(f"\n📋 Evidence ID: {evidence_id}")
    print(f"   Category: {evidence.get('category', 'unknown')}")
    print(f"   TIER: {evidence.get('tier', 'unknown')}")

    metadata = evidence.get("metadata", {})
    print(f"\n📊 Metadata:")
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            print(f"   {key}: {value}")

    # Validation status
    validation = evidence.get("validation", {})
    print(f"\n🔍 Validation Status:")
    print(f"   Status: {validation.get('status', 'unknown')}")
    print(f"   Corpus sources: {validation.get('source_count', 0)}")
    print(f"   Reason: {validation.get('reason', 'unknown')}")

    # Show corpus context
    if validation.get("match_details"):
        print(f"\n📄 Corpus Context:")
        for i, detail in enumerate(validation["match_details"], 1):
            print(f"\n   Match {i}:")
            print(f"   Field: {detail['field']}")
            print(f"   Value: {detail['value']}")
            print(f"   Files ({len(detail['files'])}):")
            for filepath in detail['files'][:3]:  # Show first 3 files
                filename = Path(filepath).name
                print(f"      - {filename}")

            # Show actual context from corpus_mapping if available
            if detail['value'] in corpus_mapping:
                mapping = corpus_mapping[detail['value']]
                matches = mapping.get('matches', [])
                if matches:
                    print(f"\n   Sample Context:")
                    sample = matches[0]
                    print(f"      File: {Path(sample['file']).name}")
                    print(f"      Line: {sample['line']}")
                    print(f"      Context: {sample['context'][:150]}...")

    # Get human decision
    print(f"\n{'='*80}")
    while True:
        decision = input("Decision (a=admit, r=reject, s=skip, q=quit): ").lower().strip()

        if decision in ['a', 'admit']:
            reason = input("Admission reason (optional): ").strip()
            return "admit", reason if reason else "Manual review - corpus context sufficient"

        elif decision in ['r', 'reject']:
            reason = input("Rejection reason (required): ").strip()
            while not reason:
                reason = input("Rejection reason (required): ").strip()
            return "reject", reason

        elif decision in ['s', 'skip']:
            return "skip", "Requires additional investigation"

        elif decision in ['q', 'quit']:
            print("\n⚠️  Exiting manual review...")
            return "quit", "Review incomplete"

        else:
            print("Invalid input. Please enter 'a', 'r', 's', or 'q'.")


def main():
    # Paths
    validation_path = "/Users/breydentaylor/certainly/visualizations/coordination/validated_evidence.json"
    corpus_mapping_path = "/Users/breydentaylor/certainly/visualizations/coordination/evidence_to_corpus_mapping.json"
    output_path = "/Users/breydentaylor/certainly/visualizations/coordination/manual_review_decisions.json"

    # Load validation results
    print(f"Loading validation results from: {validation_path}")
    with open(validation_path, 'r') as f:
        validation_results = json.load(f)

    # Load corpus mapping
    print(f"Loading corpus mapping from: {corpus_mapping_path}")
    with open(corpus_mapping_path, 'r') as f:
        corpus_mapping = json.load(f)

    corpus_mapping.pop("_summary", None)

    # Get flagged items
    flagged = validation_results.get("flagged", {})

    if not flagged:
        print("\n✅ No flagged items for manual review!")
        return 0

    print(f"\n📋 Manual Review Queue: {len(flagged)} items")
    print(f"\nInstructions:")
    print(f"  - Review each item with corpus context")
    print(f"  - Decide: admit (corpus backing sufficient), reject (insufficient), skip (need more info)")
    print(f"  - Your decisions will update the validation results")

    input("\nPress Enter to begin manual review...")

    # Review each flagged item
    decisions = {
        "reviewed_at": datetime.now().isoformat(),
        "total_flagged": len(flagged),
        "decisions": {}
    }

    admitted_count = 0
    rejected_count = 0
    skipped_count = 0

    for i, (evidence_id, evidence) in enumerate(flagged.items(), 1):
        decision, reason = present_evidence_item(
            evidence_id,
            evidence,
            corpus_mapping,
            i,
            len(flagged)
        )

        if decision == "quit":
            print(f"\n⚠️  Review incomplete. Processed {i-1}/{len(flagged)} items.")
            break

        decisions["decisions"][evidence_id] = {
            "decision": decision,
            "reason": reason,
            "original_status": evidence["validation"]["status"],
            "reviewed_at": datetime.now().isoformat()
        }

        if decision == "admit":
            admitted_count += 1
        elif decision == "reject":
            rejected_count += 1
        elif decision == "skip":
            skipped_count += 1

    # Add summary
    decisions["summary"] = {
        "admitted": admitted_count,
        "rejected": rejected_count,
        "skipped": skipped_count,
        "reviewed": admitted_count + rejected_count + skipped_count
    }

    # Write decisions
    print(f"\n✅ Writing manual review decisions to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(decisions, f, indent=2)

    print(f"\n📊 Manual Review Summary:")
    print(f"   Items reviewed: {decisions['summary']['reviewed']}/{len(flagged)}")
    print(f"   ✅ Admitted: {admitted_count}")
    print(f"   ❌ Rejected: {rejected_count}")
    print(f"   ⏸️  Skipped: {skipped_count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
