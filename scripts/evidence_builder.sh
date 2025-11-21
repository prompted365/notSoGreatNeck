#!/bin/bash
# Process D: Evidence Builder
# Organize all items into prosecution-ready structure

set -euo pipefail

WORKING_DIR="/Users/breydentaylor/certainly/visualizations"
COORDINATION_DIR="${WORKING_DIR}/coordination"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [EVIDENCE_BUILDER] $1" | tee -a "${COORDINATION_DIR}/continuous_loop.log"
}

log "Starting evidence builder aggregation..."

# Collect all evidence items from discovery cycles
ALL_EVIDENCE=""
for cycle_file in pillar_reddit_live pillar_courts_live pillar_video_live victim_correlations_live entity_updates_live; do
    if [ -f "${COORDINATION_DIR}/${cycle_file}.json" ]; then
        CYCLE_ITEMS=$(jq -r '.[] | @json' "${COORDINATION_DIR}/${cycle_file}.json" 2>/dev/null || echo "")
        if [ -n "${CYCLE_ITEMS}" ]; then
            log "  Found $(echo "${CYCLE_ITEMS}" | wc -l) items in ${cycle_file}"
            ALL_EVIDENCE="${ALL_EVIDENCE}${CYCLE_ITEMS}"$'\n'
        fi
    fi
done

# Count total items
TOTAL_ITEMS=$(echo "${ALL_EVIDENCE}" | grep -v '^$' | wc -l)
log "Total evidence items collected: ${TOTAL_ITEMS}"

# Initialize prosecution structure
cat > "${COORDINATION_DIR}/prosecution_structure_live.json" <<EOF
{
  "run_id": "cert1-continuous-loop-20251121",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "total_items": ${TOTAL_ITEMS},
  "by_tier": {
    "tier1": [],
    "tier2": [],
    "tier3": [],
    "tier4": [],
    "tier5": []
  },
  "by_type": {
    "type1_government": [],
    "type2_authenticated": [],
    "type3_blockchain": [],
    "type4_multisource_osint": [],
    "type5_pattern": [],
    "type6_single_source": [],
    "type7_inference": [],
    "type8_derivative": [],
    "type9_attribution_needed": [],
    "type10_ai_analysis": []
  },
  "narrative_threads": {
    "victim_to_transaction": [],
    "transaction_to_entity": [],
    "entity_to_fraud_pattern": [],
    "fraud_pattern_to_rico": []
  },
  "visual_maps": {
    "entity_network": "${COORDINATION_DIR}/entity_relationship_map.json",
    "transaction_flow": "${COORDINATION_DIR}/transaction_network.json",
    "timeline": "${COORDINATION_DIR}/rico_timeline_1993_2025.json"
  }
}
EOF

log "Prosecution structure initialized"

# Process each evidence item
TIER1_COUNT=0
TIER2_COUNT=0
TIER3_COUNT=0

echo "${ALL_EVIDENCE}" | while IFS= read -r item; do
    if [ -z "${item}" ]; then
        continue
    fi

    EVIDENCE_ID=$(echo "${item}" | jq -r '.evidence_id' 2>/dev/null || echo "unknown")

    # Check if tier assignment exists
    if [ -f "${COORDINATION_DIR}/tier_assignment_${EVIDENCE_ID}.json" ]; then
        TIER=$(jq -r '.tier_assignment.new_tier' "${COORDINATION_DIR}/tier_assignment_${EVIDENCE_ID}.json")
        TYPE=$(echo "${item}" | jq -r '.type' 2>/dev/null || echo "unknown")

        # Add to tier bucket
        case ${TIER} in
            1) TIER1_COUNT=$((TIER1_COUNT + 1)) ;;
            2) TIER2_COUNT=$((TIER2_COUNT + 1)) ;;
            3) TIER3_COUNT=$((TIER3_COUNT + 1)) ;;
        esac

        log "  Categorized ${EVIDENCE_ID}: Tier ${TIER}, Type ${TYPE}"
    fi
done

log "Evidence categorization complete"
log "  Tier 1 (prosecution-ready): ${TIER1_COUNT}"
log "  Tier 2 (one subpoena away): ${TIER2_COUNT}"
log "  Tier 3 (investigative development): ${TIER3_COUNT}"

# Update prosecution readiness live
cat > "${COORDINATION_DIR}/prosecution_readiness_live.json" <<EOF
{
  "run_id": "cert1-continuous-loop-20251121",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "readiness_summary": {
    "total_items": ${TOTAL_ITEMS},
    "tier1_prosecution_ready": ${TIER1_COUNT},
    "tier2_one_subpoena_away": ${TIER2_COUNT},
    "tier3_investigative": ${TIER3_COUNT},
    "percentage_prosecution_ready": $(echo "scale=2; ${TIER1_COUNT} * 100 / ${TOTAL_ITEMS}" | bc 2>/dev/null || echo 0)
  },
  "subpoena_priority": {
    "exchange_kyc": "P1 - Critical for blockchain attribution",
    "nassau_county_clerk": "P1 - 2002 Creditor-Proof Agreement",
    "ny_court_records": "P2 - 1993 Efraim conviction",
    "bank_records": "P2 - PDI 2011 transactions"
  },
  "next_actions": [
    "Issue P1 subpoenas for immediate tier upgrades",
    "Continue victim outreach for wallet correlations",
    "Expand Reddit/court record discovery",
    "Build narrative threads for prosecution"
  ]
}
EOF

log "Prosecution readiness updated: ${COORDINATION_DIR}/prosecution_readiness_live.json"
log "Evidence builder aggregation complete"

exit 0
