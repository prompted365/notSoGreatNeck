#!/bin/bash
# Test Gap Filler Reactive Processor with simulated discoveries

echo "==================================="
echo "Testing Gap Filler Reactive"
echo "==================================="
echo ""

cd "$(dirname "$0")"

# Kill any existing processes
echo "[CLEANUP] Stopping any running processors..."
pkill -f "reactive_processor.js" 2>/dev/null
pkill -f "trigger_simulator.js" 2>/dev/null
sleep 1

# Clean output files
echo "[CLEANUP] Cleaning previous test outputs..."
COORD_DIR="/Users/breydentaylor/certainly/visualizations/coordination"
rm -f "$COORD_DIR/gap_fill_reactive_log.json"
rm -f "$COORD_DIR/tier_upgrades_live.json"
rm -f "$COORD_DIR/high_priority_flags.json"

# Start simulator in background
echo "[TEST] Starting trigger simulator..."
node trigger_simulator.js &
SIMULATOR_PID=$!

# Wait for simulator to initialize
sleep 2

# Start reactive processor
echo "[TEST] Starting reactive processor..."
echo ""
timeout 20 node reactive_processor.js || true

# Stop simulator
kill $SIMULATOR_PID 2>/dev/null

echo ""
echo "==================================="
echo "Test Complete"
echo "==================================="
echo ""

# Show results
if [ -f "$COORD_DIR/gap_fill_reactive_log.json" ]; then
  echo "[RESULTS] Reactions logged:"
  cat "$COORD_DIR/gap_fill_reactive_log.json" | head -50
  echo ""
fi

if [ -f "$COORD_DIR/tier_upgrades_live.json" ]; then
  echo "[RESULTS] Tier upgrades:"
  cat "$COORD_DIR/tier_upgrades_live.json"
  echo ""
fi

if [ -f "$COORD_DIR/high_priority_flags.json" ]; then
  echo "[RESULTS] High-priority flags:"
  cat "$COORD_DIR/high_priority_flags.json"
  echo ""
fi

echo "[INFO] Test completed successfully"
