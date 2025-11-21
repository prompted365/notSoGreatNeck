# Phase 3 Swarm Lineup - UPDATED for shadowLens Integration

**Run ID**: cert1-phase3-shadowlens-20251121
**Orchestrator**: Cert1
**Mission**: Extract prosecution-grade evidence from 817MB shadowLens NotebookLM treasure + expand to 150+ admitted items

---

## New Intelligence: shadowLens Discovery

### What We Found:
- **659 files in shadowLens** (NotebookLM "Granular Prosecution Assembly Engine")
  - 29 HTML Notes (RICO dossiers with temporal anchors, subpoena targets)
  - 322 HTML Sources (court docs, research, intelligence reports)
  - 12 MP4 Artifacts (NotebookLM audio overviews)
  - 315 JSON metadata files

### Key Evidence in shadowLens:
1. **Efraim Shurka 1993 felony conviction** (Tax Evasion predicate)
2. **Jan 18, 2002 "Creditor-Proof" Agreement** (SMOKING GUN - conspiracy to defraud)
3. **Oct 31, 2003: Jason Shurka property fraud** (6-year-old listed as $6.125M cash buyer)
4. **Nov 14, 2024: War Call Recording** (Hobbs Act Extortion - Jason demanding $10-15M)
5. **77-Entity Network Structure** (Mamon, Shekel, Zahav, Zohar LLCs)
6. **$37K PDI Round-Tripping** (Money Laundering, Sept 2011)
7. **$1.38M Lukoil Judgment Evasion** (13 years, 2012-2025)

### Entity Network Confirmation:
- ✅ **Jason Shurka**: Node #2, 6,456 mentions, 2.37% degree centrality
- ✅ **UNIFYD**: Node #5, 944 mentions
- ⚠️  Talia Havakok NOT in top 10 (needs extraction from shadowLens)
- ⚠️  Esther Zernitsky NOT in top 10 (in shadowLens Notes)

---

## Updated Swarm Lineup (9 Agents)

### NEW AGENT: shadowLens_Analyst (HIGHEST PRIORITY)

**Purpose**: Extract evidence from NotebookLM prosecution dossiers
**Input**:
- `/Users/breydentaylor/certainly/shurka-dump/shadowLens/Notes/*.html` (29 files)
- `/Users/breydentaylor/certainly/shurka-dump/shadowLens/Sources/*.html` (322 files)
- `/Users/breydentaylor/certainly/shurka-dump/shadowLens/Artifacts/*.mp4` (12 files - audio transcripts)

**Tasks**:
1. Parse HTML notes for structured evidence (temporal anchors, principals, subpoena targets)
2. Extract entity mentions: Esther Zernitsky, Talia Havakok, Efraim Shurka, Manny Shurka
3. Map RICO predicates: Tax Evasion, Mail/Wire Fraud, Money Laundering, Hobbs Act Extortion
4. Cross-reference with corpus (validate NotebookLM claims against raw files)
5. Generate evidence items with:
   - `source_file`: shadowLens/Notes/{{filename}}.html
   - `source_section`: Table row or heading
   - `temporal_anchor`: Date of act
   - `subpoena_target`: Court/agency to request docs
   - `principals_exposed`: List of entities involved

**Output**: `shadowlens_evidence.json` (target: 80+ TIER 1-2 evidence pieces)

**Why Critical**: shadowLens contains **prosecution-grade structured evidence** with dates, dollar amounts, principals - higher quality than Telegram posts or blockchain tx alone

---

### Updated First-Wave Agents (Parallel Execution):

#### 1. **shadowLens_Analyst** (NEW - HIGHEST PRIORITY)
See above

#### 2. **Blockchain_Forensics** (HIGH PRIORITY - UPDATED)
**Changes from Phase 2**:
- MUST extract `amount_usd` with actual dollar values (not 0)
- Add shadowLens cross-reference: Check if wallet addresses mentioned in Notes
- Target: 50+ NEW blockchain evidence

#### 3. **Fraud_Scorer** (HIGH PRIORITY)
**Changes from Phase 2**:
- Cross-reference top 100 Telegram posts with shadowLens mentions
- If Jason Shurka post mentioned in shadowLens Notes: AUTO-UPGRADE to TIER 2
- Target: 80+ wire fraud evidence

#### 4. **URL_Analyst** (MEDIUM PRIORITY)
**Changes from Phase 2**:
- Extract URLs from shadowLens HTML sources
- Cross-reference with Telegram URL corpus
- Target: 50+ URL evidence

#### 5. **Entity_Linker** (MEDIUM PRIORITY - UPDATED)
**Changes from Phase 2**:
- **PRIORITY ENTITIES**: Esther Zernitsky, Talia Havakok, Efraim Shurka, Manny Shurka (from shadowLens)
- Build co-mention graph: Jason + Esther, Jason + Manny, Jason + Talia
- Validate against corpus + shadowLens
- Target: 100+ entity network nodes

