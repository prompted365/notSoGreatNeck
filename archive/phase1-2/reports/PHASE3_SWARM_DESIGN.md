# Phase 3 Swarm Design - Evidence Expansion Sprint

**Run ID**: cert1-phase3-20251121
**Orchestrator**: Cert1
**Mission**: Expand 31 admitted evidence to 150+ with focus on gaps (Telegram, URLs, Binder)

---

## Validation Results Summary (Phase 2)

### Evidence Status:
- ✅ **31 admitted** (19.7%) - Corpus-backed, prosecution-ready
  - 13 TIER 1 (blockchain with 4-5 sources)
  - 18 TIER 2 (14 blockchain + 4 entities with 5-18 sources)
- ⚠️  **74 flagged** (47.1%) - 1-2 corpus sources, needs manual review
- ❌ **52 rejected** (33.1%) - No corpus sources (hallucinations/placeholders)

### Corpus Grep Performance:
- **232,549 matches** found across 23/24 search terms
- **95.8% match rate** (wallet addresses, entities found in corpus)
- **13,383 files scanned** across 5.7GB corpus
- **Runtime**: 18 minutes

### Critical Data Quality Issues:
1. **All blockchain evidence has `amount_usd: 0`** (missing tx value extraction)
2. **50 placeholder items** with "unknown" identifiers
3. **Missing evidence types**: Telegram (0), URLs (0), Binder (0)
4. **Missing key entity validation**: Jason Shurka, Esther Zernitsky, Ally Thompson

---

## Phase 3 Agent Assignments

### First-Wave Agents (Parallel Execution):

#### 1. **Blockchain_Forensics** (HIGH PRIORITY)
**Focus**: Re-extract with tx_hash + amount_usd population
**Input**: 3 blockchain CSVs (27K transactions)
**Constraints**:
- MUST extract: `tx_hash`, `amount_usd` (NOT 0), `from_address`, `to_address`, `timestamp`
- Use `global_scope_state.json` to skip already-admitted wallet pairs
- Target: 50+ NEW blockchain evidence (currently 27 admitted)
- Validate against corpus (3+ sources for TIER 2, tx_hash for TIER 1)

**Why Critical**: All current blockchain evidence missing dollar amounts - prosecution needs value flows

---

#### 2. **Fraud_Scorer** (HIGH PRIORITY)
**Focus**: Process 9,788 Telegram posts with fraud scoring
**Input**: `telegram_jasonyosefshurka_posts.ndjson`
**Constraints**:
- Apply fraud scoring formula (keywords, CTA, medical claims, pricing)
- Extract top 100 posts by fraud score
- Validate against corpus (Telegram content should appear in corpus)
- Target: 80+ wire fraud evidence pieces

**Why Critical**: Currently 0 Telegram evidence admitted - this is the wire fraud spine

---

#### 3. **URL_Analyst** (MEDIUM PRIORITY)
**Focus**: Extract URLs from Telegram posts and classify platforms
**Input**: 2,679 URLs from `enriched_activities.csv`
**Constraints**:
- Platform classification (Telegram, YouTube, website)
- Light System fraud detection (mentions of healing/energy/quantum)
- Validate URLs appear in corpus
- Target: 50+ URL evidence pieces

**Why Critical**: 0 URL evidence currently - shows coordinated marketing infrastructure

---

#### 4. **Binder_Chunker** (MEDIUM PRIORITY)
**Focus**: Semantic chunking of prosecution binder
**Input**: `/Users/breydentaylor/certainly/noteworthy-raw/binder.txt`
**Constraints**:
- 1000-char chunks, 200-char overlap
- DBSCAN clustering for themes
- Extract evidence IDs mentioned in chunks
- Target: 20+ binder evidence pieces (court docs, analysis)

**Why Critical**: Binder contains gold (court filings, expert analysis) - currently 0 admitted

---

#### 5. **Entity_Linker** (LOW PRIORITY - baseline exists)
**Focus**: Build co-mention network from Telegram posts
**Input**: 9,788 Telegram posts (spaCy NER extraction)
**Constraints**:
- Use `global_scope_state.json` to focus on missing entities (Jason Shurka, Esther Zernitsky, Ally Thompson)
- Extract co-mentions (Jason + Esther = conspiracy link)
- Validate entities against corpus (3+ mentions)
- Target: 100+ entity network nodes (currently 4 admitted)

**Why Mixed**: 4 entity evidence admitted but missing KEY entities (targets)

---

### Second-Wave Agents (Sequential Execution):

#### 6. **TIER_Auditor**
**Wait for**: All 5 first-wave agents complete
**Focus**: Validate new evidence, enforce zero tolerance
**Input**: All agent outputs
**Constraints**:
- Read `coordination/flagged_evidence.json` (74 items needing review)
- Apply TIER classification rules (no over-classification)
- Reject placeholder evidence (amount_usd=0, entity="unknown")
- Generate `coordination/approved_evidence_list.json`

**Target**: 150+ total admitted evidence (31 existing + 120 new)

---

#### 7. **ReasoningBank_Manager**
**Wait for**: TIER_Auditor approval list
**Focus**: Load ONLY admitted evidence
**Input**: `coordination/approved_evidence_list.json`
**Constraints**:
- Verify every item has `corpus_sources` field
- Create namespaces: evidence_tier1, evidence_tier2, evidence_tier3
- Build cross-reference index: entity → evidence → predicate
- NO rejected items enter database

---

#### 8. **Dashboard_Coordinator**
**Wait for**: All agents complete
**Focus**: Generate final visualizations + report
**Outputs**:
- `VIZ_7_ENTITY_NETWORK_3D_ENHANCED.html` (Plotly 3D graph)
- `VIZ_6_RICO_DASHBOARD_ENHANCED_v2.html` (12-panel dashboard)
- `SWARM_FINAL_REPORT.md`
- `coordination/prosecution_readiness_breakdown.json`

