#!/usr/bin/env python3
"""
Gap Filler Agent - Phase 4 Evidence Recovery
Searches corpus for additional evidence sources to promote flagged items
"""

import json
import glob
import csv
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class GapFiller:
    def __init__(self):
        self.base_path = Path('/Users/breydentaylor/certainly')
        self.viz_path = self.base_path / 'visualizations'
        self.corpus_path = self.base_path / 'shurka-dump'
        self.noteworthy_path = self.base_path / 'noteworthy-raw'

        # Track statistics
        self.stats = {
            'telegram_mentions': 0,
            'blockchain_matches': 0,
            'shadowlens_mentions': 0,
            'promoted_to_tier2': 0,
            'promoted_to_tier3': 0,
            'still_flagged': 0
        }

        # Cache corpus files
        self.blockchain_files = list(self.corpus_path.glob('**/*.csv'))
        self.blockchain_files.extend(list(self.noteworthy_path.glob('**/*.csv')))
        print(f"Found {len(self.blockchain_files)} blockchain CSV files")

    def search_blockchain_for_address(self, address: str) -> List[Dict]:
        """Search blockchain CSVs for wallet address mentions"""
        matches = []
        address_lower = address.lower()

        for csv_file in self.blockchain_files:
            try:
                with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    if address_lower in content:
                        # Count occurrences
                        count = content.count(address_lower)
                        matches.append({
                            'type': 'blockchain_csv',
                            'file': str(csv_file),
                            'match_count': count,
                            'relevance': 'Address found in blockchain corpus'
                        })
            except Exception as e:
                continue

        return matches

    def search_telegram_for_keywords(self, keywords: List[str]) -> List[Dict]:
        """Search Telegram data for keyword mentions"""
        mentions = []
        telegram_dirs = [
            self.corpus_path / 'recon_intel/harvest/deep-crawl/telegram-discussion',
            self.corpus_path / 'recon_intel/harvest/snapshots/telegram',
            self.corpus_path / 'recon_intel/harvest/link-hop/telegram-discussion'
        ]

        for telegram_dir in telegram_dirs:
            if not telegram_dir.exists():
                continue

            for json_file in telegram_dir.glob('**/*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Handle different JSON structures
                    messages = []
                    if isinstance(data, list):
                        messages = data
                    elif isinstance(data, dict):
                        messages = data.get('messages', [data])

                    for msg in messages:
                        text = str(msg.get('text', '')).lower()
                        for keyword in keywords:
                            if keyword.lower() in text:
                                mentions.append({
                                    'type': 'telegram',
                                    'file': str(json_file),
                                    'keyword': keyword,
                                    'relevance': f'Telegram mention of {keyword}'
                                })
                                break  # Count once per message

                except Exception as e:
                    continue

        # Limit to top 3 per search to avoid inflation
        return mentions[:3] if mentions else []

    def recalculate_sources(self, item: Dict, new_sources: List[Dict]) -> Dict:
        """Recalculate effective sources with notebook discount"""
        evidence = item['evidence']
        validation = evidence.get('validation', {})

        # Get original counts
        original_corpus_sources = validation.get('corpus_sources', [])
        original_corpus_count = len(original_corpus_sources)

        # Count new corpus sources (unique files)
        unique_new_files = set()
        for source in new_sources:
            if source['type'] in ['blockchain_csv', 'telegram']:
                unique_new_files.add(source['file'])

        new_corpus_count = len(unique_new_files)
        total_corpus = original_corpus_count + new_corpus_count

        # Notebook sources (shadowLens) - apply 0.5x discount
        notebook_count = 0
        if evidence.get('namespace') == 'evidence_shadowlens':
            notebook_count = 1

        # Calculate effective sources
        effective_sources = total_corpus + (notebook_count * 0.5)

        return {
            'corpus_count': total_corpus,
            'notebook_count': notebook_count,
            'effective_sources': effective_sources,
            'original_corpus_count': original_corpus_count,
            'new_corpus_sources': list(unique_new_files),
            'new_sources_found': new_sources
        }

    def assign_tier(self, effective_sources: float, item: Dict) -> Dict:
        """Assign tier based on effective sources"""
        # Tier 2: 3.0+ effective sources (one subpoena away)
        if effective_sources >= 3.0:
            return {
                'tier': 2,
                'reason': f'Strong sourcing ({effective_sources} effective sources), one subpoena away from Tier 1'
            }

        # Tier 3: 2.0+ effective sources (investigative development)
        if effective_sources >= 2.0:
            return {
                'tier': 3,
                'reason': f'Moderate sourcing ({effective_sources} effective sources), needs further investigation'
            }

        # Still flagged
        return {
            'tier': 'flagged',
            'reason': f'Insufficient sourcing ({effective_sources} effective sources, need 2.0+)'
        }

    def process_blockchain_item(self, item: Dict) -> Dict:
        """Process a blockchain transaction evidence item"""
        evidence = item['evidence']
        metadata = evidence.get('metadata', {})

        # Extract addresses
        from_addr = metadata.get('from_address', '')
        to_addr = metadata.get('to_address', '')

        # Search corpus for these addresses
        new_sources = []

        if from_addr:
            from_matches = self.search_blockchain_for_address(from_addr)
            new_sources.extend(from_matches[:2])  # Limit per address

        if to_addr:
            to_matches = self.search_blockchain_for_address(to_addr)
            new_sources.extend(to_matches[:2])  # Limit per address

        # Also search Telegram for wallet addresses (in case discussed)
        telegram_keywords = [from_addr[:10], to_addr[:10]]  # Use prefix
        telegram_mentions = self.search_telegram_for_keywords(telegram_keywords)
        new_sources.extend(telegram_mentions)

        # Recalculate sources
        new_source_data = self.recalculate_sources(item, new_sources)

        # Re-tier
        tier_data = self.assign_tier(new_source_data['effective_sources'], item)

        # Update statistics
        self.stats['blockchain_matches'] += len([s for s in new_sources if s['type'] == 'blockchain_csv'])
        self.stats['telegram_mentions'] += len([s for s in new_sources if s['type'] == 'telegram'])

        if tier_data['tier'] == 2:
            self.stats['promoted_to_tier2'] += 1
        elif tier_data['tier'] == 3:
            self.stats['promoted_to_tier3'] += 1
        else:
            self.stats['still_flagged'] += 1

        return {
            'evidence_id': item['evidence_id'],
            'original_status': 'flagged',
            'new_tier': tier_data['tier'],
            'tier_reason': tier_data['reason'],
            'sources': new_source_data,
            'evidence': evidence
        }

    def process_entity_item(self, item: Dict) -> Dict:
        """Process an entity linkage evidence item"""
        evidence = item['evidence']
        metadata = evidence.get('metadata', {})

        # Extract entity names for search
        entity_name = metadata.get('entity_name', '')
        principals = metadata.get('principals_exposed', [])

        # Search keywords
        keywords = [entity_name] + principals
        keywords = [k for k in keywords if k]  # Remove empty

        # Search corpus
        telegram_mentions = self.search_telegram_for_keywords(keywords)

        # Recalculate sources
        new_source_data = self.recalculate_sources(item, telegram_mentions)

        # Re-tier
        tier_data = self.assign_tier(new_source_data['effective_sources'], item)

        # Update statistics
        self.stats['telegram_mentions'] += len(telegram_mentions)

        if tier_data['tier'] == 2:
            self.stats['promoted_to_tier2'] += 1
        elif tier_data['tier'] == 3:
            self.stats['promoted_to_tier3'] += 1
        else:
            self.stats['still_flagged'] += 1

        return {
            'evidence_id': item['evidence_id'],
            'original_status': 'flagged',
            'new_tier': tier_data['tier'],
            'tier_reason': tier_data['reason'],
            'sources': new_source_data,
            'evidence': evidence
        }

    def process_all_items(self, items: List[Dict]) -> List[Dict]:
        """Process all flagged items"""
        results = []

        for i, item in enumerate(items, 1):
            print(f"\nProcessing {i}/{len(items)}: {item['evidence_id']}")

            category = item['evidence'].get('category', '')

            if category == 'blockchain':
                result = self.process_blockchain_item(item)
            elif category == 'entities':
                result = self.process_entity_item(item)
            else:
                # Default processing
                result = {
                    'evidence_id': item['evidence_id'],
                    'original_status': 'flagged',
                    'new_tier': 'flagged',
                    'tier_reason': 'Unsupported category',
                    'sources': self.recalculate_sources(item, []),
                    'evidence': item['evidence']
                }
                self.stats['still_flagged'] += 1

            results.append(result)
            print(f"  → New tier: {result['new_tier']}, Effective sources: {result['sources']['effective_sources']}")

        return results

    def generate_report(self, results: List[Dict], items_processed: int) -> Dict:
        """Generate gap fill report"""
        # Calculate averages
        effective_sources_before = []
        effective_sources_after = []

        for result in results:
            # Before: original corpus + notebook discount
            orig_corpus = result['sources']['original_corpus_count']
            notebook = result['sources']['notebook_count']
            before = orig_corpus + (notebook * 0.5)
            effective_sources_before.append(before)

            # After
            effective_sources_after.append(result['sources']['effective_sources'])

        avg_before = sum(effective_sources_before) / len(effective_sources_before) if effective_sources_before else 0
        avg_after = sum(effective_sources_after) / len(effective_sources_after) if effective_sources_after else 0

        # High-value promotions
        high_value = [
            {
                'evidence_id': r['evidence_id'],
                'before': {
                    'tier': 'flagged',
                    'effective_sources': round(effective_sources_before[i], 2)
                },
                'after': {
                    'tier': r['new_tier'],
                    'effective_sources': round(r['sources']['effective_sources'], 2)
                },
                'new_sources_count': len(r['sources'].get('new_corpus_sources', []))
            }
            for i, r in enumerate(results)
            if r['new_tier'] in [2, 3]
        ]

        return {
            'run_id': 'cert1-phase4-autonomous-20251121',
            'agent': 'Gap_Filler',
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'input': {
                'flagged_items': items_processed,
                'loop_iteration': 1
            },
            'output': {
                'items_processed': items_processed,
                'tier_changes': {
                    'promoted_to_tier2': self.stats['promoted_to_tier2'],
                    'promoted_to_tier3': self.stats['promoted_to_tier3'],
                    'still_flagged': self.stats['still_flagged']
                },
                'sources_found': {
                    'telegram_mentions': self.stats['telegram_mentions'],
                    'blockchain_matches': self.stats['blockchain_matches'],
                    'shadowlens_mentions': self.stats['shadowlens_mentions']
                },
                'effective_sources_improvement': {
                    'before_avg': round(avg_before, 2),
                    'after_avg': round(avg_after, 2),
                    'improvement': round(avg_after - avg_before, 2)
                }
            },
            'high_value_promotions': high_value[:10],  # Top 10
            'still_flagged_analysis': f"{self.stats['still_flagged']} items remain flagged due to insufficient corpus presence",
            'unfilled_gaps_remaining': self.stats['still_flagged'],
            'gap_reduction': f"From {items_processed} to {self.stats['still_flagged']} unfilled gaps ({self.stats['promoted_to_tier2'] + self.stats['promoted_to_tier3']} promoted)"
        }

def main():
    print("=== Gap Filler Agent - Phase 4 ===")
    print("Starting evidence recovery and source corroboration\n")

    # Initialize
    filler = GapFiller()

    # Load input
    input_file = Path('/Users/breydentaylor/certainly/visualizations/coordination/gap_fill_input.json')
    with open(input_file, 'r') as f:
        input_data = json.load(f)

    items = input_data['items']
    print(f"Loaded {len(items)} flagged items for processing")

    # Process all items
    results = filler.process_all_items(items)

    # Generate report
    report = filler.generate_report(results, len(items))

    # Save results
    output_dir = Path('/Users/breydentaylor/certainly/visualizations/coordination')

    with open(output_dir / 'gap_fill_results.json', 'w') as f:
        json.dump({
            'results': results,
            'metadata': {
                'processed_at': datetime.utcnow().isoformat() + 'Z',
                'total_items': len(results)
            }
        }, f, indent=2)

    with open(output_dir / 'gap_fill_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    # Create state file
    state_dir = Path('/Users/breydentaylor/certainly/visualizations/state')
    with open(state_dir / 'gap_filler.state.json', 'w') as f:
        json.dump({
            'run_id': 'cert1-phase4-autonomous-20251121',
            'agent': 'gap_filler',
            'status': 'completed',
            'started_at': datetime.utcnow().isoformat() + 'Z',
            'completed_at': datetime.utcnow().isoformat() + 'Z',
            'outputs': [
                'coordination/gap_fill_results.json',
                'coordination/gap_fill_report.json'
            ],
            'metrics': {
                'items_processed': len(items),
                'promoted_to_tier2': filler.stats['promoted_to_tier2'],
                'promoted_to_tier3': filler.stats['promoted_to_tier3'],
                'still_flagged': filler.stats['still_flagged']
            }
        }, f, indent=2)

    print("\n" + "="*60)
    print("GAP FILLING COMPLETE")
    print("="*60)
    print(f"Processed: {len(items)} items")
    print(f"Promoted to Tier 2: {filler.stats['promoted_to_tier2']}")
    print(f"Promoted to Tier 3: {filler.stats['promoted_to_tier3']}")
    print(f"Still flagged: {filler.stats['still_flagged']}")
    print(f"\nNew sources found:")
    print(f"  - Telegram mentions: {filler.stats['telegram_mentions']}")
    print(f"  - Blockchain matches: {filler.stats['blockchain_matches']}")
    print(f"\nOutputs saved:")
    print(f"  - coordination/gap_fill_results.json")
    print(f"  - coordination/gap_fill_report.json")
    print(f"  - state/gap_filler.state.json")

if __name__ == '__main__':
    main()
