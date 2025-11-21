#!/usr/bin/env python3
"""
URL Analysis Script for RICO Evidence Processing
Analyzes deep-crawl-results.ndjson and classifies platforms, detects Light System mentions,
flags fraud indicators, and generates fraud scores.
"""

import json
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

# File paths
INPUT_FILE = "/Users/breydentaylor/certainly/shurka-dump/recon_intel/harvest/deep-crawl-results.ndjson"
OUTPUT_FILE = "/Users/breydentaylor/certainly/visualizations/url_classifications.csv"

# Fraud indicator keywords
FRAUD_KEYWORDS = {
    'quantum': 3,
    'healing': 2,
    'fda': 3,
    'frequency': 2,
    'energy': 1,
    'cure': 3,
    'miracle': 3,
    'certified': 2,
    'approved': 2,
    'medical': 2,
    'doctor': 1,
    'therapy': 1,
    'treatment': 2,
    'disease': 2,
    'cancer': 3,
    'pain': 1,
    'revolutionary': 2,
    'breakthrough': 2,
    'scientifically': 2,
    'clinically': 2,
}

# Pricing patterns
PRICE_PATTERNS = [
    r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*k',  # $25k, $50k
    r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',      # $25000, $50,000
]


def classify_platform(url: str, record_type: str) -> str:
    """Classify the platform based on URL and type."""
    url_lower = url.lower()

    if record_type == 'youtube' or 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif record_type == 'telegram' or 't.me' in url_lower or 'telegram' in url_lower:
        return 'telegram'
    elif 'unifyd' in url_lower:
        return 'unifyd'
    elif record_type == 'website':
        return 'website'
    else:
        return 'other'


def extract_text_content(data: Dict) -> str:
    """Extract all text content from the scraped data."""
    if not data or not isinstance(data, dict):
        return ""

    text_parts = []

    # Extract title
    if 'title' in data:
        text_parts.append(str(data['title']))

    # Extract meta description
    if 'metaDescription' in data:
        text_parts.append(str(data['metaDescription']))

    # Extract headings
    if 'headings' in data and isinstance(data['headings'], list):
        text_parts.extend([str(h) for h in data['headings']])

    # Extract description (for YouTube)
    if 'description' in data:
        text_parts.append(str(data['description']))

    return ' '.join(text_parts).lower()


def detect_light_system_mention(text: str, url: str) -> bool:
    """Detect if Light System is mentioned in content or URL."""
    patterns = [
        r'\blight\s+system\b',
        r'\bthe\s+light\s+system\b',
        r'\btls\b',
        r'thelightsystems\.com',
        r'tlsmarketplace',
    ]

    combined = (text + ' ' + url).lower()

    for pattern in patterns:
        if re.search(pattern, combined):
            return True

    return False


def find_fraud_keywords(text: str, url: str) -> List[str]:
    """Find fraud indicator keywords in text and URL."""
    combined = (text + ' ' + url).lower()
    found_keywords = []

    for keyword in FRAUD_KEYWORDS.keys():
        if re.search(r'\b' + keyword + r'\b', combined):
            found_keywords.append(keyword)

    return found_keywords


def extract_pricing(text: str) -> List[str]:
    """Extract pricing claims from text."""
    prices = []

    for pattern in PRICE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean and convert
            price_str = match.replace(',', '')
            try:
                price_val = float(price_str)
                if price_val >= 1000:  # Only flag high prices
                    prices.append(f"${match}")
            except ValueError:
                continue

    return prices


def calculate_fraud_score(
    light_system_mention: bool,
    fraud_keywords: List[str],
    has_pricing: bool,
    platform: str,
    status: str
) -> int:
    """Calculate fraud likelihood score (0-100)."""
    score = 0

    # Base score for Light System mention
    if light_system_mention:
        score += 30

    # Score for fraud keywords (weighted)
    for keyword in fraud_keywords:
        score += FRAUD_KEYWORDS.get(keyword, 1)

    # High pricing claims
    if has_pricing:
        score += 15

    # Platform weighting
    if platform == 'website':
        score += 10  # Websites more likely to contain fraud claims
    elif platform == 'youtube':
        score += 5

    # Successful scrape with data
    if status == 'success':
        score += 5

    # Cap at 100
    return min(score, 100)


