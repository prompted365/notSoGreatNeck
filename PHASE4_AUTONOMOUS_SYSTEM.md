# Phase 4 Autonomous Investigation System

**Date**: 2025-11-21
**Status**: ✅ READY FOR DEPLOYMENT
**Mode**: Autonomous continuation with exit criteria

---

## WHAT I BUILT FOR YOU

### 🎯 **Autonomous Loop System**

Phase 4 will **run until prosecution-ready** with these exit criteria:

```bash
STOP when ALL of these are met:
  ✅ Tier 1 evidence >= 60 items (up from 44)
  ✅ Unfilled gaps < 100 (down from 1,140)
  ✅ Blockchain attribution > 75% (up from 15%)
  ✅ Prosecution readiness >= 85% (up from 78%)

Safety: Max 5 loops to prevent infinite runs
```

### 📋 **Hook Scripts Created**

1. **`scripts/hooks/pre_agent_spawn.sh`**
   - Checks if agent already completed (avoid duplicate work)
   - Checks prerequisites (wait for upstream agents)
   - Blocks tool use if conditions not met
   - Initializes state file

2. **`scripts/hooks/post_agent_complete.sh`**
   - Updates agent state to "completed"
   - Updates global scope state
   - Emits completion notification

3. **`scripts/hooks/subagent_handoff.sh`**
   - Writes handoff file for downstream agents
   - Updates evidence manifest with counts
   - Emits handoff notification

4. **`scripts/hooks/check_exit_criteria.sh`**
   - Calculates current metrics (Tier 1 count, gaps, attribution rate, readiness)
   - Compares to targets
   - Returns exit code: 0 = STOP, 1 = CONTINUE

5. **`scripts/hooks/session_complete.sh`**
   - Checks if all agents completed
   - Runs exit criteria check
   - If criteria MET → Generate final package, STOP
   - If criteria NOT MET → Loop back (up to 5 times)
   - If max loops → Generate interim package, STOP

### ⚙️ **Hooks Configuration**

Configured in `.claude/settings.local.json`:
- **PreToolUse**: Before each Task tool spawn → check if agent already done, check dependencies
- **PostToolUse**: After each Task completes → update state
- **SubagentStop**: When agent finishes → write handoff
- **SessionEnd**: When session ends → check exit criteria, loop or finalize

### 📁 **Files Created**

```
visualizations/
├── CONTEXT-CERT1.md               ← My system prompt (who I am, what I do)
├── PHASE3_DEFENSIVE_METRICS_AUDIT.md  ← What Phase 3 got wrong
├── PHASE4_AUTONOMOUS_SYSTEM.md    ← This file (deployment guide)
├── .claude/settings.local.json    ← Hooks configured
├── coordination/
│   └── global_scope_state.json    ← Run state, loop count, exit criteria
├── scripts/hooks/
│   ├── pre_agent_spawn.sh         ← PreToolUse hook
│   ├── post_agent_complete.sh     ← PostToolUse hook
│   ├── subagent_handoff.sh        ← SubagentStop hook
│   ├── check_exit_criteria.sh     ← Exit criteria calculator
│   └── session_complete.sh        ← SessionEnd hook (loop controller)
└── agents/
    ├── Corpus_Validator/          ← (Need to create CONTEXT file)
    ├── Gap_Filler/                ← (Need to create CONTEXT file)
    └── Subpoena_Coordinator/      ← (Need to create CONTEXT file)
```

---

## HOW IT WORKS

### **Single Message Deployment**

You say:
```
Deploy Phase 4 autonomous investigation:
- Corpus_Validator (re-validate 817 items as Types 1-10, Tiers 1-5)
- Gap_Filler (process 1,140 flagged items)
- Subpoena_Coordinator (generate subpoena package)

Run ID: cert1-phase4-autonomous-20251121
Continue until exit criteria met (max 5 loops)
```

### **What Happens**

