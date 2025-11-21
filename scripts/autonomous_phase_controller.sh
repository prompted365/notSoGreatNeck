#!/bin/bash
# Autonomous Phase Controller - Multi-phase loop system with self-seeding
# Monitors state, triggers next phase when ready, seeds continuation messages

set -e

PHASE_STATE_FILE="state/autonomous_phases.json"
GLOBAL_STATE="coordination/global_scope_state.json"
MAX_PHASES=4
CONTINUATION_DELAY=300  # 5 minutes between phase checks

# Initialize phase state if doesn't exist
if [ ! -f "$PHASE_STATE_FILE" ]; then
    cat > "$PHASE_STATE_FILE" <<EOF
{
  "current_phase": 1,
  "max_phases": $MAX_PHASES,
  "phases_completed": [],
  "continuation_enabled": true,
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
fi

# Read current phase
CURRENT_PHASE=$(jq -r '.current_phase' "$PHASE_STATE_FILE")
PHASES_COMPLETED=$(jq -r '.phases_completed | length' "$PHASE_STATE_FILE")

echo "🔄 AUTONOMOUS PHASE CONTROLLER"
echo "   Current Phase: $CURRENT_PHASE/$MAX_PHASES"
echo "   Phases Completed: $PHASES_COMPLETED"

# Check if all phases complete
if [ "$PHASES_COMPLETED" -ge "$MAX_PHASES" ]; then
    echo "🎉 ALL PHASES COMPLETE - Investigation finished"
    jq '.continuation_enabled = false | .status = "completed"' "$PHASE_STATE_FILE" > "${PHASE_STATE_FILE}.tmp"
    mv "${PHASE_STATE_FILE}.tmp" "$PHASE_STATE_FILE"
    exit 0
fi

# Check if current phase is complete
check_phase_complete() {
    local phase=$1

    # Phase completion logic based on global state
    case $phase in
        1)
            # Phase 1: Initial evidence gathering and validation
            # Complete when: corpus_validator, gap_filler, subpoena_coordinator done
            COMPLETED=$(jq -r '.agent_status.Corpus_Validator.status == "completed" and
                              .agent_status.Gap_Filler.status == "completed" and
                              .agent_status.Subpoena_Coordinator.status == "completed"' "$GLOBAL_STATE")
            ;;
        2)
            # Phase 2: Deep analysis and forensics
            # Complete when: blockchain_forensics, entity_linker, tier_auditor done
            COMPLETED=$(jq -r '.agent_status.Blockchain_Forensics.status == "completed" and
                              .agent_status.Entity_Linker.status == "completed" and
                              .agent_status.TIER_Auditor.status == "completed"' "$GLOBAL_STATE")
            ;;
        3)
            # Phase 3: Evidence synthesis and pattern detection
            # Complete when: evidence_synthesizer, pattern_detective done
            COMPLETED=$(jq -r '.agent_status.Evidence_Synthesizer.status == "completed" and
                              .agent_status.Pattern_Detective.status == "completed"' "$GLOBAL_STATE" 2>/dev/null || echo "false")
            ;;
        4)
            # Phase 4: Final packaging and quality assurance
            # Complete when: final_packager done
            COMPLETED=$(jq -r '.agent_status.Final_Packager.status == "completed"' "$GLOBAL_STATE")
            ;;
        *)
            COMPLETED="false"
            ;;
    esac

    echo "$COMPLETED"
}

PHASE_COMPLETE=$(check_phase_complete $CURRENT_PHASE)

if [ "$PHASE_COMPLETE" = "true" ]; then
    echo "✅ Phase $CURRENT_PHASE complete - Advancing to next phase"

    # Update phase state
    NEXT_PHASE=$((CURRENT_PHASE + 1))
    jq --argjson next "$NEXT_PHASE" \
       --argjson completed "$CURRENT_PHASE" \
       '.current_phase = $next |
        .phases_completed += [$completed] |
        .last_advance = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' \
       "$PHASE_STATE_FILE" > "${PHASE_STATE_FILE}.tmp"
    mv "${PHASE_STATE_FILE}.tmp" "$PHASE_STATE_FILE"

    # Trigger continuation message
    echo "📨 TRIGGERING CONTINUATION: Phase $NEXT_PHASE deployment"
    echo "CONTINUE_PHASE_$NEXT_PHASE" > /tmp/claude_continuation_trigger.txt

    # Self-seed next check
    echo "⏰ Scheduling next check in $CONTINUATION_DELAY seconds"
    (sleep $CONTINUATION_DELAY && bash "$0") &

else
    echo "⏳ Phase $CURRENT_PHASE in progress - checking again in $CONTINUATION_DELAY seconds"

    # Self-seed next check
    (sleep $CONTINUATION_DELAY && bash "$0") &
fi

exit 0
