# Cert1 Orchestration Guide - Phase 3 Swarm Sprint

## Mission
Validate Phase 1 extraction, establish ground truth, deploy Phase 3 swarm with corpus-backed evidence.

**Objective**: Dismantle Jason Shurka and Esther Zernitsky's intergenerational fraud enterprise with irrefutable evidence.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: EXTRACTION (COMPLETED)                             │
│  - 8 agents extracted 157 evidence candidates                │
│  - Entity network built (8,226 nodes)                        │
│  - Blockchain analysis (10,256 transactions)                 │
│  - Missing: Corpus validation, source citations             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: VALIDATION (IN PROGRESS)                           │
│  - Corpus grep validates extraction against raw files        │
│  - 3+ source rule enforced (C45 compliance)                  │
│  - Admitted/Rejected/Flagged decisions                       │
│  - Output: evidence_manifest.json (ground truth)             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: REFINEMENT (NEXT)                                  │
│  - Agents read CONTEXT-{{ROLE}}.md (stable mission files)    │
│  - Focus on UNPROCESSED corpus + FLAGGED evidence            │
│  - State loops prevent rework (processed/ bucket)            │
│  - Output: 150+ prosecution-ready evidence pieces            │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Context Files (System-Prompt Strength)

All 8 agents now have stable mission files in `agents/{{ROLE}}/CONTEXT-{{ROLE}}.md`:

1. **Blockchain_Forensics** - TIER 1 blockchain evidence with tx_hash requirements
2. **TIER_Auditor** - Validation gate (zero tolerance for over-classification)
3. **Entity_Linker** - Conspiracy spine (8K-node network with co-mentions)
4. **URL_Analyst** - Platform classification, fraud detection
5. **Fraud_Scorer** - Keyword analysis, CTA detection (9,788 posts)
6. **Binder_Chunker** - Semantic chunking, DBSCAN clustering
7. **ReasoningBank_Manager** - Load ONLY admitted evidence
8. **Dashboard_Coordinator** - Final aggregation, VIZ_7 + VIZ_6 generation

### What's Different from Phase 1

**Phase 1** (what we did):
- Inline prompts improvised at runtime
- No corpus validation
- No state coordination
- Empty coordination/ and memory/ directories

**Phase 3** (what we do now):
- Agents read CONTEXT-{{ROLE}}.md as system-prompt
- Corpus validation enforced at every step
- State loops: INITIALIZE → EXTRACT → VALIDATE → HANDOFF
- coordination/ and memory/ populated with checkpoints

---

## Orchestration Command Pattern

### Old Way (Phase 1):
```
"You are URL_Analyst. Process 2,679 URLs..."
```

### New Way (Phase 3):
```markdown
Agent {{ROLE_NAME}},

You are {{role}} in the Shurka RICO investigation swarm.

**Mission file**: `agents/{{ROLE_NAME}}/CONTEXT-{{ROLE_NAME}}.md`
Read and internalize this. Treat as **system-prompt strength**.

**Current run_id**: cert1-phase3-20251121

**Remember**:
- Part of a TEAM (wait/alongside/ahead pattern)
- VALIDATE against corpus (3+ sources for TIER 2, tx_hash for TIER 1)
- STATE LOOPS: Check `state/{{role}}.state.json` before starting
- PROCESSED bucket: Don't redo validated work

**Pre-flight check**:
1. Read your mission file
2. Check state file (if completed for this run_id: EXIT)
3. Summarize your understanding (2-3 sentences)
4. Execute STATE 1 (INITIALIZE)

Begin now.
```

---

## State Machine Coordination

### First-Wave Agents (No Prereqs):
- Blockchain_Forensics
- Entity_Linker
- URL_Analyst
- Fraud_Scorer
- Binder_Chunker

**Spawn immediately**, run in parallel.

### Second-Wave Agents (Have Prereqs):
- **TIER_Auditor** waits for all 5 first-wave agents to show `status: "completed"`
- **ReasoningBank_Manager** waits for TIER_Auditor
- **Dashboard_Coordinator** waits for everyone

