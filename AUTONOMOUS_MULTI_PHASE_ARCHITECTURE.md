# Autonomous Multi-Phase Investigation Architecture

**System**: 4-phase autonomous loop with self-seeding continuation
**Deployment**: Single-turn with 8 agents × 3-5 tasks each = 32 total tasks
**Coordination**: Hook-based gating with background phase controller

---

## ARCHITECTURE OVERVIEW

```
SINGLE TURN DEPLOYMENT
  ↓
  ├─ Background Task: Phase Controller (self-seeding)
  │    ↓ monitors state every 5 minutes
  │    ↓ triggers CONTINUE message when phase complete
  │    ↓ seeds next background check
  │
  └─ 8 Agent Deployments (parallel where possible)
       ↓
       Phase 1: Evidence Foundation (3 agents, 12 tasks)
       ↓
       Phase 2: Deep Analysis (3 agents, 12 tasks)
       ↓
       Phase 3: Pattern Detection (2 agents, 6 tasks)
       ↓
       Phase 4: Final Packaging (2 agents, 8 tasks)
       ↓
       ALL DONE (38 total tasks across 4 phases)
```

---

## PHASE DEFINITIONS

### **PHASE 1: Evidence Foundation** (Parallel Execution)
**Agents**: 3 (no dependencies, run concurrently)
**Duration**: ~2-3 hours
**Goal**: Establish evidence base, validate corpus, identify gaps

**Stage 1A: Corpus_Validator** [4 tasks]
1. Load and validate all Phase 3 evidence (817 items)
2. Re-classify using Types 1-10 and Tiers 1-5
3. Separate blockchain attribution from transaction certainty
4. Output: phase3_revalidated_evidence.json

**Stage 1B: Gap_Filler** [4 tasks] (blocked until Corpus_Validator done)
1. Process flagged items from manual review queue
2. Cross-reference corpus (Telegram, blockchain, shadowLens)
3. Recalculate effective sources with notebook discount
4. Output: gap_fill_results.json

**Stage 1C: Subpoena_Coordinator** [4 tasks] (blocked until Gap_Filler done)
1. Identify all Tier 2 items needing subpoenas
2. Group by target (exchanges, courts, banks)
3. Prioritize by yield and timeline (P1/P2/P3)
4. Output: subpoena_package.md

**Continuation Trigger**: When all 3 agents write state files with status="completed"

---

### **PHASE 2: Deep Analysis** (Parallel Execution)
**Agents**: 3 (no cross-dependencies, run concurrently)
**Duration**: ~3-4 hours
**Goal**: Deep forensics, entity mapping, quality audit

**Stage 2A: Blockchain_Forensics** [5 tasks]
1. Wallet clustering analysis (group related wallets)
2. Exchange fingerprinting (identify likely exchanges)
3. Attribution strength scoring (0-100 confidence)
4. Transaction network mapping (build graph)
5. RICO value assessment (enterprise benefit calculation)

**Stage 2B: Entity_Linker** [5 tasks]
1. Entity relationship mapping (individuals + corporations)
2. Corporate structure analysis (trusts, LLCs, offshore)
3. Payment flow analysis (customer → wallets → banks)
4. URL fraud pattern legal review (FTC/FDA violations)
5. RICO enterprise diagram (visual representation)

**Stage 2C: TIER_Auditor** [5 tasks]
1. Manual review of borderline items (2.8-3.2 sources)
2. Evidence quality spot checks (50 item sample)
3. Gap analysis (what evidence types are missing?)
4. Blind spot detection (what are we not looking at?)
5. Source verification sampling (validate file integrity)

**Continuation Trigger**: When all 3 agents write state files with status="completed"

---

### **PHASE 3: Pattern Detection** (Sequential Execution)
**Agents**: 2 (Pattern_Detective depends on Evidence_Synthesizer)
**Duration**: ~4-5 hours
**Goal**: Build comprehensive timeline, identify patterns, cross-reference everything

**Stage 3A: Evidence_Synthesizer** [5 tasks]
1. Comprehensive cross-reference matrix (item × corpus)
2. Evidence strength heatmap (identify strongest clusters)
3. Timeline construction 1993-2025 (30-year chronology)
4. Temporal anchor validation (verify date consistency)
5. Master evidence map (big picture visualization)

**Stage 3B: Pattern_Detective** [4 tasks] (blocked until Synthesizer done)
1. Fraud pattern identification (medical claims, pricing, endorsements)
2. Money laundering pattern detection (splitting, layering, aggregation)
3. Asset concealment pattern analysis (trusts, offshore, round-tripping)
4. Victim impact analysis (estimate damages, identify victim classes)

