#!/bin/bash
# Real-time monitoring script for continuous discovery loop

set -euo pipefail

WORKING_DIR="/Users/breydentaylor/certainly/visualizations"
COORDINATION_DIR="${WORKING_DIR}/coordination"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

clear
echo "=========================================="
echo "CERT1 CONTINUOUS LOOP - REAL-TIME MONITOR"
echo "=========================================="
echo ""

while true; do
    # Clear previous output (keep header)
    tput cup 4 0
    tput ed

    if [ ! -f "${COORDINATION_DIR}/continuous_loop_state.json" ]; then
        echo -e "${RED}Waiting for continuous loop to initialize...${NC}"
        sleep 5
        continue
    fi

    # Read state
    STATE=$(cat "${COORDINATION_DIR}/continuous_loop_state.json")
    RUN_STATUS=$(echo "$STATE" | jq -r '.status')
    TOTAL_DISCOVERIES=$(echo "$STATE" | jq -r '.total_discoveries')
    TOTAL_UPGRADES=$(echo "$STATE" | jq -r '.total_upgrades // 0')

    echo -e "${BLUE}Run Status:${NC} ${RUN_STATUS}"
    echo -e "${BLUE}Total Discoveries:${NC} ${TOTAL_DISCOVERIES}"
    echo -e "${BLUE}Total Upgrades:${NC} ${TOTAL_UPGRADES}"
    echo ""

    # Cycle statuses
    echo -e "${YELLOW}═══ DISCOVERY CYCLES ═══${NC}"
    for cycle in cycle1_reddit cycle2_courts cycle3_video cycle4_victims cycle5_linkedin; do
        STATUS=$(echo "$STATE" | jq -r ".cycles.${cycle}.status")
        COUNT=$(echo "$STATE" | jq -r ".cycles.${cycle}.discoveries // 0")

        case $STATUS in
            "completed")
                COLOR=$GREEN
                ICON="✓"
                ;;
            "in_progress")
                COLOR=$YELLOW
                ICON="⋯"
                ;;
            "pending")
                COLOR=$RED
                ICON="○"
                ;;
            *)
                COLOR=$NC
                ICON="?"
                ;;
        esac

        printf "${COLOR}${ICON}${NC} %-20s Status: %-12s Discoveries: %d\n" "${cycle}" "${STATUS}" "${COUNT}"
    done

    echo ""

    # Process statuses
    echo -e "${YELLOW}═══ CONTINUOUS PROCESSES ═══${NC}"
    for process in backward_citation soundness_evaluator tier_assignment evidence_builder; do
        PROC_STATUS=$(echo "$STATE" | jq -r ".processes.${process}.status // \"unknown\"")

        case $PROC_STATUS in
            "running"|"completed")
                COLOR=$GREEN
                ICON="✓"
                ;;
            *)
                COLOR=$YELLOW
                ICON="⋯"
                ;;
        esac

        printf "${COLOR}${ICON}${NC} %-25s Status: %s\n" "${process}" "${PROC_STATUS}"
    done

    echo ""

    # Prosecution readiness (if available)
    if [ -f "${COORDINATION_DIR}/prosecution_readiness_live.json" ]; then
        READINESS=$(cat "${COORDINATION_DIR}/prosecution_readiness_live.json")
        TIER1=$(echo "$READINESS" | jq -r '.readiness_summary.tier1_prosecution_ready // 0')
        TIER2=$(echo "$READINESS" | jq -r '.readiness_summary.tier2_one_subpoena_away // 0')
        PERCENTAGE=$(echo "$READINESS" | jq -r '.readiness_summary.percentage_prosecution_ready // 0')

        echo -e "${YELLOW}═══ PROSECUTION READINESS ═══${NC}"
        echo -e "${GREEN}Tier 1 (Ready Now):${NC}        ${TIER1}"
        echo -e "${BLUE}Tier 2 (One Subpoena):${NC}     ${TIER2}"
        echo -e "${BLUE}Prosecution Ready %:${NC}       ${PERCENTAGE}%"
        echo ""
    fi

    # Recent activity from log (last 5 lines)
    if [ -f "${COORDINATION_DIR}/continuous_loop.log" ]; then
        echo -e "${YELLOW}═══ RECENT ACTIVITY ═══${NC}"
        tail -5 "${COORDINATION_DIR}/continuous_loop.log"
        echo ""
    fi

    echo "Press Ctrl+C to exit. Refreshing every 5 seconds..."

    sleep 5
done
