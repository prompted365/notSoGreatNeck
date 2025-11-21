#!/usr/bin/env python3
"""
TIER_Auditor Phase 3 - Final Evidence Validation
Applies notebook discount (0.5x) and EESystem safeguards
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Paths
BASE_DIR = Path("/Users/breydentaylor/certainly/visualizations")
COORD_DIR = BASE_DIR / "coordination"
STATE_DIR = BASE_DIR / "state"

# Phase 3 Rules
NOTEBOOK_DISCOUNT = 0.5  # shadowLens sources count as 0.5x
TIER2_THRESHOLD = 3.0    # effective sources
TIER3_THRESHOLD = 2.0    # effective sources

def load_json(filepath: Path) -> Any:
    """Load JSON file safely"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {filepath}: {e}")
        return None

def save_json(data: Any, filepath: Path):
    """Save JSON with pretty formatting"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved: {filepath}")

def calculate_effective_sources(evidence: Dict) -> Dict:
    """
    Apply Phase 3 notebook discount calculation

    Returns: {
        'corpus_count': int,
        'notebook_count': int,
        'effective_sources': float,
        'calculation': str
    }
    """
    # Get source counts
    namespace = evidence.get('namespace', '')

    # shadowLens evidence is notebook source
    if namespace == 'evidence_shadowlens':
        # shadowLens is a notebook source itself
        notebook_count = 1

        # Check if it has backing from Phase 2 validation (corpus sources)
        validation = evidence.get('validation', {})
        corpus_sources = validation.get('corpus_sources', [])
        corpus_count = len(corpus_sources) if corpus_sources else 0

    elif namespace == 'evidence_blockchain':
        # Blockchain evidence from CSV corpus
        notebook_count = 0

        # Check if it has validation from Phase 2
        validation = evidence.get('validation', {})
        if validation:
            corpus_sources = validation.get('corpus_sources', [])
            corpus_count = len(corpus_sources) if corpus_sources else 0
        else:
            # Default: blockchain CSV is 1 corpus source, plus wallet attributions
            from_sources = evidence.get('from_wallet', {}).get('corpus_sources', [])
            to_sources = evidence.get('to_wallet', {}).get('corpus_sources', [])
            all_sources = set(from_sources + to_sources)

            # Add the blockchain CSV itself as a source
            source_file = evidence.get('source_file', '')
            if source_file:
                all_sources.add(source_file)

            corpus_count = len(all_sources)

    elif namespace == 'evidence_tier1':
        # Phase 2 validated evidence
        validation = evidence.get('validation', {})
        corpus_sources = validation.get('corpus_sources', [])
        corpus_count = len(corpus_sources) if corpus_sources else 0
        notebook_count = 0

    else:
        # Other evidence types
        corpus_sources = evidence.get('corpus_sources', [])
        corpus_count = len(corpus_sources) if corpus_sources else 0
        notebook_count = 0

    # Calculate effective sources with discount
    effective = corpus_count + (notebook_count * NOTEBOOK_DISCOUNT)

    return {
        'corpus_count': corpus_count,
        'notebook_count': notebook_count,
        'effective_sources': effective,
        'calculation': f"{corpus_count} corpus + ({notebook_count} × {NOTEBOOK_DISCOUNT}) = {effective}"
    }

def check_eesystem_safeguard(evidence: Dict) -> Dict:
    """
    Check if evidence violates EESystem safeguard

    Returns: {
        'violates': bool,
        'reason': str,
        'action': 'admit' | 'reject' | 'flag'
    }
    """
    # Convert evidence to string for searching
    evidence_str = json.dumps(evidence).lower()

    # Check for EESystem mentions
    eesystem_patterns = [
        r'\beesystem\b',
        r'\benergy enhancement system\b',
        r'\bdr\.?\s*sandra\s*rose\s*michael\b',
        r'\bmichael\s*scalar\b'
    ]

    has_eesystem = any(re.search(p, evidence_str, re.IGNORECASE) for p in eesystem_patterns)

    if not has_eesystem:
        return {'violates': False, 'reason': 'No EESystem mention', 'action': 'admit'}

    # Check context - is it about Jason's fraud or EESystem's legitimacy?
    tls_patterns = [
        r'\bthe light system\b',
        r'\btls\b',
        r'jason.*stole.*testimonial',
        r'jason.*used.*eesystem.*testimonial',
        r'fraudulently.*used.*eesystem'
    ]

    # Check if it's about Jason defrauding using EESystem's reputation
    jason_fraud_context = any(re.search(p, evidence_str, re.IGNORECASE) for p in tls_patterns)

    if jason_fraud_context:
        return {
            'violates': False,
            'reason': 'Shows Jason fraud using EESystem reputation (victim)',
            'action': 'admit'
        }

    # Check for direct critique of EESystem technology
    eesystem_fraud_patterns = [
        r'eesystem.*\b(fraud|scam|pseudoscience|fake)\b',
        r'\b(fraud|scam|pseudoscience|fake)\b.*eesystem',
        r'energy enhancement.*\b(fraud|scam|pseudoscience|fake)\b'
    ]

    eesystem_implicated = any(re.search(p, evidence_str, re.IGNORECASE) for p in eesystem_fraud_patterns)

    # BUT: Check for protective patterns (conflict, victim, used by Jason)
    protective_patterns = [
        r'conflict.*eesystem',
        r'eesystem.*conflict',
        r'jason.*defraud.*eesystem',
        r'eesystem.*victim',
        r'versus.*eesystem',
        r'unifyd.*eesystem.*conflict'
    ]

    is_protective = any(re.search(p, evidence_str, re.IGNORECASE) for p in protective_patterns)

    if eesystem_implicated and not is_protective:
        return {
            'violates': True,
            'reason': 'Implicates EESystem technology as fraud (legal safeguard violation)',
            'action': 'reject'
        }
    elif eesystem_implicated and is_protective:
        return {
            'violates': False,
            'reason': 'EESystem mentioned in fraud context but protective language present (conflict/victim)',
            'action': 'admit'
        }

    # Ambiguous case
    return {
        'violates': False,
        'reason': 'EESystem mentioned but context ambiguous',
        'action': 'flag'
    }

def validate_tier1_requirements(evidence: Dict) -> Dict:
    """
    Validate TIER 1 requirements (strictest)

    Returns: {
        'passes': bool,
        'actual_tier': int,
        'reason': str
    }
    """
    # TIER 1 requires either:
    # 1. tx_hash (blockchain) + 3+ corpus sources for wallet attribution
    # 2. temporal_anchor + subpoena_target + principals (shadowLens documentary)

    has_tx_hash = 'tx_hash' in evidence and evidence.get('tx_hash')
    metadata = evidence.get('metadata', {})
    has_temporal = metadata.get('temporal_anchor')
    has_subpoena = metadata.get('subpoena_target')
    has_principals = metadata.get('principals_exposed')

    # Blockchain path
    if has_tx_hash:
        sources = calculate_effective_sources(evidence)
        if sources['effective_sources'] >= 3.0:
            return {'passes': True, 'actual_tier': 1, 'reason': 'tx_hash + 3+ sources'}
        else:
            return {
                'passes': False,
                'actual_tier': 2,
                'reason': f"tx_hash present but only {sources['effective_sources']} effective sources (need 3.0)"
            }

    # shadowLens documentary path - requires NON-EMPTY values
    if has_temporal and has_subpoena and has_principals:
        # Check they're not empty strings
        temporal_valid = isinstance(has_temporal, str) and len(has_temporal.strip()) > 0
        subpoena_valid = isinstance(has_subpoena, str) and len(has_subpoena.strip()) > 0
        principals_valid = isinstance(has_principals, list) and len(has_principals) > 0

        if temporal_valid and subpoena_valid and principals_valid:
            return {
                'passes': True,
                'actual_tier': 1,
                'reason': f"Documentary proof: {has_temporal} / subpoena: {has_subpoena[:50]}..."
            }

    # Doesn't meet TIER 1
    return {
        'passes': False,
        'actual_tier': 2,
        'reason': 'Missing tx_hash OR (temporal_anchor + subpoena_target + principals)'
    }

def validate_tier2_requirements(evidence: Dict) -> Dict:
    """
    Validate TIER 2 requirements

    Returns: {
        'passes': bool,
        'actual_tier': int,
        'reason': str
    }
    """
    sources = calculate_effective_sources(evidence)

    if sources['effective_sources'] >= TIER2_THRESHOLD:
        return {
            'passes': True,
            'actual_tier': 2,
            'reason': f"{sources['calculation']} (≥3.0 threshold)"
        }
    elif sources['effective_sources'] >= TIER3_THRESHOLD:
        return {
            'passes': False,
            'actual_tier': 3,
            'reason': f"{sources['calculation']} (≥2.0 but <3.0, downgrade to TIER 3)"
        }
    else:
        return {
            'passes': False,
            'actual_tier': None,
            'reason': f"{sources['calculation']} (<2.0, insufficient backing)"
        }

def check_for_placeholders(evidence: Dict) -> List[str]:
    """Check for placeholder values that should reject evidence"""
    issues = []

    # Check for zero amounts (except legitimate zero-value txs)
    if 'amount_usd' in evidence:
        if evidence['amount_usd'] == 0 and evidence.get('amount_crypto', 0) != 0:
            issues.append("amount_usd=0 (placeholder)")

    # Check for unknown entities
    if 'entity' in evidence and evidence['entity'].lower() == 'unknown':
        issues.append("entity='unknown' (placeholder)")

    if 'from_wallet' in evidence:
        if evidence['from_wallet'].get('entity', '').lower() == 'unknown':
            if evidence['from_wallet'].get('attribution') == 'known':
                issues.append("from_wallet has 'known' attribution but 'unknown' entity")

    if 'to_wallet' in evidence:
        if evidence['to_wallet'].get('entity', '').lower() == 'unknown':
            if evidence['to_wallet'].get('attribution') == 'known':
                issues.append("to_wallet has 'known' attribution but 'unknown' entity")

    return issues

def audit_evidence(evidence: Dict, evidence_id: str) -> Dict:
    """
    Complete audit of single evidence piece

    Returns full audit record with admission decision
    """
    audit = {
        'evidence_id': evidence_id,
        'claimed_tier': evidence.get('tier'),
        'namespace': evidence.get('namespace'),
        'category': evidence.get('category'),
        'validation_checks': {}
    }

    # Check 1: EESystem safeguard
    eesystem_check = check_eesystem_safeguard(evidence)
    audit['validation_checks']['eesystem_safeguard'] = eesystem_check

    if eesystem_check['action'] == 'reject':
        audit['decision'] = 'REJECTED'
        audit['reason'] = eesystem_check['reason']
        audit['approved'] = False
        return audit

    # Check 2: Placeholders
    placeholder_issues = check_for_placeholders(evidence)
    audit['validation_checks']['placeholders'] = {
        'found': len(placeholder_issues) > 0,
        'issues': placeholder_issues
    }

    if placeholder_issues:
        audit['decision'] = 'REJECTED'
        audit['reason'] = f"Placeholder values: {', '.join(placeholder_issues)}"
        audit['approved'] = False
        return audit

    # Check 3: Source calculation
    sources = calculate_effective_sources(evidence)
    audit['validation_checks']['sources'] = sources

    # Check 4: TIER validation
    claimed_tier = evidence.get('tier')

    if claimed_tier == 1:
        tier1_check = validate_tier1_requirements(evidence)
        audit['validation_checks']['tier1'] = tier1_check

        if tier1_check['passes']:
            audit['decision'] = 'APPROVED'
            audit['actual_tier'] = 1
            audit['reason'] = tier1_check['reason']
            audit['approved'] = True
        else:
            # Failed TIER 1, check if it meets lower tier
            suggested_tier = tier1_check['actual_tier']

            if suggested_tier == 2:
                # Re-validate as TIER 2
                tier2_check = validate_tier2_requirements(evidence)
                audit['validation_checks']['tier2'] = tier2_check

                if tier2_check['passes']:
                    audit['decision'] = 'DOWNGRADED'
                    audit['actual_tier'] = 2
                    audit['reason'] = f"Claimed TIER 1, downgraded to TIER 2: {tier1_check['reason']}"
                    audit['approved'] = True
                elif tier2_check['actual_tier'] == 3:
                    audit['decision'] = 'DOWNGRADED'
                    audit['actual_tier'] = 3
                    audit['reason'] = f"Claimed TIER 1, downgraded to TIER 3: {tier2_check['reason']}"
                    audit['approved'] = True
                else:
                    audit['decision'] = 'FLAGGED'
                    audit['actual_tier'] = None
                    audit['reason'] = f"Claimed TIER 1, insufficient backing: {tier2_check['reason']}"
                    audit['approved'] = False
            else:
                # Suggested tier not recognized
                audit['decision'] = 'FLAGGED'
                audit['actual_tier'] = None
                audit['reason'] = tier1_check['reason']
                audit['approved'] = False

    elif claimed_tier == 2:
        tier2_check = validate_tier2_requirements(evidence)
        audit['validation_checks']['tier2'] = tier2_check

        if tier2_check['passes']:
            audit['decision'] = 'APPROVED'
            audit['actual_tier'] = 2
            audit['reason'] = tier2_check['reason']
            audit['approved'] = True
        elif tier2_check['actual_tier'] == 3:
            audit['decision'] = 'DOWNGRADED'
            audit['actual_tier'] = 3
            audit['reason'] = tier2_check['reason']
            audit['approved'] = True  # Still approved, just at lower tier
        else:
            audit['decision'] = 'FLAGGED'
            audit['actual_tier'] = None
            audit['reason'] = tier2_check['reason']
            audit['approved'] = False

    elif claimed_tier == 3:
        # TIER 3 accepted if >= 2.0 effective sources
        if sources['effective_sources'] >= TIER3_THRESHOLD:
            audit['decision'] = 'APPROVED'
            audit['actual_tier'] = 3
            audit['reason'] = f"TIER 3 confirmed: {sources['calculation']}"
            audit['approved'] = True
        else:
            audit['decision'] = 'FLAGGED'
            audit['actual_tier'] = None
            audit['reason'] = f"Below TIER 3 threshold: {sources['calculation']}"
            audit['approved'] = False
    else:
        audit['decision'] = 'FLAGGED'
        audit['reason'] = f"Unknown TIER: {claimed_tier}"
        audit['approved'] = False

    # Special flag for EESystem mentions that need review
    if eesystem_check['action'] == 'flag':
        audit['decision'] = 'FLAGGED_LEGAL_REVIEW'
        audit['legal_review_reason'] = eesystem_check['reason']
        audit['approved'] = False

    return audit

def main():
    """Execute Phase 3 TIER audit"""

    print("=" * 80)
    print("TIER_Auditor Phase 3 - Final Evidence Validation")
    print("=" * 80)
    print(f"Run ID: cert1-phase3-shadowlens-20251121")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()

    # Load all evidence sources
    print("Loading evidence files...")

    shadowlens = load_json(COORD_DIR / "shadowlens_evidence.json")
    blockchain = load_json(COORD_DIR / "blockchain_validated_evidence.json")
    validated = load_json(COORD_DIR / "validated_evidence.json")

    if not shadowlens:
        print("ERROR: Could not load shadowlens_evidence.json")
        return

    # Aggregate all evidence
    all_evidence = {}

    # shadowLens evidence (463 items - PRIORITY)
    if shadowlens and 'evidence_items' in shadowlens:
        print(f"✓ Loaded {len(shadowlens['evidence_items'])} shadowLens evidence items")
        all_evidence.update(shadowlens['evidence_items'])

    # Blockchain evidence (1,426 transactions)
    if blockchain and 'evidence_items' in blockchain:
        print(f"✓ Loaded {len(blockchain['evidence_items'])} blockchain evidence items")
        all_evidence.update(blockchain['evidence_items'])

    # Phase 2 validated evidence - has structure {admitted: {}, flagged: {}, rejected: {}}
    if validated:
        # Extract admitted and flagged evidence (both can be used)
        admitted = validated.get('admitted', {})
        flagged = validated.get('flagged', {})

        print(f"✓ Loaded Phase 2 validated evidence: {len(admitted)} admitted, {len(flagged)} flagged")

        # Add admitted evidence (already validated in Phase 2)
        if isinstance(admitted, dict):
            for eid, item in admitted.items():
                # Wrap in evidence_id if not present
                if 'evidence_id' not in item:
                    item['evidence_id'] = eid
                all_evidence[eid] = item

        # Add flagged evidence (will be re-evaluated with Phase 3 rules)
        if isinstance(flagged, dict):
            for eid, item in flagged.items():
                if 'evidence_id' not in item:
                    item['evidence_id'] = eid
                all_evidence[eid] = item

    print(f"\nTotal evidence to audit: {len(all_evidence)}")
    print()

    # Audit all evidence
    print("Auditing evidence...")
    print("-" * 80)

    audit_results = []
    approved_evidence = {}
    flagged_evidence = []
    rejected_evidence = []
    eesystem_violations = []

    tier_stats = {1: 0, 2: 0, 3: 0}
    decision_stats = {}

    for evidence_id, evidence in all_evidence.items():
        audit = audit_evidence(evidence, evidence_id)
        audit_results.append(audit)

        # Track decision
        decision = audit['decision']
        decision_stats[decision] = decision_stats.get(decision, 0) + 1

        # Route evidence based on decision
        if audit['approved']:
            approved_evidence[evidence_id] = {
                'evidence': evidence,
                'audit': {
                    'approved': True,
                    'tier': audit['actual_tier'],
                    'validation_notes': audit['reason'],
                    'sources': audit['validation_checks'].get('sources', {}),
                    'decision': decision
                }
            }
            tier_stats[audit['actual_tier']] = tier_stats.get(audit['actual_tier'], 0) + 1

        elif decision == 'FLAGGED' or decision == 'FLAGGED_LEGAL_REVIEW':
            flagged_evidence.append({
                'evidence_id': evidence_id,
                'reason': audit['reason'],
                'legal_review': decision == 'FLAGGED_LEGAL_REVIEW',
                'evidence': evidence
            })

        elif decision == 'REJECTED':
            rejected_evidence.append({
                'evidence_id': evidence_id,
                'reason': audit['reason'],
                'evidence': evidence
            })

            # Track EESystem violations
            if 'eesystem' in audit['reason'].lower():
                eesystem_violations.append({
                    'evidence_id': evidence_id,
                    'reason': audit['reason'],
                    'evidence_snippet': str(evidence)[:500]
                })

    # Generate summary
    print()
    print("=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"Total Evidence Audited: {len(all_evidence)}")
    print(f"  ✓ Approved: {len(approved_evidence)} ({len(approved_evidence)/len(all_evidence)*100:.1f}%)")
    print(f"  ⚠  Flagged: {len(flagged_evidence)} ({len(flagged_evidence)/len(all_evidence)*100:.1f}%)")
    print(f"  ✗ Rejected: {len(rejected_evidence)} ({len(rejected_evidence)/len(all_evidence)*100:.1f}%)")
    print()
    print("Approved Evidence by TIER:")
    print(f"  TIER 1: {tier_stats.get(1, 0)}")
    print(f"  TIER 2: {tier_stats.get(2, 0)}")
    print(f"  TIER 3: {tier_stats.get(3, 0)}")
    print()
    print("Decisions:")
    for decision, count in sorted(decision_stats.items()):
        print(f"  {decision}: {count}")
    print()
    print(f"EESystem Safeguard Violations: {len(eesystem_violations)}")
    print()

    # Save outputs
    print("Saving output files...")

    # 1. Approved evidence list
    save_json(approved_evidence, COORD_DIR / "approved_evidence_list.json")

    # 2. Full audit report
    audit_report = {
        'run_id': 'cert1-phase3-shadowlens-20251121',
        'audit_date': datetime.now(timezone.utc).isoformat(),
        'total_evidence': len(all_evidence),
        'validation_passed': len(approved_evidence),
        'validation_flagged': len(flagged_evidence),
        'validation_rejected': len(rejected_evidence),
        'tier_distribution': {
            'TIER_1': tier_stats.get(1, 0),
            'TIER_2': tier_stats.get(2, 0),
            'TIER_3': tier_stats.get(3, 0)
        },
        'decision_breakdown': decision_stats,
        'phase3_rules_applied': {
            'notebook_discount': NOTEBOOK_DISCOUNT,
            'tier2_threshold': TIER2_THRESHOLD,
            'tier3_threshold': TIER3_THRESHOLD
        },
        'flagged_items': flagged_evidence[:50],  # First 50 for report
        'rejected_items': rejected_evidence[:50],
        'eesystem_violations_count': len(eesystem_violations),
        'success_criteria': {
            'total_approved_150_plus': len(approved_evidence) >= 150,
            'all_tier1_valid': tier_stats.get(1, 0) > 0,
            'zero_placeholders': all(
                not audit.get('validation_checks', {}).get('placeholders', {}).get('found', False)
                for audit in audit_results if audit.get('approved')
            ),
            'eesystem_violations_zero': len(eesystem_violations) == 0
        }
    }

    save_json(audit_report, COORD_DIR / "evidence_audit_report.json")

    # 3. EESystem violations (always save, even if zero)
    save_json({
        'violation_count': len(eesystem_violations),
        'violations': eesystem_violations,
        'status': 'zero_violations' if len(eesystem_violations) == 0 else 'violations_found'
    }, COORD_DIR / "eesystem_safeguard_violations.json")

    # 4. Flagged for manual review
    save_json({
        'flagged_count': len(flagged_evidence),
        'flagged_items': flagged_evidence
    }, COORD_DIR / "flagged_for_manual_review.json")

    # 5. Update state
    state = {
        'run_id': 'cert1-phase3-shadowlens-20251121',
        'status': 'completed',
        'phase': 'HANDOFF',
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'evidence_audited': len(all_evidence),
        'evidence_approved': len(approved_evidence),
        'evidence_flagged': len(flagged_evidence),
        'evidence_rejected': len(rejected_evidence),
        'outputs': [
            'coordination/approved_evidence_list.json',
            'coordination/evidence_audit_report.json',
            'coordination/flagged_for_manual_review.json'
        ],
        'success_criteria_met': audit_report['success_criteria']
    }

    save_json(state, STATE_DIR / "tier_auditor.state.json")

    print()
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)

    # Check success criteria
    success = audit_report['success_criteria']
    if all(success.values()):
        print("✓ ALL SUCCESS CRITERIA MET")
    else:
        print("⚠ SOME SUCCESS CRITERIA NOT MET:")
        for criterion, met in success.items():
            status = "✓" if met else "✗"
            print(f"  {status} {criterion}: {met}")

    print()
    print(f"Next: ReasoningBank_Manager should read approved_evidence_list.json")
    print()

if __name__ == "__main__":
    main()