```
Loop 1:
  ↓ Task spawns Corpus_Validator
  ↓ PreToolUse hook: Check state (not done) → ALLOW
  ↓ Corpus_Validator runs (re-validates 817 items)
  ↓ PostToolUse hook: Update state to "completed"
  ↓ SubagentStop hook: Write handoff

  ↓ Task spawns Gap_Filler
  ↓ PreToolUse hook: Check dependency (Corpus_Validator done) → ALLOW
  ↓ Gap_Filler runs (processes 1,140 flagged items)
  ↓ PostToolUse + SubagentStop hooks fire

  ↓ Task spawns Subpoena_Coordinator
  ↓ PreToolUse hook: Check dependency (Gap_Filler done) → ALLOW
  ↓ Subpoena_Coordinator runs (generates subpoena package)
  ↓ PostToolUse + SubagentStop hooks fire

  ↓ SessionEnd hook fires
  ↓ check_exit_criteria.sh runs:
      - Tier 1: 45/60 ❌
      - Gaps: 950/100 ❌
      - Attribution: 20%/75% ❌
      - Readiness: 79%/85% ❌
  ↓ Exit criteria NOT MET → CONTINUE (Loop 2)

Loop 2:
  [Same process, agents work on updated data]
  ↓ SessionEnd hook fires
  ↓ check_exit_criteria.sh:
      - Tier 1: 58/60 ❌
      - Gaps: 200/100 ❌
      - Attribution: 65%/75% ❌
      - Readiness: 83%/85% ❌
  ↓ Exit criteria NOT MET → CONTINUE (Loop 3)

Loop 3:
  [Agents continue refining]
  ↓ SessionEnd hook fires
  ↓ check_exit_criteria.sh:
      - Tier 1: 62/60 ✅
      - Gaps: 85/100 ✅
      - Attribution: 78%/75% ✅
      - Readiness: 87%/85% ✅
  ↓ EXIT CRITERIA MET → STOP

  ↓ Generate final prosecution package
  ↓ Output: handoff-binder/
      - PHASE4_FINAL_REPORT.md
      - evidence_inventory.json (Types 1-10, Tiers 1-5)
      - subpoena_package.md (priority targets)
      - blockchain_attribution_map.json
      - gap_analysis.json

🎉 INVESTIGATION COMPLETE
```

---

## WHAT'S LEFT TO CREATE

### **Agent Context Files** (3 files needed)

**1. `agents/Corpus_Validator/CONTEXT-CORPUS_VALIDATOR.md`**

Mission:
- Re-validate Phase 3's 817 evidence items using Types 1-10 + Tiers 1-5
- Apply corrections from PHASE3_DEFENSIVE_METRICS_AUDIT.md:
  - Blockchain: Type 3/9, Tier 2, separate transaction vs attribution
  - shadowLens: Type 10, Tier 2, mark "NotebookLM summary, pending subpoena"
  - URLs: Type 5, Tier 3, correct "15-20 domains" not "1,000 URLs"
- Output: `coordination/phase3_revalidated_evidence.json`

**2. `agents/Gap_Filler/CONTEXT-GAP_FILLER.md`**

Mission:
- Process 1,140 flagged items from Phase 3
- Attempt corpus cross-reference (search Telegram, blockchain, shadowLens for additional sources)
- Calculate effective_sources with notebook discount (0.5x)
- Re-tier: 3.0+ → Tier 2, 2.0+ → Tier 3, <2.0 → Keep flagged
- Output: `coordination/gap_fill_results.json`

**3. `agents/Subpoena_Coordinator/CONTEXT-SUBPOENA_COORDINATOR.md`**

Mission:
- Identify all evidence with `tier_if_confirmed: 1` or `tier_if_confirmed: 2`
- Group by subpoena target (exchanges, Nassau County, NY State Court, PDI Bank)
- For each target:
  - Priority (P1/P2/P3)
  - Expected yield (what becomes prosecution-ready)
  - Evidence IDs (list of dependent items)
  - Draft subpoena language
- Output: `coordination/subpoena_package.md`

---

## DEPLOYMENT COMMAND

When you're ready, just say:

```
Deploy Phase 4 autonomous investigation.

Run ID: cert1-phase4-autonomous-20251121

Deploy these agents in sequence (hooks will coordinate):
1. Corpus_Validator - Re-validate 817 Phase 3 items as Types 1-10, Tiers 1-5
2. Gap_Filler - Process 1,140 flagged items, attempt corpus cross-reference
3. Subpoena_Coordinator - Generate subpoena package with priorities

Exit criteria:
- Tier 1 >= 60 items
- Unfilled gaps < 100
- Blockchain attribution > 75%
- Prosecution readiness >= 85%

Continue looping until criteria met (max 5 loops).
Hooks will handle state management and continuation automatically.
```

Then I'll:
1. Create the 3 agent context files
2. Spawn all 3 agents in single message
3. Hooks coordinate sequential execution
4. After each loop, check exit criteria
5. Either continue or generate final package
6. Report back when prosecution-ready

---

## EXIT CRITERIA DETAILS

### **Tier 1 Count: Current 44 → Target 60**

**How to improve**:
- Subpoena Nassau County for 2002 agreement → Upgrade from Tier 2 to Tier 1
- Subpoena exchange KYC for top blockchain wallets → Upgrade Type 9 to Type 3, Tier 2 to Tier 1
- shadowLens documents verified → Upgrade from Tier 2 (pending) to Tier 1 (confirmed)