#### 6. **Binder_Chunker** (LOW PRIORITY - keep as-is)
No changes

---

### Updated Second-Wave Agents:

#### 7. **TIER_Auditor** (UPDATED - 2-source threshold with downgrade)
**Changes from Phase 2**:
- **NEW RULE**: 2 corpus sources = ADMIT but DOWNGRADE TIER 2 → TIER 3
  - Reason: "Only 2 sources - needs corroboration for TIER 2"
- **Maintained**: 3+ sources = TIER 2 (no downgrade)
- **Maintained**: tx_hash + 3+ sources = TIER 1 (blockchain)
- **Maintained**: shadowLens temporal anchor + 3+ sources = TIER 1 (documentary)
- **Zero tolerance**: Reject placeholders (amount_usd=0, entity="unknown")

**Expected Outcome**: 74 flagged items → 40-50 admitted as TIER 3, 20-30 remain flagged

#### 8. **ReasoningBank_Manager** (UPDATED)
**Changes from Phase 2**:
- Load shadowLens evidence into new namespace: `evidence_shadowlens`
- Cross-reference: Link shadowLens items to blockchain/Telegram evidence
- Verify: Every item has `corpus_sources` OR `shadowlens_source`

#### 9. **Dashboard_Coordinator** (keep as-is)
No changes

---

## Updated Success Criteria

### Quantitative (Revised Targets):
- ✅ **150+ admitted evidence** (31 existing + 80 shadowLens + 40 from flagged 2-source)
- ✅ TIER 1: **80+ pieces** (50 blockchain + 30 shadowLens documentary)
- ✅ TIER 2: 80+ pieces (Telegram + entities with 3+ sources)
- ✅ TIER 3: 50+ pieces (2-source threshold admits)
- ✅ Wire fraud: 3,000+ communications
- ✅ **Esther Zernitsky, Talia Havakok validated** (shadowLens extraction)
- ✅ **$6.125M Jason Shurka property fraud documented** (shadowLens)
- ✅ **War Call Recording catalogued** (Hobbs Act Extortion evidence)

### Qualitative (Enhanced):
- ✅ All shadowLens evidence has `temporal_anchor` (date of act)
- ✅ All shadowLens evidence has `subpoena_target` (court/agency)
- ✅ All shadowLens evidence has `principals_exposed` (entities involved)
- ✅ Cross-references: shadowLens ↔ blockchain ↔ Telegram ↔ entities
- ✅ RICO predicate mapping: **Tax Evasion** (new), Mail/Wire Fraud, Money Laundering, Hobbs Act Extortion (new)

---

## Updated Coordination Protocol

### Agent Priority Order:
1. **shadowLens_Analyst** (run FIRST, solo) → generates `shadowlens_evidence.json`
2. **Wait for shadowLens completion**, then spawn 5 first-wave agents in parallel:
   - Blockchain_Forensics, Fraud_Scorer, URL_Analyst, Entity_Linker, Binder_Chunker
3. **Wait for all first-wave**, then spawn second-wave sequential:
   - TIER_Auditor → ReasoningBank_Manager → Dashboard_Coordinator

### State Files:
- `state/shadowlens_analyst.state.json` (new)
- All existing state files updated with shadowLens cross-reference logic

### Coordination Files:
- `coordination/shadowlens_evidence.json` (shadowLens_Analyst output)
- `coordination/approved_evidence_list.json` (TIER_Auditor output - now includes 2-source TIER 3 admits)
- `coordination/entity_priority_list.json` (Esther, Talia, Efraim, Manny)

---

## Risk Mitigation Updates

### Risk 1: MP4 files cannot be processed
**Mitigation**: shadowLens_Analyst focuses on HTML Notes first (primary evidence). MP4 audio transcripts are secondary (skip if cannot process).

### Risk 2: shadowLens evidence duplicates existing corpus
**Mitigation**: TIER_Auditor de-duplicates by checking if evidence already admitted. shadowLens acts as **additional corpus source** (enhances existing evidence).

### Risk 3: 2-source threshold floods with low-quality admits
**Mitigation**: TIER 3 designation signals "needs corroboration". Dashboard shows TIER 3 separately. Prosecutors review TIER 3 with caution.

---

## The Updated Mission

> **The Pyramid's Shadow meets Shadow Lens.**

Jason Shurka's narratives and layers (Pyramid's Shadow) are now exposed through the NotebookLM Granular Prosecution Assembly Engine (Shadow Lens).

**Every temporal anchor = timeline proof**
**Every subpoena target = discovery path**
**Every principal exposed = conspiracy node**

817MB of NotebookLM treasure + 5.7GB corpus = prosecution-grade RICO case.

Make it irrefutable. Make it prosecution-ready. Bring them to justice.

---

**— Cert1, Orchestrator, Shurka Enterprise Investigation**
**Phase**: Phase 3 Swarm Lineup Updated
**Status**: Ready to fork agent prompts and deploy
**Next**: Archive Phase 2 prompts, create Phase 3 versions with shadowLens integration
