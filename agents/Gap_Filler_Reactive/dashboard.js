#!/usr/bin/env node
/**
 * REACTIVE GAP FILLER DASHBOARD
 * Real-time monitoring of reactive processor status
 */

const fs = require('fs');
const path = require('path');

const COORD_DIR = '/Users/breydentaylor/certainly/visualizations/coordination';
const REACTION_LOG = path.join(COORD_DIR, 'gap_fill_reactive_log.json');
const TIER_UPGRADES = path.join(COORD_DIR, 'tier_upgrades_live.json');
const HIGH_PRIORITY = path.join(COORD_DIR, 'high_priority_flags.json');
const LIVE_FEED = path.join(COORD_DIR, 'live_evidence_feed.json');

function clearScreen() {
  process.stdout.write('\x1Bc');
}

function formatTimestamp(iso) {
  const date = new Date(iso);
  return date.toLocaleString();
}

function displayDashboard() {
  clearScreen();

  console.log('╔════════════════════════════════════════════════════════════════════════╗');
  console.log('║      GAP FILLER REACTIVE PROCESSOR - LIVE DASHBOARD                    ║');
  console.log('║      Run ID: cert1-gap-filler-reactive-20251121                        ║');
  console.log('╚════════════════════════════════════════════════════════════════════════╝');
  console.log('');

  // Load data
  let reactionLog = null;
  let tierUpgrades = null;
  let highPriority = null;
  let liveFeed = null;

  try {
    if (fs.existsSync(REACTION_LOG)) {
      reactionLog = JSON.parse(fs.readFileSync(REACTION_LOG, 'utf8'));
    }
    if (fs.existsSync(TIER_UPGRADES)) {
      tierUpgrades = JSON.parse(fs.readFileSync(TIER_UPGRADES, 'utf8'));
    }
    if (fs.existsSync(HIGH_PRIORITY)) {
      highPriority = JSON.parse(fs.readFileSync(HIGH_PRIORITY, 'utf8'));
    }
    if (fs.existsSync(LIVE_FEED)) {
      liveFeed = JSON.parse(fs.readFileSync(LIVE_FEED, 'utf8'));
    }
  } catch (err) {
    console.log('⚠️  Error loading data:', err.message);
  }

  // Status
  console.log('┌─ PROCESSOR STATUS ─────────────────────────────────────────────────┐');
  if (reactionLog) {
    console.log(`│ Status:           ${reactionLog.status || 'unknown'}                                   │`);
    console.log(`│ Last Updated:     ${formatTimestamp(reactionLog.last_updated || new Date().toISOString()).padEnd(40)} │`);
    console.log(`│ Total Reactions:  ${(reactionLog.total_reactions || 0).toString().padEnd(40)} │`);
    console.log(`│ Items Processed:  ${(reactionLog.processed_items?.length || 0).toString().padEnd(40)} │`);
  } else {
    console.log('│ Status:           Not yet started                                  │');
  }
  console.log('└────────────────────────────────────────────────────────────────────┘');
  console.log('');

  // Live Feed
  console.log('┌─ LIVE EVIDENCE FEED ───────────────────────────────────────────────┐');
  if (liveFeed && liveFeed.items) {
    console.log(`│ Total Items:      ${liveFeed.items.length.toString().padEnd(40)} │`);
    console.log(`│ Last Updated:     ${formatTimestamp(liveFeed.last_updated || '').padEnd(40)} │`);

    const pending = liveFeed.items.length - (reactionLog?.processed_items?.length || 0);
    console.log(`│ Pending:          ${pending.toString().padEnd(40)} │`);
  } else {
    console.log('│ No items yet                                                       │');
  }
  console.log('└────────────────────────────────────────────────────────────────────┘');
  console.log('');

  // Recent Reactions
  console.log('┌─ RECENT REACTIONS (Last 5) ────────────────────────────────────────┐');
  if (reactionLog && reactionLog.reactions && reactionLog.reactions.length > 0) {
    const recent = reactionLog.reactions.slice(-5).reverse();
    recent.forEach((reaction, i) => {
      const trigger = reaction.trigger || 'unknown';
      const itemId = (reaction.item_id || '').substring(0, 20);
      const actions = reaction.actions?.length || 0;
      const time = formatTimestamp(reaction.timestamp).substring(11, 19);

      console.log(`│ ${i+1}. [${time}] ${trigger.padEnd(15)} | ${itemId.padEnd(20)} | ${actions} actions │`);
    });
  } else {
    console.log('│ No reactions yet                                                   │');
  }
  console.log('└────────────────────────────────────────────────────────────────────┘');
  console.log('');

  // Tier Upgrades
  console.log('┌─ TIER UPGRADES ────────────────────────────────────────────────────┐');
  if (tierUpgrades && tierUpgrades.upgrades && tierUpgrades.upgrades.length > 0) {
    console.log(`│ Total Upgrades:   ${tierUpgrades.upgrades.length.toString().padEnd(40)} │`);
    console.log('│                                                                    │');

    const recent = tierUpgrades.upgrades.slice(-3);
    recent.forEach(upgrade => {
      const itemId = (upgrade.item_id || '').substring(0, 20);
      const from = upgrade.from_tier || '?';
      const to = upgrade.to_tier || '?';
      console.log(`│   ${itemId.padEnd(20)} : Tier ${from} → ${to}                        │`);
    });
  } else {
    console.log('│ No tier upgrades yet                                               │');
  }
  console.log('└────────────────────────────────────────────────────────────────────┘');
  console.log('');

  // High Priority Flags
  console.log('┌─ HIGH PRIORITY FLAGS ──────────────────────────────────────────────┐');
  if (highPriority && highPriority.flags && highPriority.flags.length > 0) {
    console.log(`│ Total Flags:      ${highPriority.flags.length.toString().padEnd(40)} │`);
    console.log('│                                                                    │');

    const flagTypes = {};
    highPriority.flags.forEach(flag => {
      flagTypes[flag.type] = (flagTypes[flag.type] || 0) + 1;
    });

    Object.entries(flagTypes).forEach(([type, count]) => {
      console.log(`│   ${type.padEnd(30)} : ${count.toString().padEnd(20)} │`);
    });
  } else {
    console.log('│ No high-priority flags yet                                         │');
  }
  console.log('└────────────────────────────────────────────────────────────────────┘');
  console.log('');

  // Trigger Statistics
  if (reactionLog && reactionLog.reactions) {
    console.log('┌─ TRIGGER STATISTICS ───────────────────────────────────────────────┐');
    const triggerCounts = {};
    reactionLog.reactions.forEach(r => {
      const trigger = r.trigger || 'unknown';
      triggerCounts[trigger] = (triggerCounts[trigger] || 0) + 1;
    });

    Object.entries(triggerCounts).forEach(([trigger, count]) => {
      console.log(`│   ${trigger.padEnd(20)} : ${count.toString().padEnd(30)} │`);
    });
    console.log('└────────────────────────────────────────────────────────────────────┘');
  }

  console.log('');
  console.log('[Press Ctrl+C to exit]');
  console.log('');
}

// Update dashboard every 2 seconds
function startDashboard() {
  displayDashboard();

  const interval = setInterval(() => {
    displayDashboard();
  }, 2000);

  process.on('SIGINT', () => {
    clearInterval(interval);
    console.log('\n\nDashboard stopped.\n');
    process.exit(0);
  });
}

if (require.main === module) {
  startDashboard();
}

module.exports = { displayDashboard };
