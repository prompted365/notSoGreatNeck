#!/bin/bash
# Session complete hook - check exit criteria, either loop or finalize

set -e

RUN_ID="$1"
GLOBAL_STATE="coordination/global_scope_state.json"
LOOP_COUNT_FILE="state/loop_count.txt"
MAX_LOOPS=5  # Safety: prevent infinite loops

# Increment loop counter
if [ -f "$LOOP_COUNT_FILE" ]; then
    LOOP_COUNT=$(cat "$LOOP_COUNT_FILE")
else
    LOOP_COUNT=0
fi
LOOP_COUNT=$((LOOP_COUNT + 1))
echo "$LOOP_COUNT" > "$LOOP_COUNT_FILE"

echo "🔁 SESSION COMPLETE - Loop ${LOOP_COUNT}/${MAX_LOOPS}"

# Check if all agents completed
if [ -f "$GLOBAL_STATE" ]; then
    INCOMPLETE=$(jq -r '.agents | to_entries | map(select(.value.status != "completed")) | .[].key' "$GLOBAL_STATE" 2>/dev/null || echo "")

    if [ -n "$INCOMPLETE" ]; then
        echo "⚠️  WARNING: Incomplete agents: $INCOMPLETE"
        echo "Cannot proceed to exit criteria check"
        exit 1
    fi
fi

# Check exit criteria (but always run all 5 loops regardless)
echo "Checking exit criteria..."
MILESTONE_FILE="state/milestone_85_reached.txt"

if bash scripts/hooks/check_exit_criteria.sh; then
    # Exit criteria MET - but keep going until loop 5
    if [ ! -f "$MILESTONE_FILE" ]; then
        echo "🎯 85% MILESTONE REACHED at Loop ${LOOP_COUNT}/5"
        echo "Flagging milestone and continuing to loop 5 for deeper investigation"
        echo "Loop ${LOOP_COUNT}" > "$MILESTONE_FILE"
    fi

    if [ "$LOOP_COUNT" -lt "$MAX_LOOPS" ]; then
        # Continue despite meeting criteria - use remaining loops for deeper analysis
        echo "✅ Criteria met, but continuing to loop ${MAX_LOOPS} for comprehensive investigation"
        echo "🔍 Next focus: Find gaps and blind spots in current evidence"
    fi
fi

# Always continue until loop 5
if [ "$LOOP_COUNT" -ge "$MAX_LOOPS" ]; then
    echo "🎉 LOOP 5 COMPLETE - Full investigation cycle finished"
    echo "📊 Total loops: ${LOOP_COUNT}"

    # Run final package generation
    if [ -f "scripts/generate_final_prosecution_package.py" ]; then
        python scripts/generate_final_prosecution_package.py \
            --run-id "$RUN_ID" \
            --output "handoff-binder/" \
            --loop-count "$LOOP_COUNT"
    fi

    echo "✅ FINAL PACKAGE READY: handoff-binder/"

    # Check if milestone was reached
    if [ -f "$MILESTONE_FILE" ]; then
        MILESTONE_LOOP=$(cat "$MILESTONE_FILE")
        echo "📍 Milestone: 85% readiness reached at ${MILESTONE_LOOP}"
        echo "📈 Loops ${LOOP_COUNT} through 5: Continued investigation for comprehensive coverage"
    fi

    echo "🎉 Investigation pipeline complete - ready for prosecution review"

    # Reset for next investigation
    rm -f "$LOOP_COUNT_FILE"
    rm -f "$MILESTONE_FILE"

    exit 0  # STOP after 5 loops
else
    echo "🔄 CONTINUING - Loop ${LOOP_COUNT}/${MAX_LOOPS}"

    # Prepare for next loop
    if [ -f "$GLOBAL_STATE" ]; then
        jq '.status = "looping" | .loop_count = '"$LOOP_COUNT" \
           "$GLOBAL_STATE" > "${GLOBAL_STATE}.tmp"
        mv "${GLOBAL_STATE}.tmp" "$GLOBAL_STATE"
    fi

    # Determine next loop focus based on progress
    if [ -f "$MILESTONE_FILE" ]; then
        echo "🔍 Post-milestone mode: Systematic gap analysis and blind spot detection"
    else
        echo "🔁 Ready for next cycle - Cert1 will re-deploy agents"
    fi

    exit 1  # CONTINUE LOOPING
fi
