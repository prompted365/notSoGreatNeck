#!/bin/bash
# Process A: Backward Citation Searcher
# Searches all corpus files for citations of newly discovered evidence

set -euo pipefail

WORKING_DIR="/Users/breydentaylor/certainly/visualizations"
COORDINATION_DIR="${WORKING_DIR}/coordination"
CORPUS_BASE="/Users/breydentaylor/certainly/shurka-dump"

# Input: New evidence item from any discovery cycle
EVIDENCE_ITEM="$1"  # JSON string or file path
EVIDENCE_ID="$2"    # Unique identifier

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [BACKWARD_SEARCH] $1" | tee -a "${COORDINATION_DIR}/continuous_loop.log"
}

log "Starting backward citation search for: ${EVIDENCE_ID}"

# Extract key search terms from evidence
SEARCH_TERMS=$(echo "${EVIDENCE_ITEM}" | jq -r '.search_terms[]' 2>/dev/null || echo "")

if [ -z "${SEARCH_TERMS}" ]; then
    log "No search terms found in evidence item"
    exit 1
fi

# Initialize search results
CORPUS_SOURCES=0
NOTEBOOK_SOURCES=0
TOTAL_MATCHES=0

# Search shadowLens corpus
log "Searching shadowLens corpus..."
if [ -d "${CORPUS_BASE}/shadowLens" ]; then
    for term in ${SEARCH_TERMS}; do
        MATCHES=$(grep -r -l "${term}" "${CORPUS_BASE}/shadowLens" 2>/dev/null | wc -l)
        TOTAL_MATCHES=$((TOTAL_MATCHES + MATCHES))
        CORPUS_SOURCES=$((CORPUS_SOURCES + MATCHES))
        log "  Found ${MATCHES} matches for term: ${term}"
    done
fi

# Search Telegram corpus (if exists)
log "Searching Telegram corpus..."
if [ -f "${CORPUS_BASE}/telegram_posts.txt" ]; then
    for term in ${SEARCH_TERMS}; do
        MATCHES=$(grep -c "${term}" "${CORPUS_BASE}/telegram_posts.txt" 2>/dev/null || echo 0)
        TOTAL_MATCHES=$((TOTAL_MATCHES + MATCHES))
        CORPUS_SOURCES=$((CORPUS_SOURCES + 1))
        log "  Found ${MATCHES} matches for term: ${term} in Telegram"
    done
fi

# Calculate effective sources (with notebook discount)
EFFECTIVE_SOURCES=$(echo "scale=2; ${CORPUS_SOURCES} + (${NOTEBOOK_SOURCES} * 0.5)" | bc)

log "Backward search complete for ${EVIDENCE_ID}"
log "  Corpus sources: ${CORPUS_SOURCES}"
log "  Notebook sources: ${NOTEBOOK_SOURCES}"
log "  Effective sources: ${EFFECTIVE_SOURCES}"

# Output results
cat > "${COORDINATION_DIR}/backward_search_${EVIDENCE_ID}.json" <<EOF
{
  "evidence_id": "${EVIDENCE_ID}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "search_results": {
    "corpus_sources": ${CORPUS_SOURCES},
    "notebook_sources": ${NOTEBOOK_SOURCES},
    "effective_sources": ${EFFECTIVE_SOURCES},
    "total_matches": ${TOTAL_MATCHES}
  },
  "next_action": "tier_assignment"
}
EOF

log "Results written to: backward_search_${EVIDENCE_ID}.json"

# Trigger tier assignment based on effective sources
if (( $(echo "${EFFECTIVE_SOURCES} >= 3.0" | bc -l) )); then
    log "UPGRADE: ${EVIDENCE_ID} qualifies for Tier 2 (effective_sources >= 3.0)"
    echo "${EVIDENCE_ID}" >> "${COORDINATION_DIR}/tier_upgrade_queue.txt"
elif (( $(echo "${EFFECTIVE_SOURCES} >= 2.0" | bc -l) )); then
    log "PROMOTE: ${EVIDENCE_ID} qualifies for Tier 3 (effective_sources >= 2.0)"
    echo "${EVIDENCE_ID}" >> "${COORDINATION_DIR}/tier_upgrade_queue.txt"
else
    log "FLAGGED: ${EVIDENCE_ID} needs additional validation (effective_sources < 2.0)"
    echo "${EVIDENCE_ID}" >> "${COORDINATION_DIR}/validation_queue.txt"
fi

exit 0
