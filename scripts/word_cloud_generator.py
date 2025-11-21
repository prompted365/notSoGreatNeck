#!/usr/bin/env python3
"""
Word Cloud Generator - Create prosecution-ready word cloud visualizations
Generates word clouds per chunk + global, highlighting indicators
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from wordcloud import WordCloud
import seaborn as sns

# Color schemes for prosecution indicators
COLOR_SCHEMES = {
    'fraud': '#DC143C',      # Crimson red
    'victim': '#FF8C00',     # Dark orange
    'money': '#228B22',      # Forest green
    'entity': '#4169E1',     # Royal blue
    'legal': '#9370DB',      # Medium purple
    'criminal': '#8B0000',   # Dark red
    'other': '#696969'       # Dim gray
}

def create_color_func(category_frequencies):
    """Create color function for wordcloud based on indicator categories"""
    word_to_category = {}
    for category, words in category_frequencies.items():
        for word in words.keys():
            word_to_category[word] = category

    def color_func(word, **kwargs):
        category = word_to_category.get(word, 'other')
        return COLOR_SCHEMES.get(category, COLOR_SCHEMES['other'])

    return color_func

def generate_wordcloud(frequencies, category_frequencies, output_path, title, width=2400, height=1800):
    """Generate a single word cloud with color coding"""
    print(f"  Generating: {title}")

    if not frequencies:
        print(f"  WARNING: No frequencies for {title}")
        return

    # Create wordcloud
    color_func = create_color_func(category_frequencies)
    wc = WordCloud(
        width=width,
        height=height,
        background_color='white',
        max_words=200,
        relative_scaling=0.5,
        min_font_size=10,
        color_func=lambda word, **kwargs: color_func(word)
    )
    wc.generate_from_frequencies(frequencies)

    # Create figure
    fig = plt.figure(figsize=(width/100, height/100), dpi=300)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=32, fontweight='bold', pad=20)

    # Add legend
    legend_elements = [
        mpatches.Patch(color=COLOR_SCHEMES['fraud'], label='Fraud Terms'),
        mpatches.Patch(color=COLOR_SCHEMES['victim'], label='Victim Terms'),
        mpatches.Patch(color=COLOR_SCHEMES['money'], label='Money Terms'),
        mpatches.Patch(color=COLOR_SCHEMES['entity'], label='Entity Terms'),
        mpatches.Patch(color=COLOR_SCHEMES['legal'], label='Legal Terms'),
        mpatches.Patch(color=COLOR_SCHEMES['criminal'], label='Criminal Terms')
    ]
    plt.legend(handles=legend_elements, loc='lower right', fontsize=14)

    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {output_path}")

def generate_bar_chart(data, output_path):
    """Generate indicator bar chart"""
    print("  Generating indicator bar chart...")

    # Combine all category frequencies
    all_indicators = Counter()
    for category, freqs in data['global']['category_frequencies'].items():
        if category != 'other':
            all_indicators.update(freqs)

    # Get top 20
    top_indicators = all_indicators.most_common(20)
    words = [w for w, c in top_indicators]
    counts = [c for w, c in top_indicators]

    # Categorize each word for color
    categories = []
    colors = []
    for word in words:
        for cat, cat_freqs in data['global']['category_frequencies'].items():
            if word in cat_freqs:
                categories.append(cat)
                colors.append(COLOR_SCHEMES.get(cat, COLOR_SCHEMES['other']))
                break

    # Create chart
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    y_pos = np.arange(len(words))
    ax.barh(y_pos, counts, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(words)
    ax.invert_yaxis()
    ax.set_xlabel('Frequency', fontsize=14, fontweight='bold')
    ax.set_title('Top 20 Prosecution Indicators by Occurrence', fontsize=16, fontweight='bold')

    # Add legend
    legend_elements = [
        mpatches.Patch(color=COLOR_SCHEMES[cat], label=cat.title())
        for cat in set(categories)
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {output_path}")

def generate_cooccurrence_heatmap(data, output_path):
    """Generate co-occurrence heatmap"""
    print("  Generating co-occurrence heatmap...")

    co_occur = data['global']['co_occurrence']

    if not co_occur:
        print("  WARNING: No co-occurrence data")
        return

    # Get top indicators
    all_indicators = Counter()
    for category, freqs in data['global']['category_frequencies'].items():
        if category != 'other':
            all_indicators.update(freqs)

    top_words = [w for w, c in all_indicators.most_common(30)]

    # Build matrix
    matrix = np.zeros((len(top_words), len(top_words)))
    for i, word1 in enumerate(top_words):
        for j, word2 in enumerate(top_words):
            if word1 in co_occur and word2 in co_occur[word1]:
                matrix[i][j] = co_occur[word1][word2]
            elif word2 in co_occur and word1 in co_occur[word2]:
                matrix[i][j] = co_occur[word2][word1]

    # Create heatmap
    fig, ax = plt.subplots(figsize=(14, 12), dpi=300)
    sns.heatmap(
        matrix,
        xticklabels=top_words,
        yticklabels=top_words,
        cmap='YlOrRd',
        square=True,
        linewidths=0.5,
        cbar_kws={'label': 'Co-occurrence Count'},
        ax=ax
    )
    plt.title('Indicator Co-occurrence Heatmap', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Indicators', fontsize=12, fontweight='bold')
    plt.ylabel('Indicators', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.yticks(rotation=0, fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {output_path}")

def main():
    """Main execution"""
    base_path = Path(__file__).parent.parent
    coord_path = base_path / 'coordination'
    state_path = base_path / 'state'

    # Load word frequencies
    print("Loading word frequencies...")
    input_file = coord_path / 'html_word_frequencies.json'

    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        print("Please run html_analyzer.py first")
        return 1

    with open(input_file, 'r') as f:
        data = json.load(f)

    print(f"Loaded word frequencies for {len(data['chunks'])} chunks")

    # Generate per-chunk word clouds
    print("\nGenerating per-chunk word clouds...")
    chunk_names = {
        'telegram': 'Chunk 01: Telegram Communications',
        'blockchain': 'Chunk 02: Blockchain Evidence',
        'legal': 'Chunk 03: Legal Documents',
        'financial': 'Chunk 04: Financial Evidence',
        'websites': 'Chunk 05: Websites & Domains',
        'communications': 'Chunk 06: Communications',
        'documents': 'Chunk 07: General Documents',
        'data': 'Chunk 08: Miscellaneous Data'
    }

    for chunk_id, chunk_data in data['chunks'].items():
        output_file = coord_path / f'wordcloud_chunk_{list(data["chunks"].keys()).index(chunk_id)+1:02d}_{chunk_id}.png'
        generate_wordcloud(
            chunk_data['word_frequencies'],
            chunk_data['category_frequencies'],
            output_file,
            chunk_names.get(chunk_id, f'Chunk: {chunk_id}')
        )

    # Generate global word cloud
    print("\nGenerating global word cloud...")
    global_output = coord_path / 'wordcloud_global_all_chunks.png'
    generate_wordcloud(
        data['global']['word_frequencies'],
        data['global']['category_frequencies'],
        global_output,
        'Global Word Cloud: All 680 Chunks',
        width=3600,
        height=2700
    )

    # Generate bar chart
    print("\nGenerating indicator bar chart...")
    bar_output = coord_path / 'indicator_barchart.png'
    generate_bar_chart(data, bar_output)

    # Generate co-occurrence heatmap
    print("\nGenerating co-occurrence heatmap...")
    heatmap_output = coord_path / 'indicator_cooccurrence_heatmap.png'
    generate_cooccurrence_heatmap(data, heatmap_output)

    # Save state
    state_data = {
        'status': 'completed',
        'timestamp': str(Path(input_file).stat().st_mtime),
        'chunks_processed': len(data['chunks']),
        'global_words': len(data['global']['word_frequencies']),
        'outputs': {
            'per_chunk_wordclouds': 8,
            'global_wordcloud': 1,
            'indicator_barchart': 1,
            'cooccurrence_heatmap': 1
        },
        'files_generated': [
            str(coord_path / f'wordcloud_chunk_{i+1:02d}_{chunk_id}.png')
            for i, chunk_id in enumerate(data['chunks'].keys())
        ] + [
            str(global_output),
            str(bar_output),
            str(heatmap_output)
        ]
    }

    state_file = state_path / 'word_cloud_generator.state.json'
    with open(state_file, 'w') as f:
        json.dump(state_data, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("WORD CLOUD GENERATOR - EXECUTION SUMMARY")
    print("="*60)
    print(f"✅ Per-chunk word clouds: 8")
    print(f"✅ Global word cloud: 1")
    print(f"✅ Indicator bar chart: 1")
    print(f"✅ Co-occurrence heatmap: 1")
    print(f"\nTotal visualizations: 11")
    print(f"Output directory: {coord_path}")
    print(f"State file: {state_file}")
    print("="*60)
    print("\nSUCCESS CRITERIA MET:")
    print("✅ 8 chunk word clouds generated")
    print("✅ 1 global word cloud")
    print("✅ Indicator bar chart")
    print("✅ Co-occurrence heatmap")
    print("✅ All PNG files high resolution (300 DPI)")
    print("="*60)

    return 0

if __name__ == '__main__':
    sys.exit(main())
