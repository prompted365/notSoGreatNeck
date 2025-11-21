#!/bin/bash
# Pre-agent spawn hook - check if agent already completed, check prerequisites

set -e

AGENT_NAME="$1"
RUN_ID="$2"
STATE_FILE="state/${AGENT_NAME}.state.json"
GLOBAL_STATE="coordination/global_scope_state.json"

# Check if agent already completed for this run_id
if [ -f "$STATE_FILE" ]; then
    STATUS=$(jq -r '.status // "unknown"' "$STATE_FILE")
    AGENT_RUN_ID=$(jq -r '.run_id // "unknown"' "$STATE_FILE")

    if [ "$STATUS" = "completed" ] && [ "$AGENT_RUN_ID" = "$RUN_ID" ]; then
        echo "✅ SKIP: ${AGENT_NAME} already completed for run_id ${RUN_ID}"
        exit 1  # Block tool use (agent already done)
    fi

    if [ "$STATUS" = "in_progress" ]; then
        echo "⚠️  COLLISION: ${AGENT_NAME} already in progress - possible duplicate spawn"
        exit 1  # Block to prevent collision
    fi
fi

# Check prerequisites based on agent name
case "$AGENT_NAME" in
    "tier_auditor")
        # TIER_Auditor requires: URL_Analyst, Entity_Linker, Blockchain_Forensics, Fraud_Scorer, Binder_Chunker
        DEPS=("url_analyst" "entity_linker" "blockchain_forensics" "fraud_scorer" "binder_chunker")
        ;;
    "reasoningbank_manager")
        # ReasoningBank_Manager requires: TIER_Auditor
        DEPS=("tier_auditor")
        ;;
    "dashboard_coordinator")
        # Dashboard_Coordinator requires: ReasoningBank_Manager
        DEPS=("reasoningbank_manager")
        ;;
    "gap_filler")
        # Gap_Filler requires: Corpus_Validator
        DEPS=("corpus_validator")
        ;;
    "subpoena_coordinator")
        # Subpoena_Coordinator requires: Gap_Filler
        DEPS=("gap_filler")
        ;;
    *)
        # No dependencies for first-wave agents
        DEPS=()
        ;;
esac

# Check each dependency
for dep in "${DEPS[@]}"; do
    DEP_STATE="state/${dep}.state.json"
    if [ ! -f "$DEP_STATE" ]; then
        echo "⏸️  WAIT: ${AGENT_NAME} blocked - ${dep} not started yet"
        exit 1
    fi

    DEP_STATUS=$(jq -r '.status // "unknown"' "$DEP_STATE")
    if [ "$DEP_STATUS" != "completed" ]; then
        echo "⏸️  WAIT: ${AGENT_NAME} blocked - ${dep} status: ${DEP_STATUS}"
        exit 1
    fi
done

# Initialize state file
echo "🚀 INIT: ${AGENT_NAME} starting for run_id ${RUN_ID}"
jq -n \
    --arg run_id "$RUN_ID" \
    --arg agent "$AGENT_NAME" \
    --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{
        run_id: $run_id,
        agent: $agent,
        status: "initializing",
        started_at: $timestamp
    }' > "$STATE_FILE"

# Update global scope
if [ -f "$GLOBAL_STATE" ]; then
    jq --arg agent "$AGENT_NAME" \
       --arg status "initializing" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.agents[$agent] = {status: $status, started_at: $timestamp}' \
       "$GLOBAL_STATE" > "${GLOBAL_STATE}.tmp"
    mv "${GLOBAL_STATE}.tmp" "$GLOBAL_STATE"
fi

echo "✅ ALLOW: ${AGENT_NAME} cleared to execute"
exit 0  # Allow tool use