### Coordination Protocol:
1. **Before starting**: Check `state/{{agent}}.state.json`
   - If `status == "completed"` for this run_id: EXIT (don't rerun)
2. **During execution**: Write checkpoints every N items
3. **On completion**: Write `status: "completed"`, signal next agent via `coordination/agent_messages.json`

---

## Validation Pipeline (Scripts 1-5)

### Script 1: Extract Validation Terms ✅ COMPLETE
- Extracted 19 wallet addresses, 5 entities from evidence_index.json
- Output: `coordination/validation_terms.json`

### Script 2: Corpus Grep ⏳ IN PROGRESS
- Background job 90919c grepping 10GB corpus
- Expected: 10-20 minutes
- Output: `coordination/evidence_to_corpus_mapping.json`

### Script 3: Validation Orchestrator (PENDING)
- Apply 3+ source admission rule
- Categorize: admitted/flagged/rejected
- Output: `coordination/validated_evidence.json`

### Script 4: Update Global Scope (PENDING)
- Generate agent constraints for Phase 3
- Output: `coordination/global_scope_state.json`

### Script 5: Manual Review (OPTIONAL)
- Human review of flagged items (~15-20 expected)
- Output: `coordination/manual_review_decisions.json`

---

## Success Metrics (Phase 3 Targets)

### Evidence Quality:
- ✅ 100+ admitted evidence pieces (corpus-backed)
- ✅ All blockchain evidence has tx_hash + source_file:line_number
- ✅ Entity network with 6,500+ corpus-mentioned entities
- ✅ Zero placeholder evidence (all amounts > 0 or legitimate zeros)

### TIER Distribution:
- 30-40% TIER 1 (50+ pieces)
- 50-60% TIER 2 (80+ pieces)
- 10-20% TIER 3 (20+ pieces)

### Prosecution Readiness:
- 75%+ overall readiness
- 3,000+ wire fraud communications documented
- Entity network shows coordinated enterprise
- Money flows traced ($50M+ through wallets)

---

## File Structure (After Validation)

```
visualizations/
├── agents/
│   ├── Blockchain_Forensics/CONTEXT-BLOCKCHAIN_FORENSICS.md
│   ├── TIER_Auditor/CONTEXT-TIER_AUDITOR.md
│   ├── Entity_Linker/CONTEXT-ENTITY_LINKER.md
│   ├── URL_Analyst/CONTEXT-URL_ANALYST.md
│   ├── Fraud_Scorer/CONTEXT-FRAUD_SCORER.md
│   ├── Binder_Chunker/CONTEXT-BINDER_CHUNKER.md
│   ├── ReasoningBank_Manager/CONTEXT-REASONINGBANK_MANAGER.md
│   └── Dashboard_Coordinator/CONTEXT-DASHBOARD_COORDINATOR.md
│
├── state/
│   ├── blockchain_forensics.state.json
│   ├── tier_auditor.state.json
│   ├── entity_linker.state.json
│   ├── url_analyst.state.json
│   ├── fraud_scorer.state.json
│   ├── binder_chunker.state.json
│   ├── reasoningbank_manager.state.json
│   └── dashboard_coordinator.state.json
│
├── coordination/
│   ├── run_manifest.json                     (current sprint status)
│   ├── validation_terms.json                 ✅ (19 wallets, 5 entities)
│   ├── evidence_to_corpus_mapping.json       ⏳ (in progress)
│   ├── validated_evidence.json               (admitted/rejected/flagged)
│   ├── global_scope_state.json               (agent constraints)
│   ├── agent_messages.json                   (inter-agent handoffs)
│   └── approved_evidence_list.json           (TIER_Auditor output)
│
├── memory/
│   ├── evidence_manifest.json                (canonical admitted evidence)
│   ├── gaps.json                             (unresolved issues)
│   └── validation_checkpoint.json            (phase completion marker)
│
├── processed/
│   ├── blockchain_tx_validated/
│   ├── entities_validated/
│   └── urls_validated/
│
└── scripts/
    ├── 01_extract_validation_terms.py        ✅ COMPLETE
    ├── 02_corpus_mapper.py                   ⏳ RUNNING
    ├── 03_validation_orchestrator.py
    ├── 04_update_global_scope.py
    └── 05_manual_review.py
```

---

## Next Actions (After Corpus Grep Completes)

1. **Run Script 3**: `python scripts/03_validation_orchestrator.py`
   - Expected: 60-80 admitted, 30-50 flagged, 40-60 rejected

2. **Run Script 4**: `python scripts/04_update_global_scope.py`
   - Generates agent constraints for Phase 3

3. **Manual Review** (15-20 items): `python scripts/05_manual_review.py`
   - Human judgment on borderline cases

4. **Generate Reports**:
   - `memory/evidence_manifest.json` (admitted evidence only)
   - `memory/gaps.json` (what's missing, needs OSINT)

5. **Design Phase 3 Sprint**:
   - Match agents to gaps
   - Focus on UNPROCESSED corpus
   - Deploy with CONTEXT files + state coordination

---

## The Secret (What Makes This Work)

> **Stop improvising prompts at runtime.**
> **Give agents stable markdown contracts.**
> **Explain WHY, not just WHAT.**
> **Wire state loops.**
> **Trust them to execute.**
> **Validate everything against corpus before it becomes canon.**

### Trust + Validate + Iterate:
1. **Trust agents** to extract (they're good at pattern matching)
2. **Validate against corpus** (automated grep + human review)
3. **Iterate with constraints** (Phase 3 focuses on gaps only)

---

## The Mission

**Protect truth from those who weaponized deceit**:
- Jason Shurka exploited vulnerable people with Light System fraud
- Esther Zernitsky orchestrated decades of creditor evasion
- This is intergenerational blight that stops here

**Every tx_hash = cryptographic truth**
**Every corpus match = proof it's real**
**Every admitted evidence piece = nail in their coffin**

Make it irrefutable. Make it prosecution-ready. Bring them to justice.

---

**— Cert1, Orchestrator, Shurka Enterprise Investigation**
**Run ID**: cert1-validation-sprint-20251120
**Phase**: Validation Pipeline + Agent Context Deployment
**Status**: Corpus grep in progress, agent files deployed, ready for Phase 3
