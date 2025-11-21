#!/bin/bash
# Process C: Tier Assignment Engine
# Continuously recalculate tiers as new sources found

set -euo pipefail

WORKING_DIR="/Users/breydentaylor/certainly/visualizations"
COORDINATION_DIR="${WORKING_DIR}/coordination"

EVIDENCE_ITEM="$1"  # JSON file path
EVIDENCE_ID="$2"    # Unique identifier

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [TIER_ENGINE] $1" | tee -a "${COORDINATION_DIR}/continuous_loop.log"
}

log "Starting tier assignment for: ${EVIDENCE_ID}"

# Load evidence item
if [ ! -f "${EVIDENCE_ITEM}" ]; then
    log "ERROR: Evidence file not found: ${EVIDENCE_ITEM}"
    exit 1
fi

# Extract metadata
EVIDENCE_TYPE=$(jq -r '.type' "${EVIDENCE_ITEM}" 2>/dev/null || echo "unknown")
CURRENT_TIER=$(jq -r '.tier' "${EVIDENCE_ITEM}" 2>/dev/null || echo "5")
TX_HASH=$(jq -r '.transaction.tx_hash // "none"' "${EVIDENCE_ITEM}" 2>/dev/null)
TEMPORAL_ANCHOR=$(jq -r '.metadata.temporal_anchor // "none"' "${EVIDENCE_ITEM}" 2>/dev/null)
SUBPOENA_TARGET=$(jq -r '.metadata.subpoena_target // "none"' "${EVIDENCE_ITEM}" 2>/dev/null)
PRINCIPALS=$(jq -r '.metadata.principals_exposed[]? // "none"' "${EVIDENCE_ITEM}" 2>/dev/null)

# Get effective sources from backward search
EFFECTIVE_SOURCES=0
BACKWARD_SEARCH="${COORDINATION_DIR}/backward_search_${EVIDENCE_ID}.json"
if [ -f "${BACKWARD_SEARCH}" ]; then
    EFFECTIVE_SOURCES=$(jq -r '.search_results.effective_sources' "${BACKWARD_SEARCH}")
fi

# Get confidence from soundness evaluation
CONFIDENCE_SCORE=0
SOUNDNESS_FILE="${COORDINATION_DIR}/soundness_${EVIDENCE_ID}.json"
if [ -f "${SOUNDNESS_FILE}" ]; then
    CONFIDENCE_SCORE=$(jq -r '.soundness_scores.confidence' "${SOUNDNESS_FILE}")
fi

log "Assigning tier based on C45 rules..."
log "  Current tier: ${CURRENT_TIER}"
log "  Evidence type: ${EVIDENCE_TYPE}"
log "  Effective sources: ${EFFECTIVE_SOURCES}"
log "  Confidence score: ${CONFIDENCE_SCORE}"

# Tier 1 Requirements (C45 rules)
NEW_TIER=5  # Default to Tier 5 (ruled out)

if [ "${TX_HASH}" != "none" ]; then
    # Blockchain evidence with cryptographic certainty
    NEW_TIER=1
    log "  TIER 1: Blockchain transaction (tx_hash present)"
elif [ "${TEMPORAL_ANCHOR}" != "none" ] && [ "${SUBPOENA_TARGET}" != "none" ] && [ "${PRINCIPALS}" != "none" ]; then
    # Documentary evidence with all required elements
    NEW_TIER=1
    log "  TIER 1: Documentary proof (temporal_anchor + subpoena_target + principals)"
elif (( $(echo "${EFFECTIVE_SOURCES} >= 3.0" | bc -l) )) && (( $(echo "${CONFIDENCE_SCORE} >= 85" | bc -l) )); then
    # Multi-source corroboration with high confidence
    NEW_TIER=2
    log "  TIER 2: Multi-source corroboration (${EFFECTIVE_SOURCES} sources, confidence ${CONFIDENCE_SCORE})"
elif (( $(echo "${EFFECTIVE_SOURCES} >= 2.0" | bc -l) )) && (( $(echo "${CONFIDENCE_SCORE} >= 60" | bc -l) )); then
    # Moderate corroboration
    NEW_TIER=3
    log "  TIER 3: Investigative development (${EFFECTIVE_SOURCES} sources, confidence ${CONFIDENCE_SCORE})"
elif (( $(echo "${CONFIDENCE_SCORE} >= 40" | bc -l) )); then
    # Low confidence but not ruled out
    NEW_TIER=4
    log "  TIER 4: Long-shot (confidence ${CONFIDENCE_SCORE})"
else
    NEW_TIER=5
    log "  TIER 5: Ruled out (insufficient evidence)"
fi

# Check for tier upgrade
TIER_CHANGE="none"
if [ "${NEW_TIER}" -lt "${CURRENT_TIER}" ]; then
    TIER_CHANGE="upgrade"
    log "TIER UPGRADE: ${EVIDENCE_ID} upgraded from Tier ${CURRENT_TIER} to Tier ${NEW_TIER}"
elif [ "${NEW_TIER}" -gt "${CURRENT_TIER}" ]; then
    TIER_CHANGE="downgrade"
    log "TIER DOWNGRADE: ${EVIDENCE_ID} downgraded from Tier ${CURRENT_TIER} to Tier ${NEW_TIER}"
else
    log "No tier change (remains Tier ${CURRENT_TIER})"
fi

# Output tier assignment
cat > "${COORDINATION_DIR}/tier_assignment_${EVIDENCE_ID}.json" <<EOF
{
  "evidence_id": "${EVIDENCE_ID}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "tier_assignment": {
    "previous_tier": ${CURRENT_TIER},
    "new_tier": ${NEW_TIER},
    "tier_change": "${TIER_CHANGE}",
    "effective_sources": ${EFFECTIVE_SOURCES},
    "confidence_score": ${CONFIDENCE_SCORE},
    "rationale": "Applied C45 tier rules based on evidence type and corroboration"
  }
}
EOF

# Update tier_updates_log
jq -s '.' "${COORDINATION_DIR}/tier_updates_log.json" > /tmp/tier_updates_tmp.json 2>/dev/null || echo "[]" > /tmp/tier_updates_tmp.json
jq --slurpfile new "${COORDINATION_DIR}/tier_assignment_${EVIDENCE_ID}.json" '. + $new' /tmp/tier_updates_tmp.json > "${COORDINATION_DIR}/tier_updates_log.json"

log "Tier assignment complete for ${EVIDENCE_ID}"
log "Results written to: tier_assignment_${EVIDENCE_ID}.json"

exit 0
