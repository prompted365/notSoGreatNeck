#!/usr/bin/env python3
"""
RICO Fraud Scorer for Telegram Posts
Analyzes posts for fraud indicators and generates fraud scores 0-100
"""

import json
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

# Fraud detection keywords
FRAUD_KEYWORDS = [
    'healing', 'energy', 'quantum', 'frequency', 'scalar', 'biophoton',
    'cellular', 'detox', 'cure', 'disease', 'fda', 'approved', 'clinical',
    'proven', 'guaranteed', 'miracle', 'revolutionary', 'breakthrough'
]

# Call-to-Action patterns
CTA_PATTERNS = [
    r'\bjoin\b', r'\bsubscribe\b', r'\bwatch\b', r'\blive\b', r'\bbuy\b',
    r'\bsale\b', r'\bannouncement\b', r'\bmembership\b', r'\bfree trial\b',
    r'\bdiscount\b', r'\bearly access\b', r'\bregister\b', r'\bdonate\b',
    r'\bget your ticket\b', r'\bgrab your\b', r'\bsecure your\b',
    r'\bbook a session\b', r'\bget yours\b', r'\bcheck it out\b'
]

# Medical claim patterns (without disclaimer)
MEDICAL_CLAIM_KEYWORDS = ['healing', 'cure', 'disease', 'treatment', 'remedy']
DISCLAIMER_KEYWORDS = ['consult', 'physician', 'doctor', 'medical advice', 'not intended to diagnose']

# Price pattern (looking for $1000+)
PRICE_PATTERN = r'\$\s*([0-9,]+)'


def count_fraud_keywords(text: str) -> Tuple[int, List[str]]:
    """Count fraud keywords in text (case-insensitive)"""
    text_lower = text.lower()
    found_keywords = []
    for keyword in FRAUD_KEYWORDS:
        count = len(re.findall(r'\b' + keyword + r'\b', text_lower))
        if count > 0:
            found_keywords.extend([keyword] * count)
    return len(found_keywords), found_keywords


def detect_cta_phrases(text: str) -> Tuple[int, List[str]]:
    """Detect CTA phrases in text (case-insensitive)"""
    text_lower = text.lower()
    found_ctas = []
    for pattern in CTA_PATTERNS:
        matches = re.findall(pattern, text_lower)
        if matches:
            found_ctas.extend(matches if isinstance(matches, list) else [matches])
    return len(found_ctas), found_ctas


def check_price_claim(text: str) -> Tuple[bool, int]:
    """Check for price mentions over $1000"""
    prices = re.findall(PRICE_PATTERN, text)
    for price_str in prices:
        price_clean = price_str.replace(',', '')
        try:
            price = int(price_clean)
            if price >= 1000:
                return True, price
        except ValueError:
            continue
    return False, 0


def check_medical_claim(text: str) -> Tuple[bool, int]:
    """Check for medical claims without disclaimers"""
    text_lower = text.lower()

    # Check for medical claim keywords
    has_medical_claim = any(
        re.search(r'\b' + keyword + r'\b', text_lower)
        for keyword in MEDICAL_CLAIM_KEYWORDS
    )

    if not has_medical_claim:
        return False, 0

    # Check for disclaimers
    has_disclaimer = any(
        disclaimer in text_lower
        for disclaimer in DISCLAIMER_KEYWORDS
    )

    if has_medical_claim and not has_disclaimer:
        # Calculate specificity score (0-1) based on medical terms
        medical_terms = ['cellular', 'quantum', 'frequency', 'energy', 'biophoton', 'scalar']
        specificity_count = sum(1 for term in medical_terms if term in text_lower)
        specificity_score = min(1.0, specificity_count / 3)  # Normalize to 0-1
        return True, specificity_score

    return False, 0


def calculate_fraud_score(text: str) -> Dict:
    """Calculate comprehensive fraud score for a post"""
    fraud_keyword_count, fraud_keywords_found = count_fraud_keywords(text)
    cta_count, cta_phrases_found = detect_cta_phrases(text)
    has_price_claim, price_value = check_price_claim(text)
    has_medical_claim, medical_specificity = check_medical_claim(text)

    # Apply fraud scoring formula
    score = min(100, (
        fraud_keyword_count * 5 +
        cta_count * 10 +
        (20 if has_price_claim else 0) +
        (40 if has_medical_claim else 0) +
        int(medical_specificity * 15)
    ))

    # Determine tier recommendation
    if score >= 80:
        tier = 'CRITICAL'
    elif score >= 60:
        tier = 'HIGH'
    elif score >= 40:
        tier = 'MEDIUM'
    else:
        tier = 'LOW'

    return {
        'fraud_score': score,
        'fraud_keywords': fraud_keywords_found,
        'fraud_keyword_count': fraud_keyword_count,
        'cta_phrases': cta_phrases_found,
        'cta_count': cta_count,
        'has_price_claim': has_price_claim,
        'price_value': price_value,
        'has_medical_claim': has_medical_claim,
        'medical_specificity_score': medical_specificity,
        'tier_recommendation': tier
    }