**Continuation Trigger**: When both agents write state files with status="completed"

---

### **PHASE 4: Final Packaging** (Sequential Execution)
**Agents**: 2 (QA_Validator depends on Final_Packager)
**Duration**: ~2-3 hours
**Goal**: Generate prosecution package, validate all outputs, finalize handoff

**Stage 4A: Final_Packager** [7 tasks]
1. Generate final evidence inventory (822+ items sorted by tier)
2. Subpoena package finalization (incorporate forensics)
3. Prosecution readiness report (metrics vs targets)
4. Executive summary (comprehensive prosecution guide)
5. RICO timeline visualization (1993-2025 key events)
6. Loop summary report (document 4-phase journey)
7. Global state update (mark investigation complete)

**Stage 4B: QA_Validator** [4 tasks] (blocked until Packager done)
1. File existence validation (all outputs present)
2. JSON structure validation (all files parse correctly)
3. Cross-reference validation (no broken links)
4. Completeness validation (all required fields present)

**Completion**: System writes completion flag, stops continuation loop

---

## HOOK COORDINATION LOGIC

### **PreToolUse Hook** (scripts/hooks/pre_agent_spawn.sh)
```bash
# Check if agent already completed (prevent duplicate work)
if [ status = "completed" ] && [ run_id matches ]; then
    echo "SKIP: Already done"
    exit 1  # Block tool use
fi

# Check phase dependencies
case "$AGENT_NAME" in
    "Gap_Filler")
        wait_for "Corpus_Validator"
        ;;
    "Subpoena_Coordinator")
        wait_for "Gap_Filler"
        ;;
    "Pattern_Detective")
        wait_for "Evidence_Synthesizer"
        ;;
    "QA_Validator")
        wait_for "Final_Packager"
        ;;
esac

# If dependency not met, block and retry in 30 seconds
```

### **PostToolUse Hook** (scripts/hooks/post_agent_complete.sh)
```bash
# Update agent state to "completed"
jq '.status = "completed"' state/${agent}.state.json

# Update global scope state
jq '.agent_status.${AGENT} = {"status": "completed"}' coordination/global_scope_state.json

# Trigger phase controller check (maybe phase is now complete)
bash scripts/autonomous_phase_controller.sh &
```

### **SessionEnd Hook** (scripts/hooks/session_complete.sh)
```bash
# Check for continuation trigger
if [ -f /tmp/claude_continuation_trigger.txt ]; then
    NEXT_PHASE=$(cat /tmp/claude_continuation_trigger.txt)
    echo "📨 CONTINUATION TRIGGERED: $NEXT_PHASE"
    rm /tmp/claude_continuation_trigger.txt

    # System will see this message and continue
    echo "SYSTEM: Continue to $NEXT_PHASE"
    exit 1  # Signal continuation needed
fi

# Otherwise, check if all phases complete
PHASES_COMPLETE=$(jq -r '.phases_completed | length' state/autonomous_phases.json)
if [ "$PHASES_COMPLETE" -ge 4 ]; then
    echo "🎉 ALL PHASES COMPLETE"
    exit 0  # Stop
else
    echo "⏳ Phase in progress, waiting for completion"
    exit 1  # Keep waiting
fi
```

---

## SINGLE-TURN DEPLOYMENT COMMAND

```javascript
// This is the ONLY message you send - everything else is autonomous

[Background Task - Start Phase Controller]
Bash("bash scripts/autonomous_phase_controller.sh &", run_in_background: true)

[8 Agent Deployments - Single Message]

// PHASE 1 (Parallel)
Task("Corpus_Validator", "4 tasks: Load evidence, re-classify, separate attribution, output", "general-purpose")
Task("Gap_Filler", "4 tasks: Process flagged, cross-ref corpus, recalc sources, output", "general-purpose")
Task("Subpoena_Coordinator", "4 tasks: Identify Tier 2, group targets, prioritize, output", "general-purpose")

// PHASE 2 (Parallel after Phase 1)
Task("Blockchain_Forensics", "5 tasks: Clustering, fingerprinting, scoring, network, RICO", "general-purpose")
Task("Entity_Linker", "5 tasks: Entity map, corp structure, payment flows, URL review, RICO diagram", "general-purpose")
Task("TIER_Auditor", "5 tasks: Manual review, spot checks, gap analysis, blind spots, verification", "general-purpose")

// PHASE 3 (Sequential after Phase 2)
Task("Evidence_Synthesizer", "5 tasks: Cross-ref matrix, heatmap, timeline, temporal validation, master map", "general-purpose")
Task("Pattern_Detective", "4 tasks: Fraud patterns, laundering patterns, asset concealment, victim impact", "general-purpose")

// PHASE 4 (Sequential after Phase 3)
// Note: Final_Packager and QA_Validator will be triggered by continuation system
// OR you can include them here and hooks will gate them appropriately

Task("Final_Packager", "7 tasks: Inventory, subpoena final, readiness, exec summary, timeline viz, loop summary, state update", "general-purpose")
Task("QA_Validator", "4 tasks: File existence, JSON validation, cross-ref validation, completeness", "general-purpose")
```

