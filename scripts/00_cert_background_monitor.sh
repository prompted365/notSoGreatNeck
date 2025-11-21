#!/bin/bash
# CERT Background Monitor - 7-minute interval autonomous tracking
# Monitors all CERT agents, triggers continuation, self-seeds

set -e

CERT_STATE="state/cert_analytics_state.json"
GLOBAL_STATE="coordination/global_scope_state.json"
MAX_CYCLES=10
CHECK_INTERVAL=420  # 7 minutes

# Initialize CERT state
if [ ! -f "$CERT_STATE" ]; then
    cat > "$CERT_STATE" <<EOF
{
  "mission": "cert_advanced_analytics",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "current_cycle": 1,
  "max_cycles": $MAX_CYCLES,
  "cycles_completed": [],
  "continuation_enabled": true,
  "agents": {
    "File_Chunker": {"status": "pending", "chunks_identified": 0},
    "HTML_Analyzer": {"status": "pending", "files_analyzed": 0},
    "Word_Cloud_Generator": {"status": "pending", "visualizations_created": 0},
    "Qdrant_Manager": {"status": "pending", "vectors_stored": 0},
    "Semantic_Clusterer": {"status": "pending", "clusters_found": 0},
    "Network_Grapher": {"status": "pending", "nodes_enriched": 0},
    "Citation_Linker": {"status": "pending", "citations_added": 0},
    "Evidence_Integrator": {"status": "pending", "items_integrated": 0}
  }
}
EOF
fi

# Read current cycle
CURRENT_CYCLE=$(jq -r '.current_cycle' "$CERT_STATE")
CYCLES_COMPLETED=$(jq -r '.cycles_completed | length' "$CERT_STATE")

echo "🔬 CERT BACKGROUND MONITOR"
echo "   Cycle: $CURRENT_CYCLE/$MAX_CYCLES"
echo "   Completed: $CYCLES_COMPLETED"

# Check if all cycles complete
if [ "$CYCLES_COMPLETED" -ge "$MAX_CYCLES" ]; then
    echo "🎉 ALL CERT CYCLES COMPLETE"
    jq '.continuation_enabled = false | .status = "completed"' "$CERT_STATE" > "${CERT_STATE}.tmp"
    mv "${CERT_STATE}.tmp" "$CERT_STATE"
    exit 0
fi

# Check if current cycle is complete
check_cycle_complete() {
    local cycle=$1

    # Cycle complete when all 8 agents report "completed"
    COMPLETED_COUNT=$(jq -r '[.agents[] | select(.status == "completed")] | length' "$CERT_STATE")

    if [ "$COMPLETED_COUNT" -ge 8 ]; then
        echo "true"
    else
        echo "false"
    fi
}

CYCLE_COMPLETE=$(check_cycle_complete $CURRENT_CYCLE)

if [ "$CYCLE_COMPLETE" = "true" ]; then
    echo "✅ Cycle $CURRENT_CYCLE complete - Advancing"

    NEXT_CYCLE=$((CURRENT_CYCLE + 1))
    jq --argjson next "$NEXT_CYCLE" \
       --argjson completed "$CURRENT_CYCLE" \
       '.current_cycle = $next |
        .cycles_completed += [$completed] |
        .last_advance = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' \
       "$CERT_STATE" > "${CERT_STATE}.tmp"
    mv "${CERT_STATE}.tmp" "$CERT_STATE"

    echo "📨 TRIGGERING CONTINUATION: Cycle $NEXT_CYCLE"
    echo "CONTINUE_CERT_CYCLE_$NEXT_CYCLE" > /tmp/cert_continuation_trigger.txt

    # Self-seed next check
    echo "⏰ Scheduling next check in $CHECK_INTERVAL seconds"
    (sleep $CHECK_INTERVAL && bash "$0") &
else
    echo "⏳ Cycle $CURRENT_CYCLE in progress - checking again in $CHECK_INTERVAL seconds"
    echo "   Completed agents: $COMPLETED_COUNT / 8"

    # Self-seed next check
    (sleep $CHECK_INTERVAL && bash "$0") &
fi

exit 0
