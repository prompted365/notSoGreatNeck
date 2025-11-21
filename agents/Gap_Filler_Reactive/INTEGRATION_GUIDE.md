# Gap Filler Reactive - Integration Guide

## Overview

The Gap Filler Reactive Processor is a **continuous monitoring system** that watches for new evidence discoveries and automatically fills gaps in real-time. It integrates seamlessly with Pillar_Scout and the existing evidence validation pipeline.

---

## Architecture

```
┌─────────────────┐
│  Pillar_Scout   │  ← Discovers new evidence
└────────┬────────┘
         │ writes to
         ↓
┌─────────────────────────────┐
│  live_evidence_feed.json    │  ← Monitored file (every 5 seconds)
└────────┬────────────────────┘
         │ triggers
         ↓
┌──────────────────────────────┐
│  Gap_Filler_Reactive         │  ← Reacts instantly
│  - Process triggers 1-4      │
│  - Search corpus files       │
│  - Assign tiers              │
│  - Flag high-priority        │
└────────┬─────────────────────┘
         │ outputs
         ↓
┌───────────────────────────────────────┐
│  Output Files:                        │
│  - gap_fill_reactive_log.json         │
│  - tier_upgrades_live.json            │
│  - high_priority_flags.json           │
└───────────────────────────────────────┘
```

---

## Integration with Pillar_Scout

### Step 1: Pillar_Scout Discovers Evidence

When Pillar_Scout finds new evidence (victim report, court record, video, entity), it writes to `coordination/live_evidence_feed.json`:

```json
{
  "items": [
    {
      "id": "pillar_scout_20251121_001",
      "type": "victim_report",
      "victim_name": "John Doe",
      "wallet_address": "0x7d8378d189831f25e184621a1cc026fc99f9c48c",
      "amount_lost": 50000,
      "source": "victim_interview_20251121",
      "discovered_at": "2025-11-21T10:30:00Z"
    }
  ]
}
```

### Step 2: Gap_Filler_Reactive Detects New Item

Within **5 seconds**, the reactive processor:
1. Detects new item (ID not in processed set)
2. Determines trigger type (victim_report, court_record, video_evidence, entity)
3. Executes appropriate reactive trigger

### Step 3: Automatic Gap Filling

**For victim report:**
- Searches blockchain corpus for wallet address
- Searches Telegram for victim mentions
- Searches shadowLens for related cases
- Calculates effective sources: `blockchain (2) + telegram (1) = 3 sources`
- Assigns tier: `3 sources → Tier 2`
- Flags for victim interview if 2+ sources

**Result logged to `gap_fill_reactive_log.json`:**
```json
{
  "trigger": "victim_report",
  "item_id": "pillar_scout_20251121_001",
  "actions": [
    {
      "action": "blockchain_match",
      "wallet": "0x7d8378...",
      "sources": 2,
      "files": ["shurka-dump/danviv_big_map.csv", "noteworthy-raw/shurka123.csv"]
    },
    {
      "action": "telegram_mention",
      "victim": "John Doe",
      "sources": 1,
      "files": ["recon_intel/telegram/jasonyosefshurka/messages.json"]
    }
  ],
  "tier_assigned": 2,
  "effective_sources": 3
}
```

---

## Corpus Search Integration

### Blockchain Corpus
**Searched for:**
- Wallet addresses (exact match)
- Transaction amounts (fuzzy match)
- Transaction hashes

**Locations:**
- `/Users/breydentaylor/certainly/noteworthy-raw/*.csv`
- `/Users/breydentaylor/certainly/shurka-dump/*.csv`

**Search method:** `grep -ril` for fast text search across all CSV files

---

### Telegram Corpus
**Searched for:**
- Usernames
- Video URLs
- Victim names
- Message content

**Locations:**
- `/Users/breydentaylor/certainly/shurka-dump/recon_intel/telegram/**/*.json`

**Search method:** Recursive JSON text search

---

### ShadowLens Corpus
**Searched for:**
- Case numbers
- Entity names
- Claims and allegations

**Location:**
- `/Users/breydentaylor/certainly/visualizations/coordination/shadowlens_evidence.json`

**Search method:** In-memory JSON parsing and matching

---

## Tier Assignment Logic

```javascript
// Based on effective sources count
if (effective_sources >= 3) → Tier 2
else if (effective_sources >= 1) → Tier 3
else → Flagged
```

**Effective sources = unique corpus files with matches**

Example:
- 2 blockchain CSV files + 1 Telegram JSON = 3 effective sources → **Tier 2**

---

## High-Priority Flags

Automatically flagged for immediate action:

| Condition | Flag Type | Priority |
|-----------|-----------|----------|
| Victim with 2+ sources | `victim_interview` | High |
| 10+ wire fraud instances | `wire_fraud_pattern` | Critical |
| Entity with 2+ sources | `corporate_records_search` | Medium |
| Video evidence found | `archive_video` | Critical |

**Output:** `coordination/high_priority_flags.json`

```json
{
  "flags": [
    {
      "type": "victim_interview",
      "item_id": "pillar_scout_20251121_001",
      "victim_name": "John Doe",
      "reason": "3 corroborating sources found",
      "timestamp": "2025-11-21T10:30:05Z"
    }
  ]
}
```

---

## Tier Upgrades

When court records verify shadowLens claims:

**Before:** shadowLens item at Tier 2 (unverified)
**After:** Court record confirms → Upgrade to Tier 1

**Output:** `coordination/tier_upgrades_live.json`

```json
{
  "upgrades": [
    {
      "item_id": "shadowlens_claim_123",
      "from_tier": 2,
      "to_tier": 1,
      "reason": "Court record verification: 25-cv-00123",
      "timestamp": "2025-11-21T10:35:00Z"
    }
  ]
}
```

