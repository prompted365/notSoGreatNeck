# AGENT: Corpus_Validator

**Role**: Evidence Re-Classification Specialist (Types 1-10, Tiers 1-5)
**Wave**: 4.1 (First agent in Phase 4)
**Run ID**: cert1-phase4-autonomous-20251121

---

## WHY THIS MATTERS

Phase 3 produced 817 evidence items with **critical misrepresentations**:
- Blockchain attributed to "Jason Shurka" based on investigator assumption, not KYC
- shadowLens items claimed "documentary proof" but are NotebookLM summaries (not verified docs)
- URL count inflated (685 Telegram message IDs counted as separate "fraud URLs")
- TIER system mixed certainty levels (what we have vs. what we can prove)

**Your mission**: Re-classify ALL 817 items using the corrected Evidence Types 1-10 + Proof Tiers 1-5 system, separating transaction certainty from attribution uncertainty.

**Downstream impact**: Everything depends on you getting this right. TIER_Auditor, Gap_Filler, Subpoena_Coordinator all work from YOUR classifications.

---

## INPUTS

**Primary**:
- `/Users/breydentaylor/certainly/visualizations/coordination/approved_evidence_list.json` (817 Phase 3 items)

**Reference**:
- `/Users/breydentaylor/certainly/visualizations/PHASE3_DEFENSIVE_METRICS_AUDIT.md` (corrections to apply)
- `/Users/breydentaylor/certainly/visualizations/CONTEXT-CERT1.md` (Type/Tier definitions)
- `/Users/breydentaylor/certainly/visualizations/LEGAL_SAFEGUARDS.md` (EESystem protection)

---

## OUTPUTS

**Required**:
1. `coordination/phase3_revalidated_evidence.json` (817 items re-classified)
2. `coordination/corpus_validator_report.json` (summary stats)
3. `state/corpus_validator.state.json` (completion status)

---

## EVIDENCE TYPES (1-10) - WHAT Kind of Evidence

### Type 1: Government Records
**Examples**: Court filings, SEC documents, corporate registrations (Secretary of State)
**Certainty**: Highest (if verified from source)
**Phase 3 candidates**: shadowLens items pointing to court docs, corporate filings

### Type 2: Authenticated Documents
**Examples**: Contracts, bank statements, deeds, tax returns (with chain of custody)
**Certainty**: High (if authenticated)
**Phase 3 candidates**: shadowLens items pointing to contracts/agreements

### Type 3: Blockchain Transactions (Attribution Known)
**Examples**: On-chain transactions where wallet owner is proven via KYC or court records
**Certainty**: Transaction = cryptographic, Attribution = requires proof
**Phase 3 candidates**: ZERO (no KYC records exist yet)

### Type 9: Blockchain Transactions (Attribution Needed)
**Examples**: On-chain transactions where wallet owner is suspected but not proven
**Certainty**: Transaction = cryptographic, Attribution = pending subpoena
**Phase 3 candidates**: ALL 724 blockchain items (move from Type 3 to Type 9)

### Type 10: AI/LLM Analysis
**Examples**: NotebookLM summaries, shadowLens Notes, AI-generated reports
**Certainty**: Depends on underlying source documents (currently unverified)
**Phase 3 candidates**: ALL 47 shadowLens items

### Type 4: Multi-Source OSINT
**Examples**: Claims corroborated by 3+ independent public sources
**Phase 3 candidates**: URL patterns if backed by multiple platforms

### Type 5: Pattern Evidence
**Examples**: Documented patterns across corpus (fraud campaign, systematic behavior)
**Phase 3 candidates**: URL fraud patterns (15-20 domains across 9,831 posts)

### Type 6: Single-Source Leads
**Examples**: HUMINT, single OSINT source, tips, single document
**Phase 3 candidates**: Individual Telegram posts, single URL mentions

### Type 7: Inference
**Examples**: AI analysis, statistical inference, network analysis
**Phase 3 candidates**: Entity co-mention relationships

### Type 8: Derivative
**Examples**: Conclusions built from Types 1-7
**Phase 3 candidates**: RICO predicate conclusions

---

## PROOF TIERS (1-5) - HOW DEFENSIBLE for Prosecution

### Tier 1: Certificate and Charge (Ready NOW)
**Requirements**:
- Type 1 with verified source document, OR
- Type 3 with KYC-proven attribution, OR
- Type 2 with authenticated chain of custody

**Phase 3 candidates**: ZERO shadowLens items (all pending subpoena verification)

### Tier 2: One Subpoena Away
**Requirements**:
- Strong evidence needing ONE verification step
- shadowLens items (pending document retrieval)
- Blockchain Type 9 (pending exchange KYC)
- Type 4 OSINT (pending one additional source)

**Phase 3 candidates**:
- ALL 47 shadowLens items → Tier 2 (pending subpoena)
- ALL 724 blockchain items → Tier 2 (pending KYC)

### Tier 3: Investigative Development
**Requirements**:
- Needs more work, corroboration, or analysis
- 2.0+ effective sources (with notebook discount)

### Tier 4: Long-Shot / Low-Priority
**Requirements**:
- Weak leads, low expected yield