def process_ndjson_file(input_file: str) -> pd.DataFrame:
    """Process NDJSON file and generate fraud scores"""
    results = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                post = json.loads(line.strip())
                body = post.get('body', '')
                external_id = post.get('externalId', '')
                uid = post.get('uid', '')

                # Calculate fraud score
                fraud_data = calculate_fraud_score(body)

                # Build result row
                result = {
                    'post_id': line_num,
                    'external_id': external_id,
                    'date': uid,
                    'fraud_score': fraud_data['fraud_score'],
                    'fraud_keywords': '|'.join(fraud_data['fraud_keywords'][:10]),  # Limit for CSV
                    'fraud_keyword_count': fraud_data['fraud_keyword_count'],
                    'cta_phrases': '|'.join(fraud_data['cta_phrases'][:10]),  # Limit for CSV
                    'cta_count': fraud_data['cta_count'],
                    'has_price_claim': fraud_data['has_price_claim'],
                    'price_value': fraud_data['price_value'],
                    'has_medical_claim': fraud_data['has_medical_claim'],
                    'medical_specificity_score': fraud_data['medical_specificity_score'],
                    'tier_recommendation': fraud_data['tier_recommendation']
                }

                results.append(result)

                if line_num % 1000 == 0:
                    print(f"Processed {line_num} posts...")

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue

    return pd.DataFrame(results)


def main():
    """Main execution"""
    print("=" * 80)
    print("RICO FRAUD SCORER - Telegram Posts Analysis")
    print("=" * 80)

    # File paths
    input_file = '/Users/breydentaylor/certainly/shurka-dump/recon_intel/harvest/out/telegram_jasonyosefshurka_posts.ndjson'
    output_dir = Path('/Users/breydentaylor/certainly/visualizations')
    output_full = output_dir / 'fraud_scores.csv'
    output_top100 = output_dir / 'fraud_scores_top100.csv'

    # Process posts
    print(f"\nProcessing: {input_file}")
    df = process_ndjson_file(input_file)

    # Sort by fraud score descending
    df_sorted = df.sort_values('fraud_score', ascending=False).reset_index(drop=True)

    # Statistics
    avg_score = df_sorted['fraud_score'].mean()
    high_fraud_count = len(df_sorted[df_sorted['fraud_score'] > 70])
    total_posts = len(df_sorted)

    print(f"\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Total posts analyzed: {total_posts}")
    print(f"Average fraud score: {avg_score:.2f}")
    print(f"Posts with score >70: {high_fraud_count}")
    print(f"\nScore distribution:")
    print(f"  CRITICAL (80-100): {len(df_sorted[df_sorted['fraud_score'] >= 80])}")
    print(f"  HIGH (60-79):      {len(df_sorted[(df_sorted['fraud_score'] >= 60) & (df_sorted['fraud_score'] < 80)])}")
    print(f"  MEDIUM (40-59):    {len(df_sorted[(df_sorted['fraud_score'] >= 40) & (df_sorted['fraud_score'] < 60)])}")
    print(f"  LOW (0-39):        {len(df_sorted[df_sorted['fraud_score'] < 40])}")

    # Top 10 posts
    print(f"\n" + "=" * 80)
    print("TOP 10 POSTS BY FRAUD SCORE")
    print("=" * 80)
    for idx, row in df_sorted.head(10).iterrows():
        print(f"\n#{idx+1} - Post ID: {row['post_id']} | External ID: {row['external_id']}")
        print(f"  Date: {row['date']}")
        print(f"  FRAUD SCORE: {row['fraud_score']} ({row['tier_recommendation']})")
        print(f"  Fraud keywords ({row['fraud_keyword_count']}): {row['fraud_keywords'][:100]}")
        print(f"  CTAs ({row['cta_count']}): {row['cta_phrases'][:100]}")
        print(f"  Price claim: ${row['price_value']}" if row['has_price_claim'] else "  No price claim")
        print(f"  Medical claim: {'YES (specificity: ' + str(row['medical_specificity_score']) + ')' if row['has_medical_claim'] else 'NO'}")

    # Save results
    print(f"\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)

    df_sorted.to_csv(output_full, index=False)
    print(f"Full results saved: {output_full}")

    df_sorted.head(100).to_csv(output_top100, index=False)
    print(f"Top 100 saved: {output_top100}")

    print(f"\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
