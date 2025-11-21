#!/bin/bash
# Process B: Soundness Evaluator
# Evaluates every new item: verifiable? corroborated? admissible?

set -euo pipefail

WORKING_DIR="/Users/breydentaylor/certainly/visualizations"
COORDINATION_DIR="${WORKING_DIR}/coordination"

EVIDENCE_ITEM="$1"  # JSON file path
EVIDENCE_ID="$2"    # Unique identifier

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [SOUNDNESS_EVAL] $1" | tee -a "${COORDINATION_DIR}/continuous_loop.log"
}

log "Starting soundness evaluation for: ${EVIDENCE_ID}"

# Load evidence item
if [ ! -f "${EVIDENCE_ITEM}" ]; then
    log "ERROR: Evidence file not found: ${EVIDENCE_ITEM}"
    exit 1
fi

# Extract metadata
EVIDENCE_TYPE=$(jq -r '.type' "${EVIDENCE_ITEM}" 2>/dev/null || echo "unknown")
TEMPORAL_ANCHOR=$(jq -r '.metadata.temporal_anchor // "none"' "${EVIDENCE_ITEM}" 2>/dev/null)
TX_HASH=$(jq -r '.transaction.tx_hash // "none"' "${EVIDENCE_ITEM}" 2>/dev/null)
SUBPOENA_TARGET=$(jq -r '.metadata.subpoena_target // "none"' "${EVIDENCE_ITEM}" 2>/dev/null)
PRINCIPALS=$(jq -r '.metadata.principals_exposed[]? // "none"' "${EVIDENCE_ITEM}" 2>/dev/null)

# Initialize scores
VERIFIABLE_SCORE=0
CORROBORATION_SCORE=0
ADMISSIBILITY_SCORE=0

# Verifiability check
log "Checking verifiability..."
if [ "${TX_HASH}" != "none" ]; then
    VERIFIABLE_SCORE=100
    log "  Blockchain transaction (cryptographically verifiable): 100/100"
elif [ "${TEMPORAL_ANCHOR}" != "none" ] && [ "${SUBPOENA_TARGET}" != "none" ]; then
    VERIFIABLE_SCORE=80
    log "  Documentary evidence (pending subpoena): 80/100"
elif [ "${EVIDENCE_TYPE}" == "10" ]; then
    VERIFIABLE_SCORE=50
    log "  AI/LLM analysis (requires source verification): 50/100"
else
    VERIFIABLE_SCORE=30
    log "  Needs additional verification: 30/100"
fi

# Corroboration check
log "Checking corroboration..."
BACKWARD_SEARCH="${COORDINATION_DIR}/backward_search_${EVIDENCE_ID}.json"
if [ -f "${BACKWARD_SEARCH}" ]; then
    EFFECTIVE_SOURCES=$(jq -r '.search_results.effective_sources' "${BACKWARD_SEARCH}")
    if (( $(echo "${EFFECTIVE_SOURCES} >= 3.0" | bc -l) )); then
        CORROBORATION_SCORE=100
        log "  Multi-source corroboration (${EFFECTIVE_SOURCES} sources): 100/100"
    elif (( $(echo "${EFFECTIVE_SOURCES} >= 2.0" | bc -l) )); then
        CORROBORATION_SCORE=70
        log "  Moderate corroboration (${EFFECTIVE_SOURCES} sources): 70/100"
    else
        CORROBORATION_SCORE=40
        log "  Limited corroboration (${EFFECTIVE_SOURCES} sources): 40/100"
    fi
else
    CORROBORATION_SCORE=20
    log "  No backward search completed yet: 20/100"
fi

# Admissibility check
log "Checking admissibility..."
if [ "${TX_HASH}" != "none" ]; then
    ADMISSIBILITY_SCORE=100
    log "  Blockchain evidence (FRE 901 - self-authenticating): 100/100"
elif [ "${TEMPORAL_ANCHOR}" != "none" ] && [ "${SUBPOENA_TARGET}" != "none" ] && [ "${PRINCIPALS}" != "none" ]; then
    ADMISSIBILITY_SCORE=90
    log "  Documentary with temporal anchor + principals: 90/100"
elif [ "${EVIDENCE_TYPE}" == "10" ]; then
    ADMISSIBILITY_SCORE=60
    log "  AI analysis (requires expert testimony): 60/100"
else
    ADMISSIBILITY_SCORE=50
    log "  Needs authentication work: 50/100"
fi

# Calculate overall confidence score
CONFIDENCE_SCORE=$(echo "scale=2; (${VERIFIABLE_SCORE} + ${CORROBORATION_SCORE} + ${ADMISSIBILITY_SCORE}) / 3" | bc)

log "Soundness evaluation complete for ${EVIDENCE_ID}"
log "  Verifiable: ${VERIFIABLE_SCORE}/100"
log "  Corroborated: ${CORROBORATION_SCORE}/100"
log "  Admissible: ${ADMISSIBILITY_SCORE}/100"
log "  Overall Confidence: ${CONFIDENCE_SCORE}/100"

# Output results
cat > "${COORDINATION_DIR}/soundness_${EVIDENCE_ID}.json" <<EOF
{
  "evidence_id": "${EVIDENCE_ID}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "soundness_scores": {
    "verifiable": ${VERIFIABLE_SCORE},
    "corroborated": ${CORROBORATION_SCORE},
    "admissible": ${ADMISSIBILITY_SCORE},
    "confidence": ${CONFIDENCE_SCORE}
  },
  "next_action": "tier_assignment"
}
EOF

# Flag items needing additional validation
if (( $(echo "${CONFIDENCE_SCORE} < 60" | bc -l) )); then
    log "FLAGGED: ${EVIDENCE_ID} needs additional validation (confidence < 60)"
    echo "${EVIDENCE_ID}" >> "${COORDINATION_DIR}/validation_queue.txt"
elif (( $(echo "${CONFIDENCE_SCORE} >= 85" | bc -l) )); then
    log "AUTO-PROMOTE: ${EVIDENCE_ID} passes threshold (confidence >= 85)"
    echo "${EVIDENCE_ID}" >> "${COORDINATION_DIR}/auto_promote_queue.txt"
fi

log "Results written to: soundness_${EVIDENCE_ID}.json"
exit 0
