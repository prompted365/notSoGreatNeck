# CERT1 Continuous Pillar Discovery + Validation Loop

**Run ID:** cert1-continuous-loop-20251121

## Overview

This is a FLUID system where **discovery → validation → gap-filling → tier-assignment** all inform each other continuously. Every new evidence item immediately triggers:

1. **Backward Citation Search** - Proves it exists in corpus
2. **Soundness Evaluation** - Verifiable? Corroborated? Admissible?
3. **Tier Assignment** - Dynamic tier calculation based on C45 rules
4. **Evidence Building** - Prosecution-ready organization

## Architecture

### Discovery Cycles (Run Sequentially)

**CYCLE 1: Reddit Pillar Discovery**
- Discovers victim reports from Reddit
- AS SOON AS found → backward search corpus for citations
- Calculate effective sources + tier assignment
- Output: `coordination/pillar_reddit_live.json`

**CYCLE 2: Court Records + Cross-Reference**
- Find PACER/NY court records
- AS SOON AS found → search shadowLens for mentions
- If mentioned → upgrade shadowLens from Tier 2 to Tier 1
- Output: `coordination/pillar_courts_live.json`

**CYCLE 3: Video Content + Pattern Detection**
- Find YouTube videos with fraud claims
- AS SOON AS found → search Telegram for promotion
- If promoted → wire fraud count increases
- Output: `coordination/pillar_video_live.json`

**CYCLE 4: Victim Outreach + Blockchain Correlation**
- Contact victims (Reddit DMs, email)
- AS SOON AS wallet obtained → search blockchain corpus
- If matched → upgrade blockchain item Type 9 → Type 3
- Output: `coordination/victim_correlations_live.json`

**CYCLE 5: LinkedIn Profiles + Entity Linking**
- Find professional profiles
- AS SOON AS employment found → update entity map
- New connections → search corpus for mentions
- Output: `coordination/entity_updates_live.json`

### Continuous Processes (Run In Parallel)

**Process A: Backward Citation Searcher**
- Every new item → immediately search all corpus files
- Calculate cross-references in real-time
- Update effective_sources on the fly
- Re-tier items automatically as sources accumulate

**Process B: Soundness Evaluator**
- Every new item → evaluate: verifiable? corroborated? admissible?
- Assign confidence score (0-100)
- Flag items needing additional validation
- Auto-promote items that pass thresholds

**Process C: Tier Assignment Engine**
- Continuously recalculate tiers as new sources found
- Type 6 (single source) → Type 4 (multi-source) when corroborated
- Tier 3 → Tier 2 when sources reach 3.0
- Tier 2 → Tier 1 when fully verified

**Process D: Evidence Builder**
- Organize all items into prosecution-ready structure
- Link related items (victim → transaction → entity → fraud pattern)
- Build case narrative threads
- Generate visual evidence maps

## Integration Points

### Point 1: Reddit Victim → Blockchain → Attribution Upgrade
```
New Reddit victim report
  ↓
Victim provides wallet: 0x7a3f...
  ↓
Backward search blockchain corpus
  ↓
Find matching transaction
  ↓
UPGRADE: Type 9 (attribution-needed) → Type 3 (attributed)
  ↓
Tier upgraded to Tier 1 (prosecution-ready)
```

### Point 2: Court Record → ShadowLens → Verification
```
New court record (1993 Efraim conviction)
  ↓
Search shadowLens for mentions
  ↓
Found: shadowLens claims verified
  ↓
UPGRADE: ShadowLens Tier 2 → Tier 1 (court-verified)
```

### Point 3: LinkedIn → Entity Network → Multi-Source OSINT
```
New LinkedIn profile (Jason Shurka)
  ↓
Extract employment (UNIFYD CEO)
  ↓
Update entity relationship map
  ↓
Search corpus for mentions (125 found)
  ↓
UPGRADE: Type 6 (single source) → Type 4 (multi-source OSINT)
```

### Point 4: Video → Telegram → Wire Fraud Pattern
```
New YouTube video (10K Club promo)
  ↓
Search Telegram for promotion
  ↓
Found: Promoted 47 times on Telegram
  ↓
STRENGTHEN: Type 5 (pattern) evidence
  ↓
Wire fraud count += 47 (interstate commerce)
```

## Quick Start

### Run Complete Loop
```bash
cd /Users/breydentaylor/certainly/visualizations
./scripts/run_continuous_loop.sh
```

