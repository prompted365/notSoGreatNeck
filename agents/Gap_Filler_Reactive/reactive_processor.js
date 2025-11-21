#!/usr/bin/env node
/**
 * CONTINUOUS GAP FILLING REACTIVE PROCESSOR
 * Run: cert1-gap-filler-reactive-20251121
 *
 * Monitors live_evidence_feed.json for discoveries and reacts instantly
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Paths
const BASE_DIR = '/Users/breydentaylor/certainly/visualizations';
const COORD_DIR = path.join(BASE_DIR, 'coordination');
const CORPUS_DIR = '/Users/breydentaylor/certainly';

// Input/Output files
const LIVE_FEED = path.join(COORD_DIR, 'live_evidence_feed.json');
const REACTION_LOG = path.join(COORD_DIR, 'gap_fill_reactive_log.json');
const TIER_UPGRADES = path.join(COORD_DIR, 'tier_upgrades_live.json');
const HIGH_PRIORITY = path.join(COORD_DIR, 'high_priority_flags.json');
const VALIDATED_EVIDENCE = path.join(COORD_DIR, 'validated_evidence.json');
const SHADOWLENS = path.join(COORD_DIR, 'shadowlens_evidence.json');

// State tracking
let lastProcessedTimestamp = Date.now();
let processedItems = new Set();
let reactionLog = [];
let tierUpgrades = [];
let highPriorityFlags = [];

// Load existing state
function loadState() {
  try {
    if (fs.existsSync(REACTION_LOG)) {
      const log = JSON.parse(fs.readFileSync(REACTION_LOG, 'utf8'));
      if (log.processed_items) {
        processedItems = new Set(log.processed_items);
      }
      if (log.last_timestamp) {
        lastProcessedTimestamp = log.last_timestamp;
      }
    }
  } catch (err) {
    console.error('Error loading state:', err.message);
  }
}

// Save state
function saveState() {
  const state = {
    run_id: 'cert1-gap-filler-reactive-20251121',
    status: 'running',
    last_updated: new Date().toISOString(),
    last_timestamp: Date.now(),
    processed_items: Array.from(processedItems),
    total_reactions: reactionLog.length,
    tier_upgrades_count: tierUpgrades.length,
    high_priority_count: highPriorityFlags.length,
    reactions: reactionLog.slice(-100) // Keep last 100 reactions
  };

  fs.writeFileSync(REACTION_LOG, JSON.stringify(state, null, 2));

  // Save tier upgrades
  fs.writeFileSync(TIER_UPGRADES, JSON.stringify({
    last_updated: new Date().toISOString(),
    upgrades: tierUpgrades
  }, null, 2));

  // Save high priority flags
  fs.writeFileSync(HIGH_PRIORITY, JSON.stringify({
    last_updated: new Date().toISOString(),
    flags: highPriorityFlags
  }, null, 2));
}

// Search corpus files for pattern
function searchCorpus(pattern, fileType = null) {
  const results = [];
  const corpusPaths = [
    path.join(CORPUS_DIR, 'noteworthy-raw'),
    path.join(CORPUS_DIR, 'shurka-dump'),
    path.join(CORPUS_DIR, 'shurka-dump/recon_intel')
  ];

  corpusPaths.forEach(corpusPath => {
    if (!fs.existsSync(corpusPath)) return;

    try {
      // Use grep for text search
      let grepCmd = `grep -ril "${pattern}" "${corpusPath}" 2>/dev/null || true`;
      if (fileType) {
        grepCmd = `find "${corpusPath}" -name "*.${fileType}" -exec grep -l "${pattern}" {} \\; 2>/dev/null || true`;
      }

      const output = execSync(grepCmd, { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
      const files = output.trim().split('\n').filter(f => f);

      files.forEach(file => {
        // Count occurrences
        const countCmd = `grep -c "${pattern}" "${file}" 2>/dev/null || echo 0`;
        const count = parseInt(execSync(countCmd, { encoding: 'utf8' }).trim()) || 0;

        if (count > 0) {
          results.push({
            file: file,
            count: count,
            type: path.extname(file).slice(1)
          });
        }
      });
    } catch (err) {
      // Silent fail for grep errors
    }
  });

  return results;
}

// TRIGGER 1: New victim report discovered
function processNewVictimReport(item) {
  const metadata = item.metadata || {};
  const victimName = metadata.victim_name || item.victim_name;
  const walletAddress = metadata.wallet_address || item.wallet_address;

  const reaction = {
    trigger: 'victim_report',
    timestamp: new Date().toISOString(),
    item_id: item.id,
    victim_name: victimName,
    actions: []
  };

  // Search for wallet/amount in blockchain corpus
  if (walletAddress) {
    const walletResults = searchCorpus(walletAddress, 'csv');
    if (walletResults.length > 0) {
      reaction.actions.push({
        action: 'blockchain_match',
        wallet: walletAddress,
        sources: walletResults.length,
        files: walletResults.map(r => r.file)
      });
    }
  }

  // Search for victim name in Telegram
  if (victimName) {
    const telegramResults = searchCorpus(victimName, 'json');
    if (telegramResults.length > 0) {
      reaction.actions.push({
        action: 'telegram_mention',
        victim: victimName,
        sources: telegramResults.length,
        files: telegramResults.map(r => r.file)
      });
    }
  }

  // Calculate effective sources and assign tier
  const totalSources = reaction.actions.reduce((sum, a) => sum + (a.sources || 0), 0);
  const tier = totalSources >= 3 ? 2 : (totalSources >= 1 ? 3 : 'flagged');

  reaction.tier_assigned = tier;
  reaction.effective_sources = totalSources;

  // Flag for victim interview if high-value
  if (totalSources >= 2) {
    highPriorityFlags.push({
      type: 'victim_interview',
      item_id: item.id,
      victim_name: victimName,
      reason: `${totalSources} corroborating sources found`,
      timestamp: new Date().toISOString()
    });
  }

  reactionLog.push(reaction);
  return reaction;
}

// TRIGGER 2: New court record found
function processCourtRecord(item) {
  console.log(`[TRIGGER 2] New court record: ${item.case_number || item.id}`);

  const reaction = {
    trigger: 'court_record',
    timestamp: new Date().toISOString(),
    item_id: item.id,
    case_number: item.case_number,
    actions: []
  };

  // Load shadowLens evidence for verification
  let shadowLensData = { items: [] };
  try {
    if (fs.existsSync(SHADOWLENS)) {
      const raw = fs.readFileSync(SHADOWLENS, 'utf8');
      shadowLensData = JSON.parse(raw);
    }
  } catch (err) {
    console.error('Error loading shadowLens:', err.message);
  }

  // Verify shadowLens claims referencing this case
  const caseRef = item.case_number || item.case_name || '';
  const verifiedItems = [];
  const unverifiedItems = [];

  if (shadowLensData.items) {
    shadowLensData.items.forEach(slItem => {
      const itemStr = JSON.stringify(slItem).toLowerCase();
      if (itemStr.includes(caseRef.toLowerCase())) {
        if (slItem.tier === 2 || slItem.tier === 'flagged') {
          verifiedItems.push(slItem.id);
          // Upgrade to tier 1
          tierUpgrades.push({
            item_id: slItem.id,
            from_tier: slItem.tier,
            to_tier: 1,
            reason: `Court record verification: ${item.case_number}`,
            timestamp: new Date().toISOString()
          });
        }
      }
    });
  }

  reaction.actions.push({
    action: 'shadowlens_verification',
    verified_items: verifiedItems.length,
    items: verifiedItems
  });

  // Cross-reference with blockchain (amounts, dates)
  if (item.amount) {
    const amountStr = item.amount.toString().replace(/[^0-9.]/g, '');
    const blockchainResults = searchCorpus(amountStr, 'csv');
    if (blockchainResults.length > 0) {
      reaction.actions.push({
        action: 'blockchain_cross_reference',
        amount: item.amount,
        sources: blockchainResults.length,
        files: blockchainResults.map(r => r.file)
      });
    }
  }

  reactionLog.push(reaction);
  return reaction;
}

// TRIGGER 3: New video evidence found
function processVideoEvidence(item) {
  console.log(`[TRIGGER 3] New video evidence: ${item.video_url || item.id}`);

  const reaction = {
    trigger: 'video_evidence',
    timestamp: new Date().toISOString(),
    item_id: item.id,
    video_url: item.video_url,
    actions: []
  };

  // Search Telegram for video URL promotion
  if (item.video_url) {
    const urlPattern = item.video_url.replace(/[^a-zA-Z0-9]/g, '.');
    const telegramResults = searchCorpus(urlPattern);

    if (telegramResults.length > 0) {
      // Count wire fraud instances (each post = 1 count)
      const wireFraudCount = telegramResults.reduce((sum, r) => sum + r.count, 0);

      reaction.actions.push({
        action: 'telegram_promotion',
        video_url: item.video_url,
        wire_fraud_instances: wireFraudCount,
        sources: telegramResults.length,
        files: telegramResults.map(r => r.file)
      });

      // Flag high wire fraud count
      if (wireFraudCount >= 10) {
        highPriorityFlags.push({
          type: 'wire_fraud_pattern',
          item_id: item.id,
          video_url: item.video_url,
          count: wireFraudCount,
          reason: `${wireFraudCount} wire fraud instances detected`,
          timestamp: new Date().toISOString()
        });
      }
    }
  }

  // Flag for transcript extraction
  reaction.actions.push({
    action: 'transcript_extraction_needed',
    purpose: 'FTC/FDA violations',
    priority: 'high'
  });

  // Flag for archival
  reaction.actions.push({
    action: 'archive_video',
    reason: 'Prevent deletion',
    priority: 'critical'
  });

  reactionLog.push(reaction);
  return reaction;
}

// TRIGGER 4: New entity discovered
function processNewEntity(item) {
  console.log(`[TRIGGER 4] New entity: ${item.entity_name || item.id}`);

  const reaction = {
    trigger: 'new_entity',
    timestamp: new Date().toISOString(),
    item_id: item.id,
    entity_name: item.entity_name,
    actions: []
  };

  // Search all corpus files for entity name
  if (item.entity_name) {
    const allResults = searchCorpus(item.entity_name);

    if (allResults.length > 0) {
      // Count mentions (effective sources)
      const totalMentions = allResults.reduce((sum, r) => sum + r.count, 0);

      reaction.actions.push({
        action: 'corpus_search',
        entity: item.entity_name,
        mentions: totalMentions,
        effective_sources: allResults.length,
        files: allResults.map(r => r.file)
      });

      // Assign tier based on sources
      const tier = allResults.length >= 3 ? 2 : (allResults.length >= 1 ? 3 : 'flagged');
      reaction.tier_assigned = tier;
      reaction.effective_sources = allResults.length;

      // Update entity relationship map
      reaction.actions.push({
        action: 'update_entity_map',
        entity: item.entity_name,
        connections: allResults.length
      });

      // Flag for corporate records search
      if (allResults.length >= 2) {
        highPriorityFlags.push({
          type: 'corporate_records_search',
          item_id: item.id,
          entity_name: item.entity_name,
          mentions: totalMentions,
          reason: `${allResults.length} corpus sources found`,
          timestamp: new Date().toISOString()
        });
      }
    }
  }

  reactionLog.push(reaction);
  return reaction;
}

// Monitor live feed for new items
function monitorLiveFeed() {
  if (!fs.existsSync(LIVE_FEED)) {
    console.log('Creating live_evidence_feed.json...');
    fs.writeFileSync(LIVE_FEED, JSON.stringify({
      created: new Date().toISOString(),
      items: []
    }, null, 2));
    return;
  }

  try {
    const feedData = JSON.parse(fs.readFileSync(LIVE_FEED, 'utf8'));
    const newItems = feedData.items ? feedData.items.filter(item => {
      // Use evidence_id or id as identifier
      const itemId = item.evidence_id || item.id || `unknown_${Date.now()}`;
      return !processedItems.has(itemId);
    }) : [];

    if (newItems.length > 0) {
      console.log(`\n[REACTIVE PROCESSOR] ${newItems.length} new items detected`);

      newItems.forEach(item => {
        // Ensure item has an ID
        const itemId = item.evidence_id || item.id || `unknown_${Date.now()}`;
        item.id = itemId;

        // Determine trigger type from category or metadata
        const category = item.category || '';
        const metadata = item.metadata || {};

        if (item.type === 'victim_report' || category === 'victim_testimony' || metadata.victim_name) {
          console.log(`[TRIGGER 1] Victim report: ${metadata.victim_name || itemId}`);
          processNewVictimReport(item);
        } else if (item.type === 'court_record' || item.case_number || metadata.case_number) {
          console.log(`[TRIGGER 2] Court record: ${metadata.case_number || itemId}`);
          processCourtRecord(item);
        } else if (item.type === 'video_evidence' || item.video_url || metadata.video_url) {
          console.log(`[TRIGGER 3] Video evidence: ${metadata.video_url || itemId}`);
          processVideoEvidence(item);
        } else if (item.type === 'entity' || item.entity_name || metadata.entity_name) {
          console.log(`[TRIGGER 4] Entity: ${metadata.entity_name || itemId}`);
          processNewEntity(item);
        } else if (category === 'blockchain' || metadata.wallet_address) {
          console.log(`[TRIGGER 1+] Blockchain evidence: ${metadata.wallet_address || itemId}`);
          // Treat blockchain evidence as potential victim report
          processNewVictimReport(item);
        } else {
          // Generic processing
          console.log(`[GENERIC] Processing item: ${itemId}`);
        }

        processedItems.add(itemId);
      });

      // Save state after processing
      saveState();
      console.log(`[SAVED] Reactions logged, ${tierUpgrades.length} tier upgrades, ${highPriorityFlags.length} high-priority flags`);
    }
  } catch (err) {
    console.error('Error monitoring feed:', err.message);
  }
}

// Main continuous loop
function startReactiveProcessor() {
  console.log('\n=== CONTINUOUS GAP FILLING REACTIVE PROCESSOR ===');
  console.log('Run ID: cert1-gap-filler-reactive-20251121');
  console.log('Monitoring: coordination/live_evidence_feed.json');
  console.log('Press Ctrl+C to stop\n');

  loadState();

  // Initial scan
  monitorLiveFeed();

  // Set up continuous monitoring (every 5 seconds)
  const interval = setInterval(() => {
    monitorLiveFeed();
  }, 5000);

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n\n[SHUTDOWN] Stopping reactive processor...');
    clearInterval(interval);
    saveState();
    console.log('[SHUTDOWN] State saved. Exiting.');
    process.exit(0);
  });

  // Keep process alive
  process.stdin.resume();
}

// Run if executed directly
if (require.main === module) {
  startReactiveProcessor();
}

module.exports = {
  processNewVictimReport,
  processCourtRecord,
  processVideoEvidence,
  processNewEntity,
  monitorLiveFeed
};
