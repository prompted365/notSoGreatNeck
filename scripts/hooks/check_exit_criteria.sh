#!/bin/bash
# Check exit criteria - should we continue looping or stop?

set -e

MANIFEST="memory/evidence_manifest.json"
GAPS="coordination/gap_analysis.json"
BLOCKCHAIN="coordination/blockchain_attribution_report.json"
EXIT_CRITERIA_FILE="state/exit_criteria.json"

# Initialize counters
TIER1_COUNT=0
TIER2_COUNT=0
UNFILLED_GAPS=0
BLOCKCHAIN_ATTRIBUTION_RATE=0
PROSECUTION_READINESS=0

# Read evidence manifest for TIER counts
if [ -f "$MANIFEST" ]; then
    TIER1_COUNT=$(jq -r '.tier_breakdown.tier1 // 0' "$MANIFEST")
    TIER2_COUNT=$(jq -r '.tier_breakdown.tier2 // 0' "$MANIFEST")
fi

# Read gap analysis for unfilled gaps
if [ -f "$GAPS" ]; then
    UNFILLED_GAPS=$(jq -r '.unfilled_gaps // 0' "$GAPS")
fi

# Read blockchain attribution rate
if [ -f "$BLOCKCHAIN" ]; then
    BLOCKCHAIN_ATTRIBUTION_RATE=$(jq -r '.attribution_rate // 0' "$BLOCKCHAIN")
fi

# Calculate prosecution readiness (weighted formula)
# Tier 1 * 3 + Tier 2 * 2 + (100 - unfilled_gaps/10)
PROSECUTION_READINESS=$(echo "scale=2; ($TIER1_COUNT * 3 + $TIER2_COUNT * 2) / 2 + (100 - $UNFILLED_GAPS / 10)" | bc)

# Define exit criteria thresholds
TARGET_TIER1=60
TARGET_GAPS=100
TARGET_ATTRIBUTION=75
TARGET_READINESS=85

# Check each criterion
TIER1_MET=false
GAPS_MET=false
ATTRIBUTION_MET=false
READINESS_MET=false

[ "$TIER1_COUNT" -ge "$TARGET_TIER1" ] && TIER1_MET=true
[ "$UNFILLED_GAPS" -le "$TARGET_GAPS" ] && GAPS_MET=true
[ "$(echo "$BLOCKCHAIN_ATTRIBUTION_RATE >= $TARGET_ATTRIBUTION" | bc)" -eq 1 ] && ATTRIBUTION_MET=true
[ "$(echo "$PROSECUTION_READINESS >= $TARGET_READINESS" | bc)" -eq 1 ] && READINESS_MET=true

# Write exit criteria status
jq -n \
    --argjson tier1_count "$TIER1_COUNT" \
    --argjson target_tier1 "$TARGET_TIER1" \
    --arg tier1_met "$TIER1_MET" \
    --argjson unfilled_gaps "$UNFILLED_GAPS" \
    --argjson target_gaps "$TARGET_GAPS" \
    --arg gaps_met "$GAPS_MET" \
    --argjson attribution_rate "$BLOCKCHAIN_ATTRIBUTION_RATE" \
    --argjson target_attribution "$TARGET_ATTRIBUTION" \
    --arg attribution_met "$ATTRIBUTION_MET" \
    --argjson prosecution_readiness "$PROSECUTION_READINESS" \
    --argjson target_readiness "$TARGET_READINESS" \
    --arg readiness_met "$READINESS_MET" \
    '{
        tier1: {current: $tier1_count, target: $target_tier1, met: ($tier1_met == "true")},
        gaps: {current: $unfilled_gaps, target: $target_gaps, met: ($gaps_met == "true")},
        attribution: {current: $attribution_rate, target: $target_attribution, met: ($attribution_met == "true")},
        readiness: {current: $prosecution_readiness, target: $target_readiness, met: ($readiness_met == "true")}
    }' > "$EXIT_CRITERIA_FILE"

# Determine if ALL criteria met
ALL_MET=false
if [ "$TIER1_MET" = "true" ] && [ "$GAPS_MET" = "true" ] && [ "$ATTRIBUTION_MET" = "true" ] && [ "$READINESS_MET" = "true" ]; then
    ALL_MET=true
fi

echo "📊 EXIT CRITERIA CHECK:"
echo "  Tier 1 evidence: ${TIER1_COUNT}/${TARGET_TIER1} $([ "$TIER1_MET" = "true" ] && echo "✅" || echo "❌")"
echo "  Unfilled gaps: ${UNFILLED_GAPS}/${TARGET_GAPS} $([ "$GAPS_MET" = "true" ] && echo "✅" || echo "❌")"
echo "  Blockchain attribution: ${BLOCKCHAIN_ATTRIBUTION_RATE}%/${TARGET_ATTRIBUTION}% $([ "$ATTRIBUTION_MET" = "true" ] && echo "✅" || echo "❌")"
echo "  Prosecution readiness: ${PROSECUTION_READINESS}%/${TARGET_READINESS}% $([ "$READINESS_MET" = "true" ] && echo "✅" || echo "❌")"
echo ""

if [ "$ALL_MET" = "true" ]; then
    echo "🎯 EXIT CRITERIA MET - Investigation complete, generating final package"
    exit 0  # Signal: STOP LOOPING
else
    echo "🔄 CONTINUE - Exit criteria not met, continuing investigation loop"
    exit 1  # Signal: KEEP LOOPING
fi