---

## Running the System

### Start Reactive Processor (Production)
```bash
cd /Users/breydentaylor/certainly/visualizations/agents/Gap_Filler_Reactive
./start.sh
```

Runs continuously until Ctrl+C. Monitors `live_evidence_feed.json` every 5 seconds.

---

### Test with Simulator (Development)
```bash
# Terminal 1: Start simulator
cd /Users/breydentaylor/certainly/visualizations/agents/Gap_Filler_Reactive
npm run simulate

# Terminal 2: Start reactive processor
npm start
```

Simulator adds 4 test items over 15 seconds:
1. Victim report (2s delay)
2. Court record (5s delay)
3. Video evidence (8s delay)
4. Entity (11s delay)

---

### Quick Test (Automated)
```bash
./test.sh
```

Runs simulator + processor for 20 seconds, displays results.

---

### Monitor with Dashboard
```bash
node dashboard.js
```

Real-time dashboard showing:
- Processor status
- Recent reactions
- Tier upgrades
- High-priority flags
- Trigger statistics

Updates every 2 seconds.

---

## File Outputs

### 1. gap_fill_reactive_log.json
**Full state and reaction history**

```json
{
  "run_id": "cert1-gap-filler-reactive-20251121",
  "status": "running",
  "last_updated": "2025-11-21T10:45:00Z",
  "total_reactions": 47,
  "processed_items": ["item1", "item2", "..."],
  "reactions": [...]
}
```

---

### 2. tier_upgrades_live.json
**Real-time tier changes**

```json
{
  "last_updated": "2025-11-21T10:45:00Z",
  "upgrades": [
    {
      "item_id": "...",
      "from_tier": 2,
      "to_tier": 1,
      "reason": "Court record verification",
      "timestamp": "..."
    }
  ]
}
```

---

### 3. high_priority_flags.json
**Urgent actions needed**

```json
{
  "last_updated": "2025-11-21T10:45:00Z",
  "flags": [
    {
      "type": "victim_interview",
      "item_id": "...",
      "reason": "3 corroborating sources",
      "timestamp": "..."
    }
  ]
}
```

---

## Pillar_Scout Integration Requirements

For seamless integration, Pillar_Scout should:

### 1. Write to live_evidence_feed.json
```javascript
// Example Pillar_Scout code
function addDiscovery(evidence) {
  const feed = JSON.parse(fs.readFileSync('coordination/live_evidence_feed.json'));

  feed.items.push({
    id: `pillar_scout_${Date.now()}_${randomId()}`,
    type: evidence.type, // 'victim_report', 'court_record', 'video_evidence', 'entity'
    ...evidence,
    discovered_at: new Date().toISOString()
  });

  feed.last_updated = new Date().toISOString();
  fs.writeFileSync('coordination/live_evidence_feed.json', JSON.stringify(feed, null, 2));
}
```

### 2. Use Standard Item Types
- `victim_report` - New victim discovered
- `court_record` - Court document found
- `video_evidence` - Video/media evidence
- `entity` - New company/person entity

### 3. Include Required Fields

**Victim Report:**
```json
{
  "type": "victim_report",
  "victim_name": "string",
  "wallet_address": "string (optional)",
  "amount_lost": number,
  "claim": "string",
  "source": "string"
}
```

**Court Record:**
```json
{
  "type": "court_record",
  "case_number": "string",
  "case_name": "string",
  "amount": number,
  "date_filed": "YYYY-MM-DD",
  "claims": ["array"],
  "source": "string"
}
```

**Video Evidence:**
```json
{
  "type": "video_evidence",
  "video_url": "string",
  "title": "string",
  "claims": ["array"],
  "posted_date": "YYYY-MM-DD",
  "source": "string"
}
```

**Entity:**
```json
{
  "type": "entity",
  "entity_name": "string",
  "entity_type": "string",
  "related_wallets": ["array (optional)"],
  "source": "string"
}
```

---

## Performance Metrics

- **Detection Latency:** < 5 seconds from feed update
- **Corpus Search:** 100-500ms per pattern (parallel grep)
- **Memory Usage:** < 50MB (lightweight state)
- **Disk I/O:** Append-only logs (efficient)

---

## Error Handling

- **Missing corpus files:** Silent skip, continues processing
- **Malformed feed items:** Logged, skipped
- **Corpus search failures:** Logged, returns empty results
- **State corruption:** Auto-recovery from previous valid state

---

## Monitoring and Debugging

### Check if processor is running
```bash
ps aux | grep reactive_processor
```

### View recent reactions
```bash
cat coordination/gap_fill_reactive_log.json | jq '.reactions[-5:]'
```

### View tier upgrades
```bash
cat coordination/tier_upgrades_live.json | jq '.upgrades'
```

### View high-priority flags
```bash
cat coordination/high_priority_flags.json | jq '.flags'
```

### Tail logs (if logging to file)
```bash
tail -f gap_filler_reactive.log
```

---

## Future Enhancements

1. **WebSocket integration** - Real-time push notifications
2. **ML pattern detection** - Anomaly detection in reactions
3. **Automated victim interviews** - Calendar scheduling
4. **Real-time dashboard** - Web UI with live updates
5. **Slack/Discord webhooks** - Instant team notifications
6. **Distributed processing** - Scale to multiple instances

---

## Support

For issues or questions:
1. Check `gap_fill_reactive_log.json` for errors
2. Review `README.md` for usage instructions
3. Run `./test.sh` to verify system health
4. Check corpus file accessibility

---

**Status:** Production Ready
**Run ID:** cert1-gap-filler-reactive-20251121
**Last Updated:** 2025-11-21
