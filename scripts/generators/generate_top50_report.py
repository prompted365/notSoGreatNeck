#!/usr/bin/env python3
"""
Generate detailed report of top 50 most fraudulent URLs
"""

import pandas as pd

CSV_FILE = "/Users/breydentaylor/certainly/visualizations/url_classifications.csv"

# Read CSV
df = pd.read_csv(CSV_FILE)

# Get top 50
top_50 = df.head(50)

print("="*100)
print("TOP 50 MOST FRAUDULENT URLs - DETAILED REPORT")
print("="*100)
print(f"\nTotal URLs analyzed: {len(df)}")
print(f"Top 50 shown below (sorted by fraud score)")
print()

for i, (idx, row) in enumerate(top_50.iterrows(), 1):
    print(f"\n{'-'*100}")
    print(f"RANK #{i} | Fraud Score: {row['fraud_score']} | Tier: {row['tier_recommendation']} | Platform: {row['platform'].upper()}")
    print(f"{'-'*100}")
    print(f"URL: {row['url']}")
    print(f"Post ID: {row['post_id']}")

    if row['light_system_mention']:
        print(f"⚠️  LIGHT SYSTEM MENTION DETECTED")

    if pd.notna(row['fraud_keywords']) and row['fraud_keywords']:
        print(f"Fraud Keywords: {row['fraud_keywords']}")

    if pd.notna(row['pricing_claims']) and row['pricing_claims']:
        print(f"Pricing Claims: {row['pricing_claims']}")

    print(f"Status: {row['status']}")

print("\n" + "="*100)
print("END OF TOP 50 REPORT")
print("="*100)

# Additional statistics for top 50
print("\n\nTOP 50 STATISTICS:")
print(f"  Average fraud score: {top_50['fraud_score'].mean():.2f}")
print(f"  Highest fraud score: {top_50['fraud_score'].max()}")
print(f"  Lowest fraud score (in top 50): {top_50['fraud_score'].min()}")
print(f"  URLs with Light System mentions: {top_50['light_system_mention'].sum()}")
print(f"\n  Platform breakdown:")
print(top_50['platform'].value_counts())
print(f"\n  Tier breakdown:")
print(top_50['tier_recommendation'].value_counts().sort_index())

# Most common fraud keywords in top 50
all_keywords = []
for keywords_str in top_50['fraud_keywords']:
    if pd.notna(keywords_str) and keywords_str:
        all_keywords.extend(keywords_str.split(','))

from collections import Counter
keyword_counts = Counter(all_keywords)
print(f"\n  Most common fraud keywords in top 50:")
for keyword, count in keyword_counts.most_common(10):
    print(f"    {keyword}: {count}")
