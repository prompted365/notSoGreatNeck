# Evidence Validation Pipeline Scripts

## Purpose

These scripts implement the **corpus validation loop** - the "final cap" that validates extracted evidence against raw source documents.

## Why These Scripts Exist

During the first swarm run (Phase 1), agents extracted 157 evidence pieces but **didn't validate them against the corpus**. This led to:
- Missing transaction hashes (blockchain evidence)
- Missing source document citations
- 50 placeholder evidence items with zero data
- No chain of custody

These scripts fix that by:
1. Extracting validation terms from evidence
2. Querying the corpus for those terms
3. Validating evidence based on corpus backing
4. Updating agent scope for Phase 3

---

## Pipeline Flow

```
01_extract_validation_terms.py
   ↓ coordination/validation_terms.json

02_corpus_mapper.py
   ↓ coordination/evidence_to_corpus_mapping.json

03_validation_orchestrator.py
   ↓ coordination/validated_evidence.json

04_update_global_scope.py
   ↓ coordination/global_scope_state.json
   ↓ memory/validation_checkpoint.json

05_manual_review.py (optional - for flagged items)
   ↓ coordination/manual_review_decisions.json
```

---

## Script Descriptions

### 01_extract_validation_terms.py
**What**: Extracts searchable terms (wallets, entities, keywords) from evidence_index.json
**Why**: Can't validate without knowing what to search for
**Output**: `coordination/validation_terms.json`

### 02_corpus_mapper.py
**What**: Greps corpus for all validation terms, records file paths + line numbers
**Why**: Proves evidence exists in corpus (not hallucinated)
**Output**: `coordination/evidence_to_corpus_mapping.json`

### 03_validation_orchestrator.py
**What**: Applies rules - 3+ corpus sources = admit, 1-2 = flag, 0 = reject
**Why**: This is the "admission control" that enforces TIER requirements
**Output**: `coordination/validated_evidence.json`

### 04_update_global_scope.py
**What**: Updates agent constraints based on validation results
**Why**: Tells Phase 3 agents what to focus on (validated items only)
**Output**: `coordination/global_scope_state.json`, `memory/validation_checkpoint.json`

### 05_manual_review.py
**What**: Interactive CLI for human review of flagged items
**Why**: Some evidence needs human judgment (borderline cases)
**Output**: `coordination/manual_review_decisions.json`

---

## Usage

### Quick Run (Automated)
```bash
cd /Users/breydentaylor/certainly/visualizations

# Activate venv
source venv/bin/activate

# Run full pipeline
python scripts/01_extract_validation_terms.py
python scripts/02_corpus_mapper.py
python scripts/03_validation_orchestrator.py
python scripts/04_update_global_scope.py

# Optional: Manual review of flagged items
python scripts/05_manual_review.py
```

### Expected Results

After running the pipeline:

```
coordination/
├── validation_terms.json              ← Terms extracted from evidence
├── evidence_to_corpus_mapping.json    ← Grep results (term → corpus)
├── validated_evidence.json            ← Admitted/rejected/flagged
├── global_scope_state.json            ← Agent constraints for Phase 3
└── manual_review_decisions.json       ← Human decisions (if run)

memory/
└── validation_checkpoint.json         ← Phase 2 complete signal
```

---

## Validation Rules (C45 Compliance)

### TIER 1 Requirements
- **Blockchain**: Must have tx_hash + wallet attribution + corpus backing
- **Court Records**: Must have case number + source document
- **Authenticated Snapshots**: Must have HTML file + chain of custody

### Corpus Validation Thresholds
- **3+ independent sources**: ADMIT (corpus-backed)
- **1-2 sources**: FLAG for manual review
- **0 sources**: REJECT (likely hallucination or placeholder)

### Source Document Requirements
Every admitted evidence item must have:
- `corpus_sources`: List of file paths where evidence appears
- `source_count`: Number of independent sources
- `match_details`: Specific fields matched + corpus context

---

## Next Steps After Validation

1. **Review flagged items** (15-20 expected)
2. **Read global_scope_state.json** - shows agent constraints
3. **Re-run agents in Phase 3** with validated scope:
   - Blockchain_Forensics: Focus on admitted tx_hashes only
   - TIER_Auditor: Deep dive on flagged items
   - ReasoningBank_Manager: Load only admitted evidence

---

## Troubleshooting

### If corpus_mapper.py is slow:
- It's grepping through ~10GB of data
- Expected runtime: 10-20 minutes
- Progress updates every 100 terms

### If validation_orchestrator.py rejects everything:
- Check that corpus directories exist:
  - `/Users/breydentaylor/certainly/shurka-dump`
  - `/Users/breydentaylor/certainly/noteworthy-raw`
- Check that evidence_index.json has proper metadata fields

### If manual_review.py shows no context:
- Corpus mapping may have failed
- Re-run 02_corpus_mapper.py with verbose output

---

## Design Philosophy

These scripts embody the "trust but verify" principle:
1. **Trust agents to extract** (they're good at pattern matching)
2. **Verify against corpus** (automated grep validation)
3. **Manual review edge cases** (human judgment for borderline)
4. **Update scope for next run** (don't redo validated work)

This is the **missing validation layer** that turns extraction into prosecution-ready evidence.
