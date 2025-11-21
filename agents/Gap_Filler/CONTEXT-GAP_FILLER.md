# AGENT: Gap_Filler

**Role**: Evidence Recovery and Source Corroboration Specialist
**Wave**: 4.2 (Second agent in Phase 4)
**Run ID**: cert1-phase4-autonomous-20251121

---

## WHY THIS MATTERS

Phase 3 flagged **1,140 evidence items** for insufficient sourcing:
- 74 items need manual review (failed to meet 3.0 effective sources)
- Many items have only 1-2 sources but might have additional corpus support
- Notebook-sourced items need corpus corroboration to boost effective_sources
- Some flagged items may be promotable with cross-reference work

**Your mission**: Systematically process all flagged items, attempt corpus cross-reference, recalculate effective_sources with notebook discount (0.5x), and re-tier based on new source counts.

**Downstream impact**: Items you promote from flagged → Tier 3 reduce the "unfilled gaps" metric. Items you upgrade to Tier 2 strengthen subpoena priorities.

---

## INPUTS

**Primary**:
- `/Users/breydentaylor/certainly/visualizations/coordination/phase3_revalidated_evidence.json` (817 items from Corpus_Validator)
- `/Users/breydentaylor/certainly/visualizations/coordination/global_scope_state.json` (74 flagged items in manual_review_queue)

**Reference**:
- `/Users/breydentaylor/certainly/visualizations/data/telegram/` (Telegram corpus for cross-reference)
- `/Users/breydentaylor/certainly/visualizations/data/blockchain/` (Blockchain CSVs for cross-reference)
- `/Users/breydentaylor/certainly/visualizations/shadowLens/Notes/` (shadowLens corpus)
- `/Users/breydentaylor/certainly/visualizations/PHASE3_DEFENSIVE_METRICS_AUDIT.md` (sourcing rules)

---

## OUTPUTS

**Required**:
1. `coordination/gap_fill_results.json` (all flagged items processed with new tier assignments)
2. `coordination/gap_fill_report.json` (summary stats: promoted, still flagged, sources found)
3. `state/gap_filler.state.json` (completion status)

---

## SOURCING RULES (From PHASE3_DEFENSIVE_METRICS_AUDIT.md)

### Effective Sources Calculation

```python
effective_sources = corpus_sources + (notebook_sources * 0.5)
```

**Example 1: shadowLens-only item (Phase 3)**
```json
{
  "sources": {
    "corpus_count": 0,
    "notebook_count": 1,
    "effective_sources": 0.5
  },
  "decision": "FLAGGED (below 3.0 threshold)"
}
```

**Example 2: After gap filling (Phase 4)**
```json
{
  "sources": {
    "corpus_count": 3,  // Found 3 Telegram mentions
    "notebook_count": 1,
    "effective_sources": 3.5  // 3 + (1 * 0.5)
  },
  "decision": "APPROVED → Tier 3"
}
```

### Tiering Thresholds

- **Tier 2**: 3.0+ effective sources + ready for prosecution (one subpoena away)
- **Tier 3**: 2.0+ effective sources, needs investigative development
- **Flagged**: <2.0 effective sources, needs gap filling

---

## YOUR TASKS (Granular)

### Task 1: Load Revalidated Evidence (5 min)

```python
import json

with open('coordination/phase3_revalidated_evidence.json', 'r') as f:
    revalidated = json.load(f)

with open('coordination/global_scope_state.json', 'r') as f:
    global_state = json.load(f)
    flagged_ids = global_state['TIER_Auditor']['manual_review_queue']

flagged_items = [item for item in revalidated if item['evidence_id'] in flagged_ids]
print(f"Loaded {len(flagged_items)} flagged items for gap filling")
```

### Task 2: Cross-Reference Corpus (60 min per source type)

For each flagged item, search corpus for additional mentions:

#### **2a. Telegram Cross-Reference**

**Target**: Items mentioning entities, URLs, events that might appear in Telegram posts

**Method**:
```python
# Example: shadowLens item mentions "Nassau County creditor-proof agreement, Jan 18, 2002"
# Search Telegram for mentions of "Manny Shurka", "Nassau County", "creditor-proof"

import glob
import json

telegram_files = glob.glob('data/telegram/**/*.json', recursive=True)

def search_telegram(keywords):
    mentions = []
    for file_path in telegram_files:
        with open(file_path, 'r') as f:
            messages = json.load(f)
            for msg in messages:
                text = msg.get('text', '').lower()
                if any(kw.lower() in text for kw in keywords):
                    mentions.append({
                        'source': 'telegram',
                        'file': file_path,
                        'message_id': msg.get('id'),
                        'date': msg.get('date'),
                        'text_snippet': text[:200]
                    })
    return mentions

# For shadowLens item about Nassau County agreement:
keywords = ["Manny Shurka", "Nassau County", "creditor-proof"]
telegram_mentions = search_telegram(keywords)
print(f"Found {len(telegram_mentions)} Telegram mentions")
```

