# Gap Filler Reactive - Quick Reference Card

**Run ID:** `cert1-gap-filler-reactive-20251121`

---

## 🚀 Quick Start

```bash
cd /Users/breydentaylor/certainly/visualizations/agents/Gap_Filler_Reactive
./start.sh
```

**That's it!** Processor runs continuously, monitoring for new evidence.

---

## 📁 Key Files

### INPUT
- `coordination/live_evidence_feed.json` ← Pillar_Scout writes here

### OUTPUTS
- `coordination/gap_fill_reactive_log.json` ← All reactions
- `coordination/tier_upgrades_live.json` ← Tier changes
- `coordination/high_priority_flags.json` ← Urgent flags

---

## 🎯 Reactive Triggers

| Trigger | Activates When | Actions |
|---------|----------------|---------|
| **1. Victim Report** | `victim_name` exists | Search blockchain + Telegram, assign tier, flag interview |
| **2. Court Record** | `case_number` exists | Verify shadowLens, upgrade tiers |
| **3. Video Evidence** | `video_url` exists | Count wire fraud, flag archival |
| **4. Entity Discovery** | `entity_name` exists | Search corpus, map relationships |

---

## 📊 Tier Assignment

```
3+ sources  →  Tier 2
1-2 sources →  Tier 3
0 sources   →  Flagged
```

**Sources = unique corpus files with matches**

---

## 🚨 High-Priority Flags

- **victim_interview** - 2+ sources
- **wire_fraud_pattern** - 10+ instances
- **corporate_records_search** - Entity with 2+ sources
- **archive_video** - Video evidence found

---

## 🔍 Corpus Locations

```
/Users/breydentaylor/certainly/
├── noteworthy-raw/*.csv         (Blockchain)
├── shurka-dump/*.csv             (Blockchain)
├── shurka-dump/recon_intel/      (Telegram)
└── visualizations/coordination/shadowlens_evidence.json
```

---

## 📝 Pillar_Scout Integration

```javascript
// Pillar_Scout adds discovery to feed
const feed = JSON.parse(fs.readFileSync('coordination/live_evidence_feed.json'));

feed.items.push({
  evidence_id: "pillar_scout_001",
  type: "victim_report",  // or court_record, video_evidence, entity
  category: "victim_testimony",
  timestamp: "2025-11-21T10:00:00Z",
  metadata: {
    victim_name: "John Doe",
    wallet_address: "0x...",
    amount_lost: 50000
  }
});

fs.writeFileSync('coordination/live_evidence_feed.json', JSON.stringify(feed, null, 2));
```

**Gap_Filler_Reactive auto-processes within 5 seconds**

---

## 🛠️ Commands

### Production
```bash
./start.sh              # Start processor (continuous)
```

### Testing
```bash
./test.sh               # Automated test (20s)
npm run simulate        # Add test items
node dashboard.js       # Live monitoring
```

### Monitoring
```bash
# Check if running
ps aux | grep reactive_processor

# View reactions
cat coordination/gap_fill_reactive_log.json | jq '.reactions[-5:]'

# View flags
cat coordination/high_priority_flags.json | jq '.flags'
```

---

## ⚡ Performance

- **Detection:** < 5 seconds
- **Search:** 100-500ms per pattern
- **Memory:** < 50MB
- **Throughput:** ~720 items/hour

---

## ✅ Test Results

**Last Test:** 2025-11-21 07:57 UTC

| Item | Type | Sources | Tier | Flags |
|------|------|---------|------|-------|
| TEST_VICTIM_001 | Victim | 0 | Flagged | None |
| TEST_WALLET_001 | Blockchain | 2 CSVs | Tier 3 | Victim Interview |

**Status:** ✅ Working

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Not detecting items | Check `live_evidence_feed.json` has new items |
| No corpus matches | Verify corpus files exist at expected paths |
| Process not running | Run `ps aux \| grep reactive` to check |
| Malformed JSON | Check feed file syntax |

---

## 📚 Full Documentation

- `README.md` - Usage instructions
- `INTEGRATION_GUIDE.md` - Integration details
- `SYSTEM_SUMMARY.md` - Complete system overview

---

**Status:** Production Ready ✅
**Contact:** Check logs in `coordination/gap_fill_reactive_log.json`
