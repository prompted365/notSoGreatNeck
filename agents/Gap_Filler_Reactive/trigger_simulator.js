#!/usr/bin/env node
/**
 * TRIGGER SIMULATOR
 * Simulates discoveries from Pillar_Scout for testing reactive processor
 */

const fs = require('fs');
const path = require('path');

const COORD_DIR = '/Users/breydentaylor/certainly/visualizations/coordination';
const LIVE_FEED = path.join(COORD_DIR, 'live_evidence_feed.json');

// Initialize live feed
function initializeFeed() {
  const feed = {
    created: new Date().toISOString(),
    last_updated: new Date().toISOString(),
    items: []
  };
  fs.writeFileSync(LIVE_FEED, JSON.stringify(feed, null, 2));
  console.log('Live feed initialized');
}

// Add item to feed
function addItemToFeed(item) {
  let feed = { items: [] };
  if (fs.existsSync(LIVE_FEED)) {
    feed = JSON.parse(fs.readFileSync(LIVE_FEED, 'utf8'));
  }

  item.discovered_at = new Date().toISOString();
  item.id = item.id || `item_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  feed.items.push(item);
  feed.last_updated = new Date().toISOString();

  fs.writeFileSync(LIVE_FEED, JSON.stringify(feed, null, 2));
  console.log(`[SIMULATOR] Added ${item.type}: ${item.id}`);
  return item.id;
}

// Simulate discoveries
function simulateDiscoveries() {
  console.log('\n=== TRIGGER SIMULATOR ===');
  console.log('Simulating Pillar_Scout discoveries...\n');

  initializeFeed();

  // Wait a bit before adding items
  setTimeout(() => {
    console.log('[1/4] Simulating victim report discovery...');
    addItemToFeed({
      type: 'victim_report',
      victim_name: 'John Doe',
      wallet_address: '0x7d8378d189831f25e184621a1cc026fc99f9c48c',
      amount_lost: 50000,
      claim: 'Promised EESystem healing, never received device',
      source: 'victim_interview_20251121'
    });
  }, 2000);

  setTimeout(() => {
    console.log('[2/4] Simulating court record discovery...');
    addItemToFeed({
      type: 'court_record',
      case_number: '25-cv-00123',
      case_name: 'Doe v. UNIFYD',
      amount: 125000,
      date_filed: '2025-01-15',
      claims: ['fraud', 'misrepresentation', 'breach_of_contract'],
      source: 'pacer_download_20251121'
    });
  }, 5000);

  setTimeout(() => {
    console.log('[3/4] Simulating video evidence discovery...');
    addItemToFeed({
      type: 'video_evidence',
      video_url: 'https://t.me/jasonyosefshurka/12345',
      title: 'EESystem Healing Claims',
      duration_seconds: 1200,
      claims: ['FDA_violation', 'cure_claims', 'testimonials'],
      posted_date: '2024-06-15',
      source: 'telegram_archive_20251121'
    });
  }, 8000);

  setTimeout(() => {
    console.log('[4/4] Simulating entity discovery...');
    addItemToFeed({
      type: 'entity',
      entity_name: 'Universal Wellness Solutions LLC',
      entity_type: 'corporation',
      state: 'Delaware',
      discovered_in: 'blockchain_analysis',
      related_wallets: ['0xabc123...'],
      source: 'corporate_records_search_20251121'
    });
  }, 11000);

  setTimeout(() => {
    console.log('\n[COMPLETE] All simulated discoveries added to feed');
    console.log('Reactive processor should have processed these items\n');
  }, 14000);
}

// Run simulation
if (require.main === module) {
  simulateDiscoveries();
}

module.exports = { addItemToFeed, simulateDiscoveries };