### Tier 5: Ruled Out
**Requirements**:
- Abandoned theories, disproven claims

---

## YOUR TASKS (Granular)

### Task 1: Load Phase 3 Evidence (5 min)

```python
import json

with open('coordination/approved_evidence_list.json', 'r') as f:
    phase3_evidence = json.load(f)

print(f"Loaded {len(phase3_evidence)} Phase 3 evidence items")
```

### Task 2: Re-Classify Blockchain Evidence (30 min)

For each blockchain item in Phase 3:

**OLD (Phase 3 - WRONG)**:
```json
{
  "evidence_id": "TIER2-BTC-0397",
  "tier": 2,
  "category": "blockchain",
  "from_wallet": {
    "entity": "Jason Shurka / UNIFYD",
    "corpus_sources": ["mission_context"]
  }
}
```

**NEW (Phase 4 - CORRECT)**:
```json
{
  "evidence_id": "BTC-0397",
  "type": 9,  // Attribution needed
  "tier": 2,  // One subpoena away (exchange KYC)
  "category": "blockchain_transaction",
  "transaction": {
    "tx_hash": "0x2e75985...",
    "amount_usd": 7000000.0,
    "certainty": "cryptographic",  // ALWAYS certain
    "chain": "ETH",
    "timestamp": "2021-10-30 14:41:40"
  },
  "attribution": {
    "from_wallet": "0x66b870...",
    "suspected_entity": "Jason Shurka / UNIFYD",
    "basis": "Correlation with UNIFYD bank records (mission briefing)",
    "certainty": "pending_subpoena",  // NOT certain
    "evidence_basis": "investigator_assumption",  // Honest label
    "subpoena_target": "Coinbase (KYC for wallet 0x66b870...)",
    "tier_if_confirmed": 1  // Would become Tier 1 if KYC proves ownership
  },
  "rico_value": {
    "org_benefit_theory": true,
    "explanation": "Under RICO, enterprise liability attaches if wallet clustering or KYC demonstrates benefit to UNIFYD/Jason enterprise, regardless of personal ownership"
  },
  "source_file": "fund_transactions_10k^1_export-0x66b870ddf78c975af5cd8edc6de25eca81791de1.csv",
  "source_line": 1578
}
```

**Apply to ALL 724 blockchain items**.

### Task 3: Re-Classify shadowLens Evidence (20 min)

For each shadowLens item:

**OLD (Phase 3 - WRONG)**:
```json
{
  "evidence_id": "shadowlens_RICO_Patterns_Dossier_0_1",
  "tier": 1,  // WRONG - claimed documentary proof
  "category": "documentary",
  "metadata": {
    "temporal_anchor": "Jan 18, 2002",
    "evidence_act": "Creditor-Proof Agreement"
  }
}
```

**NEW (Phase 4 - CORRECT)**:
```json
{
  "evidence_id": "shadowlens_RICO_Patterns_Dossier_0_1",
  "type": 10,  // AI analysis (NotebookLM summary)
  "tier": 2,   // One subpoena away (document retrieval)
  "category": "notebooklm_summary",
  "metadata": {
    "temporal_anchor": "Jan 18, 2002",
    "evidence_act": "Creditor-Proof Agreement",
    "subpoena_target": "Nassau County Clerk/Surrogate's Court",
    "principals_exposed": ["Manny Shurka", "Malka Shurka", "Efraim Shurka", "Esther Zernitsky"]
  },
  "audit": {
    "sources": {
      "corpus_count": 0,
      "notebook_count": 1,
      "effective_sources": 0.5  // Notebook discount
    },
    "decision": "APPROVED (Tier 2 - Pending Subpoena)",
    "caveat": "NotebookLM summary only - NOT verified documentary proof. If subpoena retrieves document matching summary, upgrade to Type 1/Tier 1. If document doesn't match or doesn't exist, evidence collapses."
  },
  "tier_if_confirmed": 1,  // Becomes Tier 1 if subpoena confirms
  "source_file": "shadowLens/Notes/RICO_Patterns_Dossier.html",
  "source_section": "Table 1, Row 2"
}
```

**Apply to ALL 47 shadowLens items**.

### Task 4: Re-Classify URL Evidence (15 min)

**OLD (Phase 3 - WRONG)**:
> "1,000 TLS fraud URLs classified. Top domain: t.me (685 instances)"

**NEW (Phase 4 - CORRECT)**:
```json
{
  "evidence_id": "URL-PATTERN-001",
  "type": 5,  // Pattern evidence
  "tier": 3,  // Needs legal review of specific posts
  "category": "fraud_pattern",
  "pattern": {
    "description": "Jason Shurka systematically promotes TLS across 15-20 fraud domains in 9,831 Telegram posts",
    "instances": {
      "total_posts": 9831,
      "unique_domains": 20,
      "primary_domains": [
        "thelightsystems.com (35 mentions)",
        "jasonshurka.com (27 mentions)",
        "tlsmarketplace.shop (14 mentions)",
        "unifydhealing.com (41 mentions)"
      ],
      "platforms": {
        "telegram_channel": "t.me/jasonyosefshurka (9,831 posts)",
        "youtube": "103 unique videos",
        "instagram": "@unifydhealing (24 mentions)"
      }
    },
    "fraud_indicators": {
      "medical_claims": true,
      "pricing": true,
      "call_to_action": true
    }
  },
  "caveat": "Automated keyword analysis - requires manual legal review to confirm fraudulent intent, absence of disclaimers, FTC/FDA violations",
  "tier_if_confirmed": 2,  // After legal review
  "source_file": "coordination/url_classifications.csv"
}
```

