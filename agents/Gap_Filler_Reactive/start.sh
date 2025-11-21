#!/bin/bash
# Start Gap Filler Reactive Processor
# Run ID: cert1-gap-filler-reactive-20251121

echo "==================================="
echo "Gap Filler Reactive Processor"
echo "Run ID: cert1-gap-filler-reactive-20251121"
echo "==================================="
echo ""

cd "$(dirname "$0")"

# Check if live feed exists
LIVE_FEED="/Users/breydentaylor/certainly/visualizations/coordination/live_evidence_feed.json"
if [ ! -f "$LIVE_FEED" ]; then
  echo "[SETUP] Creating live_evidence_feed.json..."
  cat > "$LIVE_FEED" << 'EOF'
{
  "created": "2025-11-21T00:00:00.000Z",
  "last_updated": "2025-11-21T00:00:00.000Z",
  "description": "Live feed for Pillar_Scout discoveries",
  "items": []
}
EOF
fi

echo "[INFO] Monitoring: coordination/live_evidence_feed.json"
echo "[INFO] Output logs:"
echo "  - gap_fill_reactive_log.json"
echo "  - tier_upgrades_live.json"
echo "  - high_priority_flags.json"
echo ""
echo "[START] Press Ctrl+C to stop"
echo ""

# Start the processor
node reactive_processor.js
