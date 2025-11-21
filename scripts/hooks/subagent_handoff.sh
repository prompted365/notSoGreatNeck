#!/bin/bash
# Subagent handoff hook - write handoff file, update evidence manifest

set -e

AGENT_NAME="$1"
RUN_ID="$2"
HANDOFF_FILE="coordination/${AGENT_NAME}_handoff.json"
EVIDENCE_MANIFEST="memory/evidence_manifest.json"

# Write handoff file
echo "📤 HANDOFF: ${AGENT_NAME} writing handoff file"
jq -n \
    --arg agent "$AGENT_NAME" \
    --arg run_id "$RUN_ID" \
    --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{
        agent: $agent,
        run_id: $run_id,
        status: "completed",
        timestamp: $timestamp
    }' > "$HANDOFF_FILE"

# Update evidence manifest if approved_evidence_list exists
if [ -f "coordination/approved_evidence_list.json" ]; then
    COUNT=$(jq 'length' coordination/approved_evidence_list.json)

    if [ -f "$EVIDENCE_MANIFEST" ]; then
        jq --arg agent "$AGENT_NAME" \
           --argjson count "$COUNT" \
           '.agents[$agent].evidence_count = $count' \
           "$EVIDENCE_MANIFEST" > "${EVIDENCE_MANIFEST}.tmp"
        mv "${EVIDENCE_MANIFEST}.tmp" "$EVIDENCE_MANIFEST"
    fi

    echo "📊 METRICS: ${AGENT_NAME} processed ${COUNT} evidence items"
fi

echo "✅ HANDOFF COMPLETE: ${AGENT_NAME} ready for downstream agents"