**Create ONE pattern evidence item** (not 1,000 separate URLs).

### Task 5: Generate Summary Report (10 min)

```json
{
  "run_id": "cert1-phase4-autonomous-20251121",
  "agent": "Corpus_Validator",
  "status": "completed",
  "timestamp": "2025-11-21T06:30:00Z",
  "input": {
    "phase3_items": 817,
    "phase3_breakdown": {
      "tier1": 44,
      "tier2": 13,
      "tier3": 760
    }
  },
  "output": {
    "revalidated_items": 817,
    "type_breakdown": {
      "type1": 0,  // No verified government records yet
      "type2": 0,  // No authenticated docs yet
      "type3": 0,  // No blockchain with proven attribution
      "type9": 724,  // Blockchain with pending attribution
      "type10": 47,  // NotebookLM summaries
      "type5": 1,  // URL pattern evidence
      "other": 45  // Other types
    },
    "tier_breakdown": {
      "tier1": 0,  // Nothing prosecution-ready without subpoenas
      "tier2": 771,  // 724 blockchain + 47 shadowLens (one subpoena away)
      "tier3": 46  // Remaining items
    }
  },
  "key_corrections": {
    "blockchain": "724 items downgraded from 'attributed' to 'pending attribution' (Type 9, Tier 2)",
    "shadowlens": "47 items corrected from 'documentary proof' to 'NotebookLM summaries' (Type 10, Tier 2)",
    "urls": "Consolidated 685 Telegram message IDs into 1 pattern evidence item (Type 5, Tier 3)"
  },
  "subpoena_priorities": {
    "exchange_kyc": "724 blockchain items → Tier 1 if confirmed",
    "nassau_county_clerk": "47 shadowLens items → Tier 1 if documents match summaries"
  }
}
```

### Task 6: Update State File (2 min)

```json
{
  "run_id": "cert1-phase4-autonomous-20251121",
  "agent": "corpus_validator",
  "status": "completed",
  "started_at": "2025-11-21T06:00:00Z",
  "completed_at": "2025-11-21T06:30:00Z",
  "outputs": [
    "coordination/phase3_revalidated_evidence.json",
    "coordination/corpus_validator_report.json"
  ],
  "metrics": {
    "items_processed": 817,
    "type_corrections": 772,
    "tier_corrections": 44
  }
}
```

---

## CRITICAL RULES

### 1. **NEVER Claim Attribution Without KYC**

❌ WRONG:
```json
{"entity": "Jason Shurka", "attribution": "known"}
```

✅ CORRECT:
```json
{
  "suspected_entity": "Jason Shurka / UNIFYD",
  "certainty": "pending_subpoena",
  "basis": "Correlation with bank records",
  "subpoena_target": "Coinbase KYC"
}
```

### 2. **NEVER Claim Documentary Proof for NotebookLM**

❌ WRONG:
```json
{"tier": 1, "category": "documentary"}
```

✅ CORRECT:
```json
{
  "type": 10,
  "tier": 2,
  "category": "notebooklm_summary",
  "caveat": "Pending subpoena verification"
}
```

### 3. **ALWAYS Separate Transaction from Attribution**

✅ CORRECT:
```json
{
  "transaction": {"certainty": "cryptographic"},
  "attribution": {"certainty": "pending_subpoena"}
}
```

### 4. **ALWAYS Apply Notebook Source Discount**

```python
effective_sources = corpus_sources + (notebook_sources * 0.5)
```

shadowLens items: `corpus_sources: 0, notebook_sources: 1 → effective_sources: 0.5`

---

## TEAM BEHAVIOR

**Upstream Dependencies**: NONE (you run first)

**Downstream Consumers**:
- **Gap_Filler**: Will process flagged items based on YOUR tier assignments
- **Subpoena_Coordinator**: Will prioritize targets based on YOUR `tier_if_confirmed` values
- **TIER_Auditor**: Will validate YOUR classifications in future phases

**If You Fail**: Everything downstream gets wrong classifications → prosecution package is unreliable

**Success Criteria**:
- ✅ ALL 817 items re-classified with Type 1-10
- ✅ ALL 817 items re-tiered with Tier 1-5
- ✅ Blockchain items separated (transaction certainty vs attribution uncertainty)
- ✅ shadowLens items marked as "NotebookLM summaries, pending subpoena"
- ✅ URL evidence consolidated into pattern (not 1,000 separate items)
- ✅ State file updated to "completed"

---

**Begin now. Read Phase 3 evidence, apply corrections, output revalidated evidence. You have 90 minutes for this task.**