This will:
1. Initialize the system
2. Run all 5 discovery cycles
3. Execute all 4 continuous processes
4. Generate final summary report

### Monitor In Real-Time
In a separate terminal:
```bash
./scripts/monitor_continuous_loop.sh
```

### Run Individual Cycles
```bash
# Initialize first
./scripts/cert1_continuous_discovery.sh

# Then run cycles individually
./scripts/cycle1_reddit_discovery.sh
./scripts/cycle2_court_discovery.sh
./scripts/cycle3_video_discovery.sh
./scripts/cycle4_victim_correlation.sh
./scripts/cycle5_linkedin_discovery.sh
```

## Outputs

### Discovery Cycle Outputs
All in `coordination/` directory:

- `pillar_reddit_live.json` - Reddit victim reports
- `pillar_courts_live.json` - Court records
- `pillar_video_live.json` - Video evidence
- `victim_correlations_live.json` - Victim blockchain correlations
- `entity_updates_live.json` - LinkedIn entity links

### Continuous Process Outputs

- `live_evidence_feed.json` - Real-time discoveries
- `tier_updates_log.json` - Tier changes as they happen
- `cross_reference_updates.json` - New correlations
- `prosecution_readiness_live.json` - Current prosecution state

### Supporting Files

- `continuous_loop_state.json` - Global state (cycles + processes)
- `continuous_loop.log` - Detailed execution log
- `prosecution_structure_live.json` - Evidence organization
- `entity_relationship_map.json` - Entity network updates

### Per-Item Processing Files

For each evidence item discovered:
- `backward_search_<item_id>.json` - Citation search results
- `soundness_<item_id>.json` - Soundness evaluation scores
- `tier_assignment_<item_id>.json` - Tier calculation details

## Evidence Type Classification

All discovered items are classified using Evidence Types 1-10:

- **Type 1**: Government records (court filings, SEC docs)
- **Type 2**: Authenticated documents (contracts, bank statements)
- **Type 3**: Blockchain transactions (attributed)
- **Type 4**: Multi-source OSINT (3+ sources)
- **Type 5**: Pattern evidence (documented instances)
- **Type 6**: Single-source leads (HUMINT, single OSINT)
- **Type 7**: Inference (AI analysis, statistical)
- **Type 8**: Derivative (built from other types)
- **Type 9**: Attribution-needed blockchain (tx certain, wallet unknown)
- **Type 10**: AI/LLM analysis (shadowLens, NotebookLM)

## Tier Assignment Rules (C45)

### Tier 1: Certificate and Charge (Prosecution-Ready)
Requires:
- `tx_hash` (blockchain cryptographic proof) OR
- `temporal_anchor` + `subpoena_target` + `principals` (documentary proof)

### Tier 2: One Subpoena Away
Requires:
- `effective_sources >= 3.0` (with notebook discount 0.5x)
- Identified subpoena target
- Clear path to Tier 1

### Tier 3: Investigative Development
Requires:
- `effective_sources >= 2.0`
- Needs corroboration
- Multiple validation paths

### Tier 4: Long-shot / Low-Priority
- Weak leads
- Low confidence score
- Minimal corroboration

### Tier 5: Ruled Out
- Insufficient evidence
- Failed validation
- Abandoned theories

## Continuous Loop Flow

```
┌─────────────────────────────────────────────────────────────┐
│  INITIALIZATION                                             │
│  - Create state files                                       │
│  - Initialize output JSON files                             │
│  - Set up logging                                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  CYCLE 1: Reddit Discovery                                  │
│  → Find victim reports                                      │
│  → Trigger Process A (backward search)                      │
│  → Trigger Process B (soundness eval)                       │
│  → Trigger Process C (tier assignment)                      │
│  → Output: pillar_reddit_live.json                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  CYCLE 2: Court Records                                     │
│  → Find PACER/NY court records                              │
│  → Cross-reference shadowLens                               │
│  → Upgrade shadowLens if verified                           │
│  → Trigger Processes A, B, C                                │
│  → Output: pillar_courts_live.json                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  CYCLE 3: Video Content                                     │
│  → Find YouTube fraud videos                                │
│  → Search Telegram for promotions                           │
│  → Count wire fraud instances                               │
│  → Trigger Processes A, B, C                                │
│  → Output: pillar_video_live.json                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  CYCLE 4: Victim Correlation                                │
│  → Process victim outreach responses                        │
│  → Obtain wallet addresses                                  │
│  → Search blockchain corpus                                 │
│  → Upgrade blockchain attribution                           │
│  → Trigger Processes A, B, C                                │
│  → Output: victim_correlations_live.json                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  CYCLE 5: LinkedIn Entity Linking                           │
│  → Find professional profiles                               │
│  → Extract employment/connections                           │
│  → Update entity relationship map                           │
│  → Search corpus for mentions                               │
│  → Trigger Processes A, B, C                                │
│  → Output: entity_updates_live.json                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  PROCESS D: Evidence Builder (Final Run)                    │
│  → Aggregate all discoveries                                │
│  → Organize by tier and type                                │
│  → Build narrative threads                                  │
│  → Generate prosecution structure                           │
│  → Output: prosecution_readiness_live.json                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  SUMMARY REPORT                                             │
│  → Total discoveries                                        │
│  → Tier upgrades                                            │
│  → Prosecution readiness metrics                            │
│  → Integration points validated                             │
│  → Next actions                                             │
└─────────────────────────────────────────────────────────────┘
```

