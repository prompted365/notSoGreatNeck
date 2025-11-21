#!/bin/bash
# Post-agent complete hook - update state to completed

set -e

AGENT_NAME="$1"
RUN_ID="$2"
STATE_FILE="state/${AGENT_NAME}.state.json"
GLOBAL_STATE="coordination/global_scope_state.json"

if [ ! -f "$STATE_FILE" ]; then
    echo "⚠️  WARNING: No state file for ${AGENT_NAME} - creating one"
    jq -n \
        --arg run_id "$RUN_ID" \
        --arg agent "$AGENT_NAME" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{
            run_id: $run_id,
            agent: $agent,
            status: "completed",
            completed_at: $timestamp
        }' > "$STATE_FILE"
else
    # Update existing state to completed
    jq --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.status = "completed" | .completed_at = $timestamp' \
       "$STATE_FILE" > "${STATE_FILE}.tmp"
    mv "${STATE_FILE}.tmp" "$STATE_FILE"
fi

# Update global scope
if [ -f "$GLOBAL_STATE" ]; then
    jq --arg agent "$AGENT_NAME" \
       --arg status "completed" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.agents[$agent].status = $status | .agents[$agent].completed_at = $timestamp' \
       "$GLOBAL_STATE" > "${GLOBAL_STATE}.tmp"
    mv "${GLOBAL_STATE}.tmp" "$GLOBAL_STATE"
fi

echo "✅ COMPLETE: ${AGENT_NAME} finished at $(date)"