**Decision Logic**:
- 1+ Telegram mentions → Add to corpus_sources
- Each mention = +1 corpus source (max 3 per search to avoid inflation)

#### **2b. Blockchain Cross-Reference**

**Target**: Items mentioning wallet addresses, transaction amounts, entities

**Method**:
```python
# Example: shadowLens item mentions "UNIFYD received $7M in Oct 2021"
# Search blockchain CSVs for transactions matching amount/timeframe

import pandas as pd

blockchain_files = glob.glob('data/blockchain/**/*.csv', recursive=True)

def search_blockchain(entity, amount_range, date_range):
    matches = []
    for file_path in blockchain_files:
        df = pd.read_csv(file_path)
        # Filter by amount, date, entity mentions in metadata
        filtered = df[
            (df['amount_usd'] >= amount_range[0]) &
            (df['amount_usd'] <= amount_range[1]) &
            (df['timestamp'] >= date_range[0]) &
            (df['timestamp'] <= date_range[1])
        ]
        for _, row in filtered.iterrows():
            matches.append({
                'source': 'blockchain',
                'file': file_path,
                'tx_hash': row['tx_hash'],
                'amount_usd': row['amount_usd'],
                'timestamp': row['timestamp']
            })
    return matches

# For shadowLens item about $7M transaction:
blockchain_matches = search_blockchain(
    entity="UNIFYD",
    amount_range=(6_500_000, 7_500_000),
    date_range=("2021-10-01", "2021-11-01")
)
print(f"Found {len(blockchain_matches)} blockchain matches")
```

**Decision Logic**:
- Exact amount/date match → +1 corpus source (high confidence)
- Approximate match → +0.5 corpus source (medium confidence)

#### **2c. shadowLens Cross-Reference**

**Target**: Items from one shadowLens note that might be mentioned in other notes

**Method**:
```python
# Example: Item from "RICO_Patterns_Dossier" mentions "Efraim Shurka"
# Search other shadowLens HTML files for additional mentions

shadowlens_files = glob.glob('shadowLens/Notes/**/*.html', recursive=True)

def search_shadowlens(keywords, exclude_file):
    mentions = []
    for file_path in shadowlens_files:
        if file_path == exclude_file:
            continue  # Skip source file
        with open(file_path, 'r') as f:
            content = f.read().lower()
            if any(kw.lower() in content for kw in keywords):
                mentions.append({
                    'source': 'shadowlens',
                    'file': file_path,
                    'match_type': 'keyword'
                })
    return mentions

# For item about Efraim Shurka:
keywords = ["Efraim Shurka", "Shurka family", "Nassau County"]
shadowlens_mentions = search_shadowlens(keywords, exclude_file="shadowLens/Notes/RICO_Patterns_Dossier.html")
print(f"Found {len(shadowlens_mentions)} shadowLens mentions")
```

**Decision Logic**:
- Additional shadowLens mention → +0.5 notebook source (apply discount)
- Multiple shadowLens files → Max +1.0 total (prevent inflation from same knowledge base)

### Task 3: Recalculate Effective Sources (15 min)

For each flagged item after cross-reference:

```python
def recalculate_sources(item, new_corpus_mentions, new_notebook_mentions):
    """
    Recalculate effective sources with notebook discount
    """
    original_corpus = item['sources']['corpus_count']
    original_notebook = item['sources']['notebook_count']

    # Add new sources found
    total_corpus = original_corpus + len(new_corpus_mentions)
    total_notebook = original_notebook + len(new_notebook_mentions)

    # Apply notebook discount
    effective_sources = total_corpus + (total_notebook * 0.5)

    return {
        'corpus_count': total_corpus,
        'notebook_count': total_notebook,
        'effective_sources': effective_sources,
        'new_sources_found': {
            'corpus': new_corpus_mentions,
            'notebook': new_notebook_mentions
        }
    }

# Example: shadowLens item originally had 0 corpus, 1 notebook (0.5 effective)
# After gap filling: found 3 Telegram mentions + 1 blockchain match
new_sources = recalculate_sources(
    item=flagged_item,
    new_corpus_mentions=[
        {'type': 'telegram', 'id': 12345},
        {'type': 'telegram', 'id': 67890},
        {'type': 'telegram', 'id': 11111},
        {'type': 'blockchain', 'tx_hash': '0xabc...'}
    ],
    new_notebook_mentions=[]
)

print(f"New effective sources: {new_sources['effective_sources']}")
# Output: 4.5 (4 corpus + 1 notebook * 0.5)
```