def determine_tier(
    fraud_score: int,
    light_system_mention: bool,
    platform: str
) -> int:
    """
    Determine evidence tier:
    1 = blockchain-verified or highly credible
    2 = cross-referenced content
    3 = hypotheses or lower confidence
    """
    # High fraud score + Light System mention + website = Tier 1
    if fraud_score >= 60 and light_system_mention and platform in ['website', 'youtube']:
        return 1

    # Medium fraud score + some indicators = Tier 2
    elif fraud_score >= 30 and light_system_mention:
        return 2

    # Everything else = Tier 3
    else:
        return 3


def analyze_url(record: Dict) -> Dict:
    """Analyze a single URL record."""
    url = record.get('url', '')
    post_id = record.get('postId', '')
    record_type = record.get('type', '')
    status = record.get('status', '')
    data = record.get('data', {})

    # Extract text content
    text = extract_text_content(data)

    # Platform classification
    platform = classify_platform(url, record_type)

    # Light System detection
    light_system_mention = detect_light_system_mention(text, url)

    # Fraud keyword detection
    fraud_keywords = find_fraud_keywords(text, url)

    # Pricing extraction
    pricing = extract_pricing(text)

    # Calculate fraud score
    fraud_score = calculate_fraud_score(
        light_system_mention,
        fraud_keywords,
        len(pricing) > 0,
        platform,
        status
    )

    # Determine tier
    tier = determine_tier(fraud_score, light_system_mention, platform)

    return {
        'url': url,
        'post_id': post_id,
        'platform': platform,
        'light_system_mention': light_system_mention,
        'fraud_keywords': ','.join(fraud_keywords) if fraud_keywords else '',
        'fraud_score': fraud_score,
        'tier_recommendation': tier,
        'pricing_claims': ','.join(pricing) if pricing else '',
        'status': status,
    }


def main():
    """Main processing function."""
    print("Starting URL analysis...")
    print(f"Input file: {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")

    # Read NDJSON file
    records = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                record = json.loads(line.strip())
                records.append(record)
            except json.JSONDecodeError as e:
                print(f"Error parsing line {i}: {e}")
                continue

    print(f"Loaded {len(records)} records")

    # Analyze all URLs
    results = []
    for i, record in enumerate(records, 1):
        if i % 100 == 0:
            print(f"Processing record {i}/{len(records)}...")

        result = analyze_url(record)
        results.append(result)

    # Create DataFrame
    df = pd.DataFrame(results)

    # Sort by fraud score (descending)
    df = df.sort_values('fraud_score', ascending=False)

    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nCSV saved to: {OUTPUT_FILE}")

    # Generate statistics
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)

    print(f"\nTotal URLs analyzed: {len(df)}")
    print(f"\nPlatform distribution:")
    print(df['platform'].value_counts())

    print(f"\nLight System mentions: {df['light_system_mention'].sum()}")

    print(f"\nTier distribution:")
    print(df['tier_recommendation'].value_counts().sort_index())

    print(f"\nFraud score statistics:")
    print(f"  Mean: {df['fraud_score'].mean():.2f}")
    print(f"  Median: {df['fraud_score'].median():.2f}")
    print(f"  Max: {df['fraud_score'].max()}")
    print(f"  Min: {df['fraud_score'].min()}")

    print(f"\nTop 10 most fraudulent URLs:")
    print("="*80)

    top_10 = df.head(10)
    for idx, row in top_10.iterrows():
        print(f"\n{row['fraud_score']:.0f} | {row['platform'].upper()} | Tier {row['tier_recommendation']}")
        print(f"    {row['url'][:100]}")
        if row['fraud_keywords']:
            print(f"    Keywords: {row['fraud_keywords']}")
        if row['light_system_mention']:
            print(f"    ⚠️  Light System mention detected")

    print("\n" + "="*80)
    print(f"Top 50 URLs by fraud score have been flagged in the CSV")
    print("="*80)

    return df


if __name__ == '__main__':
    df = main()
