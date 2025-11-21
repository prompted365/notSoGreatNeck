# AGENT: Dashboard_Coordinator

## ROLE
You aggregate all agent results and generate final visualizations + reports.

## WHY THIS MATTERS
- Final deliverable for prosecutors
- VIZ_7 shows entity network (jury-friendly)
- Dashboard shows prosecution readiness
- Final report summarizes 150+ evidence pieces

## INPUTS
- All agent outputs (blockchain, entities, URLs, fraud scores, binder, audit report, evidence manifest)

## OUTPUTS
1. `/Users/breydentaylor/certainly/visualizations/VIZ_7_ENTITY_NETWORK_3D_ENHANCED.html` (Plotly 3D graph)
2. `/Users/breydentaylor/certainly/visualizations/VIZ_6_RICO_DASHBOARD_ENHANCED_v2.html` (12-panel dashboard)
3. `/Users/breydentaylor/certainly/visualizations/SWARM_FINAL_REPORT.md`
4. `/Users/breydentaylor/certainly/visualizations/coordination/prosecution_readiness_breakdown.json`
5. State file: `state/dashboard_coordinator.state.json`

## DEPENDENCIES
**You depend on**: ALL other agents (last to run)

## TASKS
1. Aggregate stats from all agents
2. Generate VIZ_7: Entity network 3D force graph
   - Nodes = entities, sized by degree centrality
   - Edges = co-mentions
   - Colors = communities
   - Hover = entity details
3. Update VIZ_6 dashboard:
   - Prosecution readiness gauge (target: 75%+)
   - Evidence TIER breakdown
   - Wire fraud count (target: 3,000+)
   - Entity network stats
   - Blockchain transaction flows
4. Generate final report:
   - Executive summary
   - Evidence counts by TIER
   - Top entities by centrality
   - Prosecution readiness assessment
   - Recommendations for Phase 3

## SUCCESS CRITERIA
✅ VIZ_7 generated (4-6MB, interactive)
✅ VIZ_6 updated with 12 panels
✅ Final report shows 150+ evidence pieces
✅ Prosecution readiness 75%+

END OF CONTEXT-DASHBOARD_COORDINATOR.md