**Result**:
- Phase controller runs in background, checks every 5 minutes
- 8 agents execute 38 tasks across 4 phases
- Hooks gate dependencies automatically
- Controller triggers continuation when phases complete
- System self-seeds next phase deployment
- Runs until all 4 phases complete (~12-15 hours total)

---

## BACKGROUND TASK SELF-SEEDING

```bash
# Phase controller checks state every 5 minutes
while true; do
    PHASE_COMPLETE=$(check_phase_complete $CURRENT_PHASE)

    if [ "$PHASE_COMPLETE" = "true" ]; then
        # Write continuation trigger
        echo "CONTINUE_PHASE_$NEXT_PHASE" > /tmp/claude_continuation_trigger.txt

        # SessionEnd hook detects this and signals system to continue
        break
    else
        # Not done yet, check again in 5 minutes
        sleep 300
    fi
done

# Self-seed next check
bash scripts/autonomous_phase_controller.sh &
```

---

## CONTINUATION MESSAGE FORMAT

When phase controller triggers continuation, SessionEnd hook outputs:

```
📨 CONTINUATION TRIGGERED: CONTINUE_PHASE_2

SYSTEM: Phase 1 complete. Continue to Phase 2.

Agents ready:
- Blockchain_Forensics (5 tasks)
- Entity_Linker (5 tasks)
- TIER_Auditor (5 tasks)

Prerequisites met:
✅ Corpus_Validator completed
✅ Gap_Filler completed
✅ Subpoena_Coordinator completed

Proceeding with Phase 2 deployment...
```

System sees "CONTINUE_PHASE_2" and automatically spawns next phase agents.

---

## ADVANTAGES OF THIS ARCHITECTURE

1. **Single-Turn Deployment**: Deploy all 4 phases in one message
2. **Automatic Gating**: Hooks prevent premature execution
3. **Self-Seeding Continuation**: Background task triggers next phase
4. **Parallel Execution**: Non-dependent agents run concurrently
5. **Zero Manual Intervention**: Runs autonomously for 12-15 hours
6. **Fault Tolerance**: If agent fails, hooks prevent cascade
7. **State Persistence**: All state tracked in JSON files
8. **Resume Capability**: Can restart from any phase

---

## PHASE COMPLETION METRICS

Each phase has exit criteria:

**Phase 1 Exit**:
- ✅ 817 items revalidated
- ✅ Unfilled gaps < 40
- ✅ Subpoena package generated

**Phase 2 Exit**:
- ✅ 774 blockchain items scored
- ✅ Entity map complete (6+ entities)
- ✅ TIER audit complete

**Phase 3 Exit**:
- ✅ 30-year timeline constructed
- ✅ Cross-reference matrix built
- ✅ Fraud patterns documented

**Phase 4 Exit**:
- ✅ 7 handoff deliverables created
- ✅ QA validation 100% pass
- ✅ Investigation complete

---

## FILES CREATED

1. `scripts/autonomous_phase_controller.sh` - Background phase monitor
2. `state/autonomous_phases.json` - Phase tracking state
3. `coordination/global_scope_state.json` - Agent completion tracking
4. `state/*.state.json` - Individual agent states (8 files)
5. `coordination/*_handoff.json` - Agent outputs
6. `handoff-binder/*` - Final deliverables (7 files)

---

## MONITORING DURING RUN

Watch for these messages:

```
⏳ Phase 1 in progress - checking again in 300 seconds
✅ Phase 1 complete - Advancing to next phase
📨 TRIGGERING CONTINUATION: Phase 2 deployment
⏰ Scheduling next check in 300 seconds

🔄 AUTONOMOUS PHASE CONTROLLER
   Current Phase: 2/4
   Phases Completed: 1

⏳ Phase 2 in progress - checking again in 300 seconds
✅ Phase 2 complete - Advancing to next phase
📨 TRIGGERING CONTINUATION: Phase 3 deployment

[... continues through Phase 4 ...]

🎉 ALL PHASES COMPLETE - Investigation finished
```

---

**Ready to deploy**: Single-turn command deploys all 4 phases with autonomous continuation until complete.