**Metric calculated by**: Counting items in `memory/evidence_manifest.json` with `tier: 1`

### **Unfilled Gaps: Current 1,140 → Target < 100**

**How to improve**:
- Gap_Filler finds additional corpus sources → Upgrade flagged items to Tier 3
- Cross-reference shadowLens with Telegram/blockchain → Boost effective_sources
- Manual review of borderline items → Some may be promotable

**Metric calculated by**: Counting items in `coordination/gap_analysis.json` with `status: "unfilled"`

### **Blockchain Attribution: Current 15% → Target 75%**

**How to improve**:
- Exchange KYC subpoenas → Convert "pending_subpoena" to "known"
- Wallet clustering analysis → Link wallets to known entities
- Forensic analysis of transaction patterns → Strengthen attribution basis

**Metric calculated by**: `(wallets with attribution="known") / (total wallets) * 100`

### **Prosecution Readiness: Current 78% → Target 85%**

**How to improve**:
- Increase Tier 1 count (weighted 3x)
- Increase Tier 2 count (weighted 2x)
- Reduce unfilled gaps

**Formula**: `(Tier1 * 3 + Tier2 * 2) / 2 + (100 - unfilled_gaps / 10)`

---

## SAFETY FEATURES

### **Max 5 Loops**

Prevents infinite running if exit criteria never met.

After 5 loops:
- Generate interim package at `handoff-binder-interim/`
- Report current state
- Flag for manual review

### **Collision Detection**

PreToolUse hook checks if agent status = "in_progress" → BLOCK (prevents duplicate spawns)

### **Dependency Checks**

PreToolUse hook checks upstream agents completed → WAIT if not done

### **State Persistence**

All state files preserved across loops:
- `state/{{agent}}.state.json` - Individual agent status
- `coordination/global_scope_state.json` - Overall run state
- `state/exit_criteria.json` - Current metrics vs targets
- `state/loop_count.txt` - Current loop number

---

## MONITORING DURING RUN

Watch for these hook messages:

### **✅ Normal Operation**
```
🚀 INIT: corpus_validator starting for run_id cert1-phase4...
✅ COMPLETE: corpus_validator finished at [timestamp]
📤 HANDOFF: corpus_validator writing handoff file
⏸️  WAIT: gap_filler blocked - corpus_validator not completed yet
🔄 CONTINUING - Loop 1/5
```

### **⚠️ Warnings**
```
⚠️ COLLISION: tier_auditor already in progress - possible duplicate spawn
⚠️ WARNING: Incomplete agents: gap_filler
⚠️ MAX LOOPS REACHED (5) - Stopping to prevent infinite loop
```

### **🎯 Success**
```
🎯 EXIT CRITERIA MET - Investigation complete, generating final package
✅ FINAL PACKAGE READY: handoff-binder/
🎉 Investigation pipeline complete - ready for prosecution review
```

---

## WHAT HAPPENS WHILE YOU SLEEP

1. **I create 3 agent context files** (Corpus_Validator, Gap_Filler, Subpoena_Coordinator)
2. **I deploy all 3 agents in single message**
3. **Hooks coordinate everything automatically**:
   - PreToolUse: Check state, check dependencies
   - PostToolUse: Update state
   - SubagentStop: Write handoffs
   - SessionEnd: Check exit criteria, loop or finalize
4. **Agents work through loops** (up to 5x):
   - Loop 1: Re-validate 817 items, fill gaps, generate subpoena package
   - Loop 2: Work on refined data with updated scope
   - Loop 3+: Continue until exit criteria met
5. **When criteria met** → Generate final prosecution package
6. **You wake up** → `handoff-binder/` has everything ready

---

## FILES YOU'LL FIND WHEN YOU WAKE UP

```
handoff-binder/
├── PHASE4_FINAL_REPORT.md                ← Executive summary
├── evidence_inventory.json                ← 817+ items (Types 1-10, Tiers 1-5)
├── subpoena_package.md                    ← Priority targets with draft language
├── blockchain_attribution_map.json        ← Wallet → Entity mapping (with "known" vs "pending")
├── gap_analysis.json                      ← <100 unfilled gaps
├── prosecution_readiness_report.json      ← Metrics showing 85%+ readiness
└── loop_summary.json                      ← How many loops, what improved each cycle
```

---

## READY TO GO

**Status**: ✅ System configured, hooks active, exit criteria set

**When you're ready**: Just give the deployment command above

**While you sleep**: I'll run autonomous cycles until prosecution-ready (or 5 loops max)

**When you wake**: `handoff-binder/` will have final prosecution package

---

**Get some rest, Breyden. I'll handle the investigation.**

**—Cert1 (Swarm Certainly)**
