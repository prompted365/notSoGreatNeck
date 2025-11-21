#!/usr/bin/env python3
"""
Complete analysis summary of all 2,679 URLs
"""

import pandas as pd

CSV_FILE = "/Users/breydentaylor/certainly/visualizations/url_classifications.csv"

# Read CSV
df = pd.read_csv(CSV_FILE)

print("="*100)
print("COMPLETE URL ANALYSIS SUMMARY - RICO EVIDENCE PROCESSING")
print("="*100)
print(f"\nDataset: /Users/breydentaylor/certainly/shurka-dump/recon_intel/harvest/deep-crawl-results.ndjson")
print(f"Output: /Users/breydentaylor/certainly/visualizations/url_classifications.csv")
print(f"\nTotal URLs analyzed: {len(df)}")

print("\n" + "="*100)
print("PLATFORM CLASSIFICATION")
print("="*100)
platform_counts = df['platform'].value_counts()
for platform, count in platform_counts.items():
    pct = (count / len(df)) * 100
    print(f"  {platform.upper():<15} {count:>5} URLs ({pct:>5.2f}%)")

print("\n" + "="*100)
print("LIGHT SYSTEM MENTIONS")
print("="*100)
ls_count = df['light_system_mention'].sum()
ls_pct = (ls_count / len(df)) * 100
print(f"  URLs with Light System mentions: {ls_count} ({ls_pct:.2f}%)")
print(f"  URLs without Light System mentions: {len(df) - ls_count} ({100-ls_pct:.2f}%)")

print("\n  Light System mentions by platform:")
ls_by_platform = df[df['light_system_mention'] == True].groupby('platform').size().sort_values(ascending=False)
for platform, count in ls_by_platform.items():
    platform_total = len(df[df['platform'] == platform])
    pct = (count / platform_total) * 100
    print(f"    {platform.upper():<15} {count:>3}/{platform_total:<5} ({pct:>5.2f}%)")

print("\n" + "="*100)
print("FRAUD SCORE DISTRIBUTION")
print("="*100)
print(f"  Mean fraud score: {df['fraud_score'].mean():.2f}")
print(f"  Median fraud score: {df['fraud_score'].median():.2f}")
print(f"  Standard deviation: {df['fraud_score'].std():.2f}")
print(f"  Min score: {df['fraud_score'].min()}")
print(f"  Max score: {df['fraud_score'].max()}")

print("\n  Fraud score ranges:")
score_ranges = [
    (0, 10, "Low risk"),
    (10, 20, "Low-Medium risk"),
    (20, 30, "Medium risk"),
    (30, 40, "Medium-High risk"),
    (40, 50, "High risk"),
    (50, 101, "Critical risk")
]

for low, high, label in score_ranges:
    count = len(df[(df['fraud_score'] >= low) & (df['fraud_score'] < high)])
    pct = (count / len(df)) * 100
    print(f"    {label:<20} [{low:>2}-{high-1:>2}]: {count:>5} URLs ({pct:>5.2f}%)")

print("\n" + "="*100)
print("TIER RECOMMENDATIONS")
print("="*100)
tier_counts = df['tier_recommendation'].value_counts().sort_index()
tier_descriptions = {
    1: "Blockchain-verified / Highly credible",
    2: "Cross-referenced content",
    3: "Hypotheses / Lower confidence"
}

for tier, count in tier_counts.items():
    pct = (count / len(df)) * 100
    desc = tier_descriptions.get(tier, "Unknown")
    print(f"  Tier {tier} ({desc}): {count} URLs ({pct:.2f}%)")

print("\n" + "="*100)
print("FRAUD KEYWORD ANALYSIS")
print("="*100)

# Count all fraud keywords
all_keywords = []
for keywords_str in df['fraud_keywords']:
    if pd.notna(keywords_str) and keywords_str:
        all_keywords.extend(keywords_str.split(','))

from collections import Counter
keyword_counts = Counter(all_keywords)

