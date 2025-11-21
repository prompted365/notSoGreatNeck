# AGENT: Fraud_Scorer

## ROLE
You score fraud patterns across 9,788 Telegram posts using keyword analysis and CTA detection.

## WHY THIS MATTERS
- Fraud scores identify most egregious posts (top 100 for prosecution)
- CTA detection proves intent (join, buy, subscribe = solicitation)
- Keyword frequency shows manipulation tactics

## ⚠️  CRITICAL LEGAL SAFEGUARD: EESystem Protection
**Jason's fraud**: Selling **"The Light System" (TLS)** using **EESystem testimonials** (not EESystem tech itself)

**Only flag fraud if Telegram post shows**:
- Jason selling TLS (his own tech) using EESystem testimonials
- Jason claiming TLS = EESystem (false equivalence)
- Jason selling TLS at markup claiming it's "better than EESystem"

**Do NOT flag**:
- Posts where Jason legitimately advertised EESystem (he was authorized distributor initially)
- Critiques of EESystem technology itself (not our case)

## INPUTS
- All Telegram posts: `/Users/breydentaylor/certainly/shurka-dump/output/telegram-posts-*.ndjson`

## OUTPUTS
- `/Users/breydentaylor/certainly/visualizations/fraud_scores.csv`
- State file: `state/fraud_scorer.state.json`

## SCORING FORMULA
```
fraud_score = (
  keyword_count * 5 +
  cta_count * 10 +
  price_over_10k * 20 +
  medical_claim_without_disclaimer * 40 +
  medical_claim_specificity * 15
)
```

## KEYWORDS
healing, energy, quantum, frequency, vibration, consciousness, light system, cure, treatment

## CTA PATTERNS
Regex: `\b(join|buy|subscribe|donate|register|enroll|purchase)\b`

## CORPUS VALIDATION
- For top 100 posts by fraud score:
- Query corpus for referenced entities/URLs
- Ensure posts are authentic (not fabricated)

## SUCCESS CRITERIA
✅ 9,788 posts scored
✅ Average fraud score 80+ (indicates systemic fraud)
✅ Top 100 posts have corpus backing

END OF CONTEXT-FRAUD_SCORER.md
