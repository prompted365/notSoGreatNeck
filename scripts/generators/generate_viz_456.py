#!/usr/bin/env python3
"""
Generate visualizations 4-6: Evidence, Geographic, Conspiracy Network
"""

import json
import csv
from collections import defaultdict, Counter

# Read all data
print("📊 Loading foundation data...")
entities = {}
with open('../shurka-dump/database-backups_2025-11-05T04-22-08_entities.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        entities[row['id']] = row

relationships = []
with open('../shurka-dump/database-backups_2025-11-05T04-22-08_relationships.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        relationships.append(row)

print(f"   Entities: {len(entities)}")
print(f"   Relationships: {len(relationships)}\n")

# ==============================================================================
# VIZ 4: EVIDENCE PROVENANCE HEAT MAP
# ==============================================================================
print("=" * 80)
print("VIZ 4: EVIDENCE PROVENANCE HEAT MAP - ENTITY-TO-EVIDENCE CROSS-REFERENCE")
print("=" * 80)

# Track which entities have evidence
entity_evidence = defaultdict(lambda: {'total_rels': 0, 'evidenced_rels': 0, 'rico_rels': 0, 'sources': set()})

for rel in relationships:
    src = rel.get('source_entity_id', '')
    tgt = rel.get('target_entity_id', '')
    evidence = rel.get('evidence', '').strip()
    rico = rel.get('rico_relevance', '').strip()
    sources = rel.get('source_documents', '').strip()

    for entity_id in [src, tgt]:
        if entity_id:
            entity_evidence[entity_id]['total_rels'] += 1
            if evidence or sources:
                entity_evidence[entity_id]['evidenced_rels'] += 1
                if sources:
                    entity_evidence[entity_id]['sources'].add(sources[:50])
            if rico:
                entity_evidence[entity_id]['rico_rels'] += 1

# Calculate evidence strength scores
evidence_scores = []
for entity_id, stats in entity_evidence.items():
    if stats['total_rels'] > 0:
        evidence_pct = (stats['evidenced_rels'] / stats['total_rels']) * 100
        rico_pct = (stats['rico_rels'] / stats['total_rels']) * 100
        score = evidence_pct + (rico_pct * 2)  # RICO evidence weighted 2x
        evidence_scores.append({
            'entity': entity_id,
            'score': score,
            'evidenced': stats['evidenced_rels'],
            'rico': stats['rico_rels'],
            'total': stats['total_rels'],
            'sources': len(stats['sources'])
        })

evidence_scores.sort(key=lambda x: x['score'], reverse=True)

print(f"\n🔥 TOP 20 ENTITIES BY EVIDENCE STRENGTH:")
for i, item in enumerate(evidence_scores[:20], 1):
    entity = item['entity'][:35]
    score = item['score']
    evidenced = item['evidenced']
    rico = item['rico']
    total = item['total']
    sources = item['sources']

    # Heat map visualization
    if score > 200:
        heat = '🔴🔴🔴'  # RED HOT
    elif score > 100:
        heat = '🟠🟠'    # ORANGE
    elif score > 50:
        heat = '🟡'      # YELLOW
    else:
        heat = '⚪'      # WHITE

    print(f"   {i:2d}. {heat} {entity:35s} | Score: {score:6.1f} | {evidenced}/{total} evidenced | {rico} RICO")

# Generate Mermaid quadrant chart
mermaid4 = ["```mermaid", "quadrantChart"]
mermaid4.append('    title Entity Evidence Strength Matrix')
mermaid4.append('    x-axis "Low Evidence Coverage" --> "High Evidence Coverage"')
mermaid4.append('    y-axis "Low RICO Relevance" --> "High RICO Relevance"')

# Place top 15 entities in quadrants
for item in evidence_scores[:15]:
    entity = item['entity'].replace(' ', '_')[:20]
    x = min(item['evidenced'] / max(item['total'], 1) * 100, 100)
    y = min(item['rico'] / max(item['total'], 1) * 100, 100)
    mermaid4.append(f'    {entity}: [{x:.0f}, {y:.0f}]')

mermaid4.append("```")

viz4_output = "\n".join(mermaid4)
print("\n" + viz4_output)

# Save VIZ 4
with open('VIZ_4_EVIDENCE_HEAT_MAP.md', 'w') as f:
    f.write("# VIZ 4: EVIDENCE PROVENANCE HEAT MAP\n\n")
    f.write("**Purpose:** Cross-reference entities with available evidence strength\n\n")
    f.write("**Methodology:**\n")
    f.write("- Evidence Score = (Evidenced Relationships / Total Relationships × 100)\n")
    f.write("- RICO Score = (RICO-Relevant Relationships / Total Relationships × 100) × 2\n")
    f.write("- Total Score = Evidence Score + RICO Score\n\n")
    f.write("**Heat Map Legend:**\n")
    f.write("- 🔴🔴🔴 RED HOT: Score > 200 (multiple RICO-relevant evidenced relationships)\n")
    f.write("- 🟠🟠 ORANGE: Score > 100 (moderate evidence + RICO relevance)\n")
    f.write("- 🟡 YELLOW: Score > 50 (some evidence)\n")
    f.write("- ⚪ WHITE: Score < 50 (weak evidence)\n\n")
    f.write("## Top 20 Entities by Evidence Strength\n\n")
    for i, item in enumerate(evidence_scores[:20], 1):
        entity = item['entity']
        score = item['score']
        evidenced = item['evidenced']
        rico = item['rico']
        total = item['total']
        sources = item['sources']

        if score > 200:
            heat = '🔴🔴🔴'
        elif score > 100:
            heat = '🟠🟠'
        elif score > 50:
            heat = '🟡'
        else:
            heat = '⚪'

        f.write(f"{i}. {heat} **{entity}**\n")
        f.write(f"   - Evidence Score: {score:.1f}\n")
        f.write(f"   - Evidenced Relationships: {evidenced}/{total}\n")
        f.write(f"   - RICO-Relevant Relationships: {rico}\n")
        f.write(f"   - Source Documents: {sources}\n\n")

    f.write("\n" + viz4_output)
    f.write("\n\n**RICO Significance:** Identifies strongest evidentiary targets for subpoenas and witness interviews\n")

print("\n✅ VIZ 4 COMPLETE: Evidence heat map showing strongest targets\n")

# ==============================================================================
# VIZ 5: GEOGRAPHIC/JURISDICTIONAL NEXUS
# ==============================================================================
print("=" * 80)
print("VIZ 5: GEOGRAPHIC/JURISDICTIONAL NEXUS MAP")
print("=" * 80)

# Extract geographic data from entities
geo_data = defaultdict(lambda: {'entities': [], 'types': Counter()})

for entity_id, entity in entities.items():
    # Look for location indicators
    jurisdiction = entity.get('jurisdiction', '').strip()
    addresses = entity.get('addresses', '').strip()
    entity_type = entity.get('entity_type', 'unknown')

    locations = []
    if jurisdiction:
        locations.append(jurisdiction)
    if 'brooklyn' in str(entity).lower():
        locations.append('Brooklyn, NY')
    if 'queens' in str(entity).lower():
        locations.append('Queens, NY')
    if 'israel' in str(entity).lower() or 'haifa' in str(entity).lower() or 'tel aviv' in str(entity).lower():
        locations.append('Israel')
    if 'florida' in str(entity).lower():
        locations.append('Florida')

    for loc in locations:
        geo_data[loc]['entities'].append(entity_id)
        geo_data[loc]['types'][entity_type] += 1

print(f"\n📍 JURISDICTIONAL DISTRIBUTION:")
for location, data in sorted(geo_data.items(), key=lambda x: len(x[1]['entities']), reverse=True)[:15]:
    entity_count = len(data['entities'])
    top_type = data['types'].most_common(1)[0] if data['types'] else ('unknown', 0)
    print(f"   {location:30s}: {entity_count:3d} entities (primary: {top_type[0]})")

# Generate geographic map (simplified)
mermaid5 = ["```mermaid", "graph LR"]
mermaid5.append('    %% Shurka Criminal Enterprise - Geographic/Jurisdictional Nexus')
mermaid5.append('')
mermaid5.append('    US["🇺🇸 UNITED STATES"]')
mermaid5.append('    style US fill:#1e3a8a,stroke:#1e40af,stroke-width:3px,color:#fff')
mermaid5.append('')
mermaid5.append('    IL["🇮🇱 ISRAEL"]')
mermaid5.append('    style IL fill:#0c4a6e,stroke:#0369a1,stroke-width:3px,color:#fff')
mermaid5.append('')

# US Locations
us_locs = ['Brooklyn, NY', 'Queens, NY', 'Florida', 'New York']
for loc in us_locs:
    if loc in geo_data:
        count = len(geo_data[loc]['entities'])
        loc_clean = loc.replace(',', '').replace(' ', '_').replace('.', '')
        mermaid5.append(f'    {loc_clean}["{loc}<br/>{count} entities"]')
        mermaid5.append(f'    US --> {loc_clean}')

# Israel locations
il_locs = ['Israel']
for loc in il_locs:
    if loc in geo_data:
        count = len(geo_data[loc]['entities'])
        loc_clean = loc.replace(',', '').replace(' ', '_').replace('.', '')
        mermaid5.append(f'    {loc_clean}["{loc}<br/>{count} entities"]')
        mermaid5.append(f'    IL --> {loc_clean}')

# Add connections showing international coordination
mermaid5.append('')
mermaid5.append('    %% Cross-border connections')
mermaid5.append('    US <==> |Wire fraud<br/>Money laundering| IL')

mermaid5.append("```")

viz5_output = "\n".join(mermaid5)
print("\n" + viz5_output)

with open('VIZ_5_GEOGRAPHIC_NEXUS.md', 'w') as f:
    f.write("# VIZ 5: GEOGRAPHIC/JURISDICTIONAL NEXUS MAP\n\n")
    f.write("**Purpose:** Establish multi-jurisdictional criminal enterprise for RICO\n\n")
    f.write("**Key Findings:**\n")
    for location, data in sorted(geo_data.items(), key=lambda x: len(x[1]['entities']), reverse=True)[:10]:
        entity_count = len(data['entities'])
        top_type = data['types'].most_common(1)[0] if data['types'] else ('unknown', 0)
        f.write(f"- **{location}**: {entity_count} entities (primary type: {top_type[0]})\n")

    f.write("\n" + viz5_output)
    f.write("\n\n**RICO Significance:** Multi-state and international operations support RICO enterprise scope and wire fraud predicates (18 U.S.C. § 1343)\n")

print("\n✅ VIZ 5 COMPLETE: Geographic nexus showing US-Israel coordination\n")

# ==============================================================================
# VIZ 6: CONSPIRACY NETWORK - MANNY ↔ JASON + COORDINATION PATTERNS
# ==============================================================================
print("=" * 80)
print("VIZ 6: CRIMINAL CONSPIRACY COORDINATION NETWORK")
print("=" * 80)

# Find conspiracy-related relationships
conspiracy_rels = []
for rel in relationships:
    rel_type = rel.get('relationship_type', '').upper()
    description = rel.get('description', '').lower()
    rico = rel.get('rico_relevance', '').lower()

    if any(keyword in rel_type or keyword in description or keyword in rico
           for keyword in ['CONSPIRACY', 'CRIMINAL', 'EXTORTION', 'FRAUD', 'COORDINATED']):
        conspiracy_rels.append(rel)

print(f"\n🚨 CONSPIRACY-RELATED RELATIONSHIPS: {len(conspiracy_rels)}")

# Build conspiracy network
conspiracy_nodes = set()
conspiracy_edges = []

for rel in conspiracy_rels:
    src = rel.get('source_entity_id', '')
    tgt = rel.get('target_entity_id', '')
    rel_type = rel.get('relationship_type', 'unknown')
    rico = rel.get('rico_relevance', '')[:100]

    if src and tgt:
        conspiracy_nodes.add(src)
        conspiracy_nodes.add(tgt)
        conspiracy_edges.append({
            'src': src,
            'tgt': tgt,
            'type': rel_type,
            'rico': rico
        })

# Generate Mermaid graph
mermaid6 = ["```mermaid", "graph TD"]
mermaid6.append('    %% Criminal Conspiracy Coordination Network')
mermaid6.append('')

# Highlight key conspirators
key_conspirators = {
    'person_manny_shurka': '👤 Manny Shurka<br/>CO-CONSPIRATOR',
    'person_jason_y_shurka': '🎯 Jason Shurka<br/>PRIMARY TARGET',
    'jason-yosef-shurka': '🎯 Jason Shurka<br/>PRIMARY TARGET',
    'manny_shurka': '👤 Manny Shurka<br/>CO-CONSPIRATOR',
}

for node_id in conspiracy_nodes:
    clean_id = node_id.replace('-', '_').replace(' ', '_')
    if node_id in key_conspirators:
        label = key_conspirators[node_id]
        mermaid6.append(f'    {clean_id}["{label}"]')
        mermaid6.append(f'    style {clean_id} fill:#dc2626,stroke:#991b1b,stroke-width:5px,color:#fff,font-size:14px')
    else:
        label = node_id[:30]
        mermaid6.append(f'    {clean_id}["{label}"]')

mermaid6.append('')
mermaid6.append('    %% Conspiracy Relationships')

for edge in conspiracy_edges[:20]:  # Limit for readability
    src_clean = edge['src'].replace('-', '_').replace(' ', '_')
    tgt_clean = edge['tgt'].replace('-', '_').replace(' ', '_')
    label = edge['type'][:25]

    if 'CRIMINAL' in edge['type'].upper() or 'CONSPIRACY' in edge['type'].upper():
        mermaid6.append(f'    {src_clean} ==>|🚨 {label}| {tgt_clean}')
        mermaid6.append(f'    linkStyle {len([e for e in conspiracy_edges[:20] if e == edge])} stroke:#dc2626,stroke-width:4px')
    else:
        mermaid6.append(f'    {src_clean} -->|{label}| {tgt_clean}')

mermaid6.append("```")

viz6_output = "\n".join(mermaid6)
print("\n" + viz6_output)

with open('VIZ_6_CONSPIRACY_NETWORK.md', 'w') as f:
    f.write("# VIZ 6: CRIMINAL CONSPIRACY COORDINATION NETWORK\n\n")
    f.write("**Purpose:** Map Manny ↔ Jason conspiracy coordination and co-conspirator network\n\n")
    f.write("**Key Evidence:**\n")
    f.write("- **Aug 2024**: Jason $30M extortion demand → Manny $15M 'lowball' offer (coordination)\n")
    f.write("- **Nov 14, 2024**: Jason ultimatum call → Hours later, coordinated multi-platform attack\n")
    f.write("- **Pattern**: Shared extortion methodology, synchronized timing, unified fraud scheme\n\n")
    f.write(f"**Conspiracy-Related Relationships Identified:** {len(conspiracy_rels)}\n\n")

    f.write("## Conspiracy Relationships Detail:\n\n")
    for i, rel in enumerate(conspiracy_rels[:10], 1):
        src = rel.get('source_entity_id', 'unknown')
        tgt = rel.get('target_entity_id', 'unknown')
        rel_type = rel.get('relationship_type', 'unknown')
        rico = rel.get('rico_relevance', '')
        timeline = rel.get('timeline', '')

        f.write(f"{i}. **{src} ↔ {tgt}**\n")
        f.write(f"   - Type: {rel_type}\n")
        if rico:
            f.write(f"   - RICO: {rico[:200]}...\n")
        if timeline:
            f.write(f"   - Timeline: {timeline[:200]}...\n")
        f.write("\n")

    f.write("\n" + viz6_output)
    f.write("\n\n**RICO Significance:** Establishes CONSPIRACY (18 U.S.C. § 371) and demonstrates coordinated racketeering pattern\n")

print("\n✅ VIZ 6 COMPLETE: Conspiracy network showing Manny ↔ Jason coordination\n")

print("\n" + "=" * 80)
print("✅ ALL 6 VISUALIZATIONS COMPLETE")
print("=" * 80)
print("\nFiles created:")
print("  - VIZ_4_EVIDENCE_HEAT_MAP.md")
print("  - VIZ_5_GEOGRAPHIC_NEXUS.md")
print("  - VIZ_6_CONSPIRACY_NETWORK.md")
print("\nALL VISUALIZATIONS READY FOR PROSECUTION BINDER")
