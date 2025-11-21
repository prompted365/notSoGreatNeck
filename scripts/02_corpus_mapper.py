#!/usr/bin/env python3
"""
Intelligent corpus grep - map validation terms to source documents.

Purpose:
- For each term (wallet, entity, keyword), find ALL corpus occurrences
- Record: file path, line number, context window
- Smart matching: exact for wallets, fuzzy for names, pattern for amounts

Why this matters:
- Proves evidence exists in corpus (not hallucinated)
- Provides source document citations for chain of custody
- Enables TIER classification validation
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

def grep_corpus_for_term(
    term: str,
    term_type: str,
    corpus_dirs: List[str],
    context_chars: int = 200
) -> List[Dict]:
    """
    Find all occurrences of term in corpus with context.

    Returns: [{"file": path, "line": num, "context": str, "match_type": str}]
    """
    matches = []

    for corpus_dir in corpus_dirs:
        corpus_path = Path(corpus_dir)

        if not corpus_path.exists():
            print(f"⚠️  Warning: Corpus directory not found: {corpus_dir}")
            continue

        # Walk all files in corpus
        for filepath in corpus_path.rglob('*'):
            # Skip non-files
            if not filepath.is_file():
                continue

            # Skip binary/db files
            if filepath.suffix in ['.db', '.sqlite', '.pkl', '.gpickle', '.png', '.jpg', '.pdf']:
                continue

            # Skip processed/coordination/memory (don't validate against our own outputs)
            if any(part in filepath.parts for part in ['processed', 'coordination', 'memory', 'scripts']):
                continue

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        matched = False
                        match_type = "unknown"

                        # Smart matching based on term type
                        if term_type == "wallet_addresses":
                            # Exact match for blockchain addresses (case-insensitive)
                            if term.lower() in line.lower():
                                matched = True
                                match_type = "exact"

                        elif term_type == "entity_names":
                            # Fuzzy match for names (handle variants)
                            name_variants = [
                                term,
                                term.lower(),
                                term.replace(" ", ""),
                                term.split()[0] if " " in term else term  # First name only
                            ]
                            if any(variant in line for variant in name_variants):
                                matched = True
                                match_type = "fuzzy"

                        elif term_type == "keywords":
                            # Case-insensitive keyword match
                            if re.search(rf'\b{re.escape(term)}\b', line, re.IGNORECASE):
                                matched = True
                                match_type = "keyword"

                        elif term_type == "amounts":
                            # Dollar amount pattern matching
                            amount_patterns = [
                                f"${term:,.2f}",
                                f"${int(term):,}",
                                f"{term}",
                                f"${term/1000:.0f}K" if term >= 1000 else ""
                            ]
                            if any(pattern and pattern in line for pattern in amount_patterns):
                                matched = True
                                match_type = "amount"

                        elif term_type == "urls":
                            # URL matching (domain extraction)
                            if term in line:
                                matched = True
                                match_type = "url"

                        elif term_type == "platforms":
                            # Platform keyword match
                            if term.lower() in line.lower():
                                matched = True
                                match_type = "platform"

                        if matched:
                            # Extract context window
                            term_pos = line.lower().find(term.lower())
                            if term_pos == -1:
                                term_pos = 0

                            context_start = max(0, term_pos - context_chars)
                            context_end = min(len(line), term_pos + len(term) + context_chars)
                            context = line[context_start:context_end].strip()

                            matches.append({
                                "file": str(filepath),
                                "line": line_num,
                                "context": context,
                                "match_type": match_type
                            })

            except Exception as e:
                # Skip files that can't be read (binary, permissions, etc.)
                continue

    return matches


def main():
    # Paths
    terms_path = "/Users/breydentaylor/certainly/visualizations/coordination/validation_terms.json"
    output_path = "/Users/breydentaylor/certainly/visualizations/coordination/evidence_to_corpus_mapping.json"

    # Corpus directories to search
    corpus_dirs = [
        "/Users/breydentaylor/certainly/shurka-dump",
        "/Users/breydentaylor/certainly/noteworthy-raw"
    ]

    # Load validation terms
    print(f"Loading validation terms from: {terms_path}")
    with open(terms_path, 'r') as f:
        terms = json.load(f)

    # Remove stats (not searchable)
    terms.pop("_stats", None)

    # Map terms to corpus
    print(f"\n🔍 Searching corpus directories:")
    for d in corpus_dirs:
        print(f"   - {d}")
    print()

    corpus_mapping = {}
    total_terms = sum(len(term_list) for term_list in terms.values())
    processed = 0

    for term_type, term_list in terms.items():
        print(f"Processing {term_type} ({len(term_list)} terms)...")

        for term in term_list:
            matches = grep_corpus_for_term(term, term_type, corpus_dirs)

            if matches:
                corpus_mapping[term] = {
                    "term_type": term_type,
                    "match_count": len(matches),
                    "unique_files": len(set(m["file"] for m in matches)),
                    "matches": matches[:100]  # Limit to first 100 matches per term
                }

            processed += 1
            if processed % 100 == 0:
                print(f"   Progress: {processed}/{total_terms} terms ({processed/total_terms*100:.1f}%)")

    # Add summary stats
    corpus_mapping["_summary"] = {
        "generated_at": datetime.now().isoformat(),
        "total_terms_searched": total_terms,
        "terms_with_matches": len(corpus_mapping) - 1,  # -1 for _summary itself
        "total_matches": sum(m["match_count"] for m in corpus_mapping.values() if isinstance(m, dict) and "match_count" in m),
        "corpus_directories": corpus_dirs
    }

    # Write output
    print(f"\n✅ Writing corpus mapping to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(corpus_mapping, f, indent=2)

    print(f"\n📊 Corpus Mapping Stats:")
    print(f"   Terms searched: {total_terms}")
    print(f"   Terms with matches: {corpus_mapping['_summary']['terms_with_matches']}")
    print(f"   Total matches found: {corpus_mapping['_summary']['total_matches']}")
    print(f"   Match rate: {corpus_mapping['_summary']['terms_with_matches']/total_terms*100:.1f}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
