#!/usr/bin/env python3
"""
Extract validation terms from evidence_index.json for corpus querying.

Purpose:
- Pull all entities, wallets, keywords, amounts from existing evidence
- Create searchable term lists for corpus validation
- Output: coordination/validation_terms.json

Why this matters:
- Can't validate evidence without knowing what to search for
- Prevents manual term extraction (error-prone)
- Enables automated corpus mapping
"""

import json
import sys
from pathlib import Path
from typing import Dict, Set, List

def extract_terms(evidence_index_path: str) -> Dict[str, List[str]]:
    """Extract searchable terms from evidence index."""

    with open(evidence_index_path, 'r') as f:
        evidence = json.load(f)

    terms = {
        "wallet_addresses": set(),
        "entity_names": set(),
        "keywords": set(),
        "amounts": set(),
        "platforms": set(),
        "urls": set()
    }

    # Process each evidence item
    for evidence_id, item in evidence.items():
        metadata = item.get("metadata", {})

        # Extract wallet addresses (blockchain evidence)
        if "from_address" in metadata:
            addr = metadata["from_address"]
            if addr and addr != "0x0000000000000000000000000000000000000000":
                terms["wallet_addresses"].add(addr.lower())

        if "to_address" in metadata:
            addr = metadata["to_address"]
            if addr and addr != "0x0000000000000000000000000000000000000000":
                terms["wallet_addresses"].add(addr.lower())

        # Extract entity names
        if "entity_name" in metadata:
            name = metadata["entity_name"]
            if name and name != "unknown":
                terms["entity_names"].add(name)

        # Extract platform identifiers
        if "platform" in metadata:
            platform = metadata["platform"]
            if platform:
                terms["platforms"].add(platform)

        # Extract amounts (for verification)
        if "amount_usd" in metadata:
            amount = metadata["amount_usd"]
            if amount and amount > 0:
                terms["amounts"].add(amount)

        # Extract fraud keywords (if present)
        if "fraud_keywords" in metadata:
            keywords = metadata["fraud_keywords"]
            if isinstance(keywords, list):
                terms["keywords"].update(keywords)

        # Extract URLs (if present)
        if "url" in metadata:
            url = metadata["url"]
            if url:
                terms["urls"].add(url)

    # Convert sets to sorted lists for JSON
    result = {
        category: sorted(list(term_set))
        for category, term_set in terms.items()
    }

    # Add stats
    result["_stats"] = {
        "total_wallet_addresses": len(result["wallet_addresses"]),
        "total_entity_names": len(result["entity_names"]),
        "total_keywords": len(result["keywords"]),
        "total_amounts": len(result["amounts"]),
        "total_platforms": len(result["platforms"]),
        "total_urls": len(result["urls"])
    }

    return result


def main():
    # Paths
    evidence_path = "/Users/breydentaylor/certainly/visualizations/evidence_index.json"
    output_path = "/Users/breydentaylor/certainly/visualizations/coordination/validation_terms.json"

    # Ensure coordination/ exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Extract terms
    print(f"Reading evidence from: {evidence_path}")
    terms = extract_terms(evidence_path)

    # Write output
    with open(output_path, 'w') as f:
        json.dump(terms, f, indent=2)

    print(f"\n✅ Extracted validation terms:")
    print(f"   Wallet addresses: {terms['_stats']['total_wallet_addresses']}")
    print(f"   Entity names: {terms['_stats']['total_entity_names']}")
    print(f"   Keywords: {terms['_stats']['total_keywords']}")
    print(f"   Amounts: {terms['_stats']['total_amounts']}")
    print(f"   Platforms: {terms['_stats']['total_platforms']}")
    print(f"   URLs: {terms['_stats']['total_urls']}")
    print(f"\n✅ Wrote: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