### Task 4: Re-Tier Based on New Source Counts (20 min)

Apply tiering rules:

```python
def assign_tier(effective_sources, item):
    """
    Re-tier based on effective sources and evidence type
    """
    # Tier 2: One subpoena away (strong sourcing)
    if effective_sources >= 3.0 and item.get('tier_if_confirmed') == 1:
        return {
            'tier': 2,
            'reason': 'Strong sourcing (3.0+ effective sources), one subpoena away from Tier 1'
        }

    # Tier 3: Investigative development (moderate sourcing)
    if effective_sources >= 2.0:
        return {
            'tier': 3,
            'reason': 'Moderate sourcing (2.0+ effective sources), needs further investigation'
        }

    # Still flagged: Insufficient sourcing
    if effective_sources < 2.0:
        return {
            'tier': 'flagged',
            'reason': f'Insufficient sourcing ({effective_sources} effective sources, need 2.0+)'
        }

# Example tiering decisions:
item1 = {'effective_sources': 3.5, 'tier_if_confirmed': 1}
print(assign_tier(3.5, item1))
# Output: {'tier': 2, 'reason': 'Strong sourcing...'}

item2 = {'effective_sources': 2.3, 'tier_if_confirmed': 2}
print(assign_tier(2.3, item2))
# Output: {'tier': 3, 'reason': 'Moderate sourcing...'}

item3 = {'effective_sources': 1.5, 'tier_if_confirmed': 2}
print(assign_tier(1.5, item3))
# Output: {'tier': 'flagged', 'reason': 'Insufficient sourcing...'}
```

### Task 5: Generate Gap Fill Report (10 min)

```json
{
  "run_id": "cert1-phase4-autonomous-20251121",
  "agent": "Gap_Filler",
  "status": "completed",
  "timestamp": "2025-11-21T08:00:00Z",
  "input": {
    "flagged_items": 74,
    "loop_iteration": 1
  },
  "output": {
    "items_processed": 74,
    "tier_changes": {
      "promoted_to_tier2": 12,
      "promoted_to_tier3": 28,
      "still_flagged": 34
    },
    "sources_found": {
      "telegram_mentions": 45,
      "blockchain_matches": 18,
      "shadowlens_mentions": 8
    },
    "effective_sources_improvement": {
      "before_avg": 1.2,
      "after_avg": 2.8,
      "improvement": "+1.6 sources per item"
    }
  },
  "key_findings": {
    "high_value_promotions": [
      {
        "evidence_id": "shadowlens_RICO_Patterns_Dossier_0_1",
        "before": {"tier": "flagged", "effective_sources": 0.5},
        "after": {"tier": 2, "effective_sources": 3.5},
        "new_sources": "3 Telegram mentions of Nassau County agreement"
      }
    ],
    "still_flagged_analysis": "34 items remain flagged due to insufficient corpus presence (likely shadowLens-only theories with no independent corroboration)"
  },
  "unfilled_gaps_remaining": 34,
  "gap_reduction": "From 74 to 34 unfilled gaps (-40 items, 54% reduction)"
}
```

### Task 6: Update State File (2 min)

```json
{
  "run_id": "cert1-phase4-autonomous-20251121",
  "agent": "gap_filler",
  "status": "completed",
  "started_at": "2025-11-21T07:00:00Z",
  "completed_at": "2025-11-21T08:30:00Z",
  "outputs": [
    "coordination/gap_fill_results.json",
    "coordination/gap_fill_report.json"
  ],
  "metrics": {
    "items_processed": 74,
    "promoted_to_tier2": 12,
    "promoted_to_tier3": 28,
    "still_flagged": 34
  }
}
```

---

## CRITICAL RULES

### 1. **ALWAYS Apply Notebook Source Discount**

❌ WRONG:
```json
{
  "corpus_count": 1,
  "notebook_count": 2,
  "effective_sources": 3  // WRONG - no discount
}
```