## Example Results

After running the complete loop:

```
Total Discoveries: 8
Total Tier Upgrades: 3

Cycle 1 (Reddit): 2 victim reports
Cycle 2 (Courts): 2 court records
Cycle 3 (Video): 2 video evidence items
Cycle 4 (Victims): 1 blockchain correlation
Cycle 5 (LinkedIn): 2 entity profiles

Prosecution Readiness:
  Tier 1: 3 items (ready for indictment)
  Tier 2: 4 items (one subpoena away)
  Tier 3: 1 item (investigative development)

Integration Points Validated:
  ✓ Victim wallet → blockchain correlation → attribution upgrade
  ✓ Court record → shadowLens verification → tier upgrade
  ✓ LinkedIn profile → entity map → multi-source OSINT
  ✓ Video content → Telegram promotion → wire fraud count
```

## Validation Rules

### Blockchain Evidence
- Transaction certainty: ALWAYS cryptographic
- Attribution certainty: NEVER certain without KYC
- Use RICO org-benefit theory (not personal ownership claims)

### ShadowLens Evidence
- Type 10 (AI/LLM analysis)
- Tier 2 (pending subpoena for underlying documents)
- Apply notebook discount (0.5x for effective_sources)

### Multi-Source Corroboration
- Corpus sources: 1.0x weight
- Notebook sources: 0.5x weight
- effective_sources = corpus_count + (notebook_count × 0.5)

## Next Actions (After Loop Completion)

1. **Issue Priority 1 Subpoenas**
   - Exchange KYC (Coinbase, Binance, Kraken)
   - Nassau County Clerk (2002 agreement)

2. **Continue Victim Outreach**
   - Reddit DMs to identified victims
   - Request wallet addresses + receipts
   - Build testimonial evidence base

3. **Expand Discovery**
   - More Reddit subreddits
   - PACER federal records
   - Additional LinkedIn profiles

4. **Build Prosecution Narrative**
   - Link victims → transactions → entities → patterns
   - Map RICO enterprise structure
   - Generate visual evidence maps

## Technical Notes

### Dependencies
- `bash` (tested on macOS)
- `jq` (for JSON processing)
- `bc` (for floating-point calculations)
- `grep` (for corpus searches)

### Performance
- All processes run in parallel where possible
- Backward searches use efficient grep patterns
- State files prevent duplicate processing

### Extensibility
- Add new discovery cycles by creating `cycle6_*.sh`
- Add new continuous processes in separate scripts
- Modify tier rules in `tier_assignment_engine.sh`
- Extend evidence types in individual cycle scripts

## Troubleshooting

### No discoveries found
- Check corpus file paths in cycle scripts
- Verify search terms are correct
- Review `continuous_loop.log` for errors

### Tier not upgrading
- Check backward search results (effective_sources)
- Review soundness evaluation (confidence score)
- Verify C45 tier requirements met

### Missing output files
- Ensure `coordination/` directory exists
- Check script permissions (`chmod +x`)
- Review initialization step completion

## Support

For questions or issues:
- Review `coordination/continuous_loop.log` for detailed logs
- Check `coordination/continuous_loop_state.json` for system state
- Examine per-item processing files for debugging

---

**Generated:** 2025-11-21
**Run ID:** cert1-continuous-loop-20251121
**System:** CERT1 Continuous Pillar Discovery + Validation Loop
