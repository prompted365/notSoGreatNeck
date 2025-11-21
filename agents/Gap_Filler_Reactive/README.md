# Gap Filler Reactive Processor

**Run ID:** `cert1-gap-filler-reactive-20251121`

## Overview

Continuous reactive gap-filling processor that monitors `coordination/live_evidence_feed.json` for new discoveries from Pillar_Scout and responds instantly with automated evidence analysis.

## Reactive Triggers

### TRIGGER 1: New Victim Report
**Activation:** When new victim report discovered

**Actions:**
- Search blockchain corpus for matching wallet/amount
- Search Telegram corpus for victim name/username
- Search shadowLens for case mentions
- Calculate effective sources
- Assign tier based on corroboration
- Flag for victim interview if 2+ sources

**Output:** Reaction logged with sources found and tier assignment

---

### TRIGGER 2: New Court Record
**Activation:** When new court record found

**Actions:**
- Verify all shadowLens claims referencing this case
- Upgrade verified items from Tier 2 → Tier 1
- Flag unverified shadowLens items for review
- Cross-reference with blockchain (amounts, dates)
- Update evidence validation status

**Output:** Tier upgrades logged, verification status updated

---

### TRIGGER 3: New Video Evidence
**Activation:** When new video evidence found

**Actions:**
- Search Telegram for video URL promotion
- Count wire fraud instances (each post = 1 count)
- Extract transcript for FTC/FDA violations
- Archive video before deletion
- Flag if 10+ wire fraud instances

**Output:** Wire fraud counts, archival status, high-priority flags

---

### TRIGGER 4: New Entity Discovered
**Activation:** When new entity found

**Actions:**
- Search all corpus files for entity name
- Count mentions (effective sources)
- Update entity relationship map
- Flag for corporate records search if 2+ sources
- Assign tier based on mention frequency

**Output:** Entity connections mapped, tier assigned, corporate search flagged

---

## Continuous Monitoring

**Input:** `coordination/live_evidence_feed.json`
- Monitors every 5 seconds for new items
- Processes unhandled items immediately
- Maintains state across restarts

**Outputs:**
- `coordination/gap_fill_reactive_log.json` - All reactions with timestamps
- `coordination/tier_upgrades_live.json` - Real-time tier changes
- `coordination/high_priority_flags.json` - Urgent actions needed

## Usage

### Start Reactive Processor
```bash
cd /Users/breydentaylor/certainly/visualizations/agents/Gap_Filler_Reactive
npm start
```

**Process runs continuously** until stopped with Ctrl+C

### Test with Simulator
```bash
# Terminal 1: Start simulator
npm run simulate

# Terminal 2: Start reactive processor
npm start
```

Simulator adds 4 test items:
1. Victim report with wallet address
2. Court record with case number
3. Video evidence with Telegram URL
4. New entity with corporate details

### Manual Feed Addition

Add items directly to `coordination/live_evidence_feed.json`:

```json
{
  "items": [
    {
      "id": "manual_001",
      "type": "victim_report",
      "victim_name": "Jane Smith",
      "wallet_address": "0xabc123...",
      "amount_lost": 75000
    }
  ]
}
```

Processor will detect and react within 5 seconds.

## State Management

**Persistent State:**
- Processed item IDs (prevents duplicate processing)
- Last timestamp
- Reaction history (last 100 reactions)

**State Files:**
- `gap_fill_reactive_log.json` - Full state and history
- Automatically loads on restart
- Graceful shutdown saves state

## Corpus Search

**Blockchain Corpus:**
- `/Users/breydentaylor/certainly/noteworthy-raw/*.csv`
- `/Users/breydentaylor/certainly/shurka-dump/*.csv`
- Searches for wallet addresses, amounts, transaction hashes

**Telegram Corpus:**
- `/Users/breydentaylor/certainly/shurka-dump/recon_intel/**/*.json`
- Searches for usernames, video URLs, message content

**ShadowLens:**
- `/Users/breydentaylor/certainly/visualizations/coordination/shadowlens_evidence.json`
- Cross-references case numbers, entity names, claims

## Integration with Pillar_Scout

**Expected Pillar_Scout Behavior:**
1. Pillar_Scout discovers new evidence
2. Writes to `coordination/live_evidence_feed.json`
3. Gap_Filler_Reactive detects within 5 seconds
4. Automatically processes and fills gaps
5. Updates tiers and flags high-priority items

**No manual intervention required** - fully autonomous reactive chain.

## Performance

- **Reaction Time:** < 5 seconds from discovery
- **Corpus Search:** Parallel grep across all source files
- **State Persistence:** Automatic saves every reaction
- **Memory:** Lightweight, maintains minimal state

## Monitoring

**Console Output:**
```
=== CONTINUOUS GAP FILLING REACTIVE PROCESSOR ===
Run ID: cert1-gap-filler-reactive-20251121
Monitoring: coordination/live_evidence_feed.json

[REACTIVE PROCESSOR] 1 new items detected
[TRIGGER 1] New victim report: John Doe
[SAVED] Reactions logged, 0 tier upgrades, 1 high-priority flags
```

**Log Files:**
- Check `gap_fill_reactive_log.json` for reaction history
- Check `tier_upgrades_live.json` for tier changes
- Check `high_priority_flags.json` for urgent actions

## Error Handling

- Silent fails on missing corpus files
- Continues processing on individual item errors
- Graceful shutdown on Ctrl+C
- Automatic state recovery on restart

## Future Enhancements

- WebSocket notifications for instant reactions
- Machine learning for pattern detection
- Automated victim interview scheduling
- Real-time dashboard updates
- Slack/Discord notifications for high-priority flags