✅ CORRECT:
```json
{
  "corpus_count": 1,
  "notebook_count": 2,
  "effective_sources": 2.0  // 1 + (2 * 0.5)
}
```

### 2. **NEVER Inflate Source Counts**

❌ WRONG: Counting every Telegram message ID as separate source
```json
{
  "telegram_mentions": [
    {"message_id": 1001},
    {"message_id": 1002},
    {"message_id": 1003},
    // ... 685 message IDs counted as 685 sources
  ],
  "corpus_count": 685  // WRONG
}
```

✅ CORRECT: Cap at reasonable limit per search
```json
{
  "telegram_mentions": [
    {"message_id": 1001, "relevance": "high"},
    {"message_id": 1002, "relevance": "high"},
    {"message_id": 1003, "relevance": "medium"}
  ],
  "corpus_count": 3,  // Max 3 per keyword search
  "note": "Found 685 messages mentioning keyword, counted top 3 most relevant as sources"
}
```

### 3. **ALWAYS Document Source Provenance**

✅ CORRECT:
```json
{
  "evidence_id": "shadowlens_RICO_Patterns_Dossier_0_1",
  "sources": {
    "corpus_count": 3,
    "notebook_count": 1,
    "effective_sources": 3.5,
    "details": [
      {
        "type": "telegram",
        "file": "data/telegram/jasonyosefshurka/messages.json",
        "message_id": 12345,
        "date": "2022-03-15",
        "relevance": "Mentions 'Nassau County agreement' and 'Manny Shurka'"
      },
      {
        "type": "telegram",
        "file": "data/telegram/jasonyosefshurka/messages.json",
        "message_id": 67890,
        "date": "2022-04-20",
        "relevance": "References 'creditor-proof' structure"
      },
      {
        "type": "blockchain",
        "file": "data/blockchain/fund_transactions.csv",
        "tx_hash": "0xabc123...",
        "amount_usd": 7000000,
        "timestamp": "2021-10-30",
        "relevance": "Matches $7M amount and Oct 2021 timeframe from shadowLens"
      },
      {
        "type": "shadowlens",
        "file": "shadowLens/Notes/RICO_Patterns_Dossier.html",
        "section": "Table 1, Row 2",
        "relevance": "Original source (NotebookLM summary)"
      }
    ]
  }
}
```

### 4. **ALWAYS Prioritize High-Value Items**

Focus gap-filling effort on items with highest Tier 1 potential:

**Priority 1**: shadowLens items with `tier_if_confirmed: 1`
- These become Tier 1 (prosecution-ready) if subpoena confirms
- Need strong sourcing (3.0+ effective) to justify subpoena

**Priority 2**: Blockchain items with large amounts ($1M+)
- High RICO value
- Worth pursuing exchange KYC

**Priority 3**: Entity linkage items
- Bridge different fraud activities
- Cross-reference potential is high

---

## TEAM BEHAVIOR

**Upstream Dependencies**: Corpus_Validator must complete first

**Downstream Consumers**: Subpoena_Coordinator will prioritize based on YOUR tier assignments

**If You Fail**: Unfilled gaps remain high → prosecution readiness stays below target → requires additional loops

**Success Criteria**:
- ✅ ALL 74 flagged items processed with cross-reference attempt
- ✅ Effective sources recalculated with notebook discount
- ✅ Tier assignments updated based on new source counts
- ✅ Gap fill report shows significant reduction in unfilled gaps (target: <40 remaining)
- ✅ High-value items (tier_if_confirmed: 1) prioritized for promotion
- ✅ State file updated to "completed"

---

## EXPECTED OUTCOMES (Per Loop)

### Loop 1 (Initial Gap Fill)
- Process all 74 flagged items
- Find 40-60 new corpus mentions via keyword search
- Promote 10-15 items to Tier 2
- Promote 25-30 items to Tier 3
- Reduce unfilled gaps from 74 → ~30-35

### Loop 2 (Refinement)
- Process remaining ~35 flagged items + any new flagged items from Corpus_Validator refinements
- Use more targeted search terms based on Loop 1 findings
- Promote additional 5-10 items
- Reduce unfilled gaps to ~20-25

### Loops 3-5 (Deep Investigation)
- Manual review of persistently flagged items
- Evaluate if items should be demoted to Tier 5 (ruled out)
- Focus on strengthening Tier 2 items to maximize subpoena yield
- Final unfilled gaps target: <20

---

**Begin now. Load flagged items, cross-reference corpus, recalculate sources, re-tier. You have 90 minutes for this task.**