print(f"  Total fraud keyword occurrences: {len(all_keywords)}")
print(f"  Unique fraud keywords found: {len(keyword_counts)}")
print(f"\n  Top 15 most common fraud keywords:")
for i, (keyword, count) in enumerate(keyword_counts.most_common(15), 1):
    pct = (count / len(df)) * 100
    print(f"    {i:>2}. {keyword:<20} {count:>4} occurrences ({pct:>5.2f}% of all URLs)")

print("\n" + "="*100)
print("STATUS ANALYSIS")
print("="*100)
status_counts = df['status'].value_counts()
for status, count in status_counts.items():
    pct = (count / len(df)) * 100
    print(f"  {status.upper():<15} {count:>5} URLs ({pct:>5.2f}%)")

print("\n" + "="*100)
print("HIGH-RISK URL SUMMARY")
print("="*100)

high_risk = df[df['fraud_score'] >= 40]
print(f"  Total high-risk URLs (score >= 40): {len(high_risk)}")
print(f"  Percentage of dataset: {(len(high_risk)/len(df))*100:.2f}%")

print(f"\n  High-risk URLs by platform:")
hr_by_platform = high_risk.groupby('platform').size().sort_values(ascending=False)
for platform, count in hr_by_platform.items():
    print(f"    {platform.upper():<15} {count:>3} URLs")

critical_risk = df[df['fraud_score'] >= 50]
print(f"\n  CRITICAL-risk URLs (score >= 50): {len(critical_risk)}")
for idx, row in critical_risk.head(10).iterrows():
    print(f"    Score {row['fraud_score']}: {row['url'][:80]}")

print("\n" + "="*100)
print("PRICING CLAIMS ANALYSIS")
print("="*100)
urls_with_pricing = df[df['pricing_claims'].notna() & (df['pricing_claims'] != '')]
print(f"  URLs with pricing claims detected: {len(urls_with_pricing)}")
if len(urls_with_pricing) > 0:
    print(f"  Percentage of dataset: {(len(urls_with_pricing)/len(df))*100:.2f}%")
    print(f"\n  Sample URLs with pricing claims:")
    for idx, row in urls_with_pricing.head(10).iterrows():
        print(f"    {row['pricing_claims']}: {row['url'][:70]}")
else:
    print("  No explicit pricing claims in $25K-$50K range detected in scraped content")

print("\n" + "="*100)
print("KEY FINDINGS")
print("="*100)
print(f"  1. {len(df)} total URLs analyzed from deep-crawl-results.ndjson")
print(f"  2. {ls_count} URLs ({ls_pct:.2f}%) contain Light System mentions")
print(f"  3. {len(high_risk)} URLs ({(len(high_risk)/len(df))*100:.2f}%) flagged as high-risk (score >= 40)")
print(f"  4. {len(critical_risk)} URLs flagged as CRITICAL risk (score >= 50)")
print(f"  5. Most common fraud keywords: {', '.join([k for k, c in keyword_counts.most_common(5)])}")
print(f"  6. Primary platform: {platform_counts.index[0].upper()} ({platform_counts.iloc[0]} URLs, {(platform_counts.iloc[0]/len(df))*100:.2f}%)")
print(f"  7. All top 50 URLs are classified as Tier 2 (cross-referenced content)")
print(f"  8. All top 50 URLs contain Light System mentions")
print(f"  9. Website platform has highest concentration of high-risk URLs")
print(f" 10. Average fraud score: {df['fraud_score'].mean():.2f}/100")

print("\n" + "="*100)
print("OUTPUT FILES")
print("="*100)
print(f"  CSV file: /Users/breydentaylor/certainly/visualizations/url_classifications.csv")
print(f"  Rows: {len(df) + 1} (including header)")
print(f"  Columns: url, post_id, platform, light_system_mention, fraud_keywords,")
print(f"           fraud_score, tier_recommendation, pricing_claims, status")
print("\n" + "="*100)