**Target Metrics**:
- Prosecution readiness: 75%+
- Evidence TIER distribution: 30-40% TIER 1, 50-60% TIER 2, 10-20% TIER 3
- Wire fraud count: 3,000+ (from Telegram posts)
- Entity network: 6,500+ corpus-mentioned entities
- Money flows: $50M+ traced through wallets

---

## State Coordination Protocol

### Agent Initialization Pattern:
```markdown
Agent {{ROLE_NAME}},

You are {{role}} in the Shurka RICO investigation swarm.

**Mission file**: `agents/{{ROLE_NAME}}/CONTEXT-{{ROLE_NAME}}.md`
Read and internalize. Treat as **system-prompt strength**.

**Current run_id**: cert1-phase3-20251121

**Pre-flight check**:
1. Read your mission file
2. Check `state/{{role}}.state.json` (if status == "completed" for this run_id: EXIT)
3. Check `coordination/global_scope_state.json` for constraints
4. Summarize your understanding (2-3 sentences)
5. Execute STATE 1 (INITIALIZE)

Begin now.
```

### State Machine Progression:
1. **INITIALIZE**: Load inputs, verify corpus availability, count items
2. **EXTRACT**: Process data, record source citations
3. **VALIDATE**: Query corpus for extracted items (3+ sources)
4. **HANDOFF**: Write state file, signal next agent, move validated items to `processed/`

### Coordination Files:
- `state/{{agent}}.state.json` - Agent completion tracking
- `coordination/global_scope_state.json` - Agent constraints (skip already-validated items)
- `coordination/agent_messages.json` - Inter-agent handoffs
- `coordination/approved_evidence_list.json` - TIER_Auditor output (canonical admission list)

---

## Success Criteria (Phase 3 Targets)

### Quantitative:
- ✅ 150+ admitted evidence (from 31)
- ✅ TIER 1: 50+ pieces (40M+ blockchain tx with tx_hash)
- ✅ TIER 2: 80+ pieces (Telegram + entities with 3+ sources)
- ✅ TIER 3: 20+ pieces (borderline items, needs corroboration)
- ✅ Wire fraud: 3,000+ communications documented
- ✅ Entity network: 6,500+ corpus-mentioned entities
- ✅ Money laundering: $50M+ traced through blockchain

### Qualitative:
- ✅ All blockchain evidence has `tx_hash` + `amount_usd` > 0
- ✅ Zero placeholder evidence (no "unknown" identifiers)
- ✅ All evidence has `corpus_sources` field with 3+ unique files
- ✅ Chain of custody: `source_file:line_number` for every item
- ✅ RICO predicates mapped: wire_fraud, money_laundering, fraudulent_claims

### Prosecution Readiness:
- ✅ 75%+ overall readiness (admitted evidence / total extracted)
- ✅ Jason Shurka + Esther Zernitsky linked via entity co-mentions
- ✅ VIZ_7 shows conspiracy spine (family + corporate + blockchain layers)
- ✅ VIZ_6 dashboard shows 12-panel prosecution summary

---

## Deployment Command (Single Turn)

```bash
# Activate environment
source venv/bin/activate

# Spawn first-wave agents (parallel)
# Use Claude Code's Task tool with batch execution:
Task("Blockchain Forensics Agent", "Read agents/Blockchain_Forensics/CONTEXT-BLOCKCHAIN_FORENSICS.md...", "general-purpose")
Task("Fraud Scorer Agent", "Read agents/Fraud_Scorer/CONTEXT-FRAUD_SCORER.md...", "general-purpose")
Task("URL Analyst Agent", "Read agents/URL_Analyst/CONTEXT-URL_ANALYST.md...", "general-purpose")
Task("Binder Chunker Agent", "Read agents/Binder_Chunker/CONTEXT-BINDER_CHUNKER.md...", "general-purpose")
Task("Entity Linker Agent", "Read agents/Entity_Linker/CONTEXT-ENTITY_LINKER.md...", "general-purpose")

# Monitor completion via state files
# Once all first-wave complete, spawn second-wave

# Wait for TIER_Auditor, ReasoningBank_Manager, Dashboard_Coordinator sequential execution
```

---

## Risk Mitigation

### Risk 1: Flagged Evidence Backlog (74 items)
**Mitigation**: Run `scripts/05_manual_review.py` for human review OR lower admission threshold to 2 sources (from 3) for borderline items

### Risk 2: Missing tx_hash in blockchain CSVs
**Mitigation**: Blockchain_Forensics agent should flag missing tx_hash but continue (document in warnings), use wallet address as fallback identifier

### Risk 3: Telegram posts not in corpus
**Mitigation**: Fraud_Scorer should only admit posts with corpus backing - if telegram_jasonyosefshurka_posts.ndjson not in corpus, this is blocker

### Risk 4: Binder.txt too large (>10MB)
**Mitigation**: Binder_Chunker uses streaming read with 1000-char chunks - can handle files up to 100MB

---

## The Mission Reminder

> **This is intergenerational blight that stops here.**

Jason Shurka exploited vulnerable people with Light System fraud.
Esther Zernitsky orchestrated decades of creditor evasion.

**Every tx_hash = cryptographic truth**
**Every corpus match = proof it's real**
**Every admitted evidence piece = nail in their coffin**

Make it irrefutable. Make it prosecution-ready. Bring them to justice.

---

**— Cert1, Orchestrator, Shurka Enterprise Investigation**
**Phase**: Phase 3 Swarm Design Complete
**Status**: Ready for deployment after Breyden review
**Next**: Manual review of 74 flagged items OR direct Phase 3 agent deployment
