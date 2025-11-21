#!/usr/bin/env python3
"""
HTML Analyzer - Extract word frequencies from prosecution binder chunks
Generates word frequency data for word cloud visualization
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import sys

# Prosecution indicators and keywords
INDICATOR_CATEGORIES = {
    'fraud': ['scam', 'fraud', 'fake', 'stolen', 'laundering', 'launder', 'ponzi',
              'scheme', 'deceptive', 'misleading', 'counterfeit', 'forged', 'embezzle'],
    'victim': ['victim', 'complaint', 'loss', 'frozen', 'seized', 'damaged',
               'harmed', 'affected', 'plaintiff', 'claimant', 'injured'],
    'money': ['usd', 'btc', 'eth', 'usdt', 'wallet', 'crypto', 'cryptocurrency',
              'bitcoin', 'ethereum', 'tether', 'payment', 'transaction', 'transfer'],
    'entity': ['jason', 'shurka', 'unifyd', 'tls', 'ray', 'havakok', 'gadish',
               'sig', 'signature', 'investment', 'group'],
    'legal': ['court', 'judge', 'lawsuit', 'indictment', 'prosecution', 'evidence',
              'testimony', 'subpoena', 'warrant', 'conviction', 'charges', 'rico'],
    'criminal': ['conspiracy', 'racketeering', 'organized', 'crime', 'criminal',
                 'illegal', 'unlawful', 'violation', 'offense', 'felony']
}

# Define 8 logical chunk categories based on prosecution case structure
CHUNK_CATEGORIES = {
    'telegram': [0, 85],      # Telegram communications chunk
    'blockchain': [85, 170],  # Blockchain evidence chunk
    'legal': [170, 255],      # Legal documents chunk
    'financial': [255, 340],  # Financial evidence chunk
    'websites': [340, 425],   # Website/domain evidence chunk
    'communications': [425, 510],  # Other communications chunk
    'documents': [510, 595],  # General documents chunk
    'data': [595, 680]        # Miscellaneous data chunk
}

def clean_text(text):
    """Clean and normalize text for word frequency analysis"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and emojis
    text = re.sub(r'[^\w\s-]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_meaningful_word(word):
    """Filter out meaningless words"""
    # Skip short words, numbers, and common stopwords
    if len(word) < 3:
        return False
    if word.isdigit():
        return False

    stopwords = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
        'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
        'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did',
        'its', 'let', 'put', 'say', 'she', 'too', 'use', 'from', 'have', 'that',
        'with', 'this', 'will', 'your', 'about', 'there', 'their', 'which', 'would'
    }
    return word not in stopwords

def categorize_word(word):
    """Categorize word by indicator type"""
    word_lower = word.lower()
    for category, keywords in INDICATOR_CATEGORIES.items():
        if word_lower in keywords:
            return category
    return 'other'

def extract_word_frequencies(chunks, chunk_range=None):
    """Extract word frequencies from chunks"""
    word_counter = Counter()
    category_counter = defaultdict(Counter)
    co_occurrence = defaultdict(lambda: defaultdict(int))

    # Filter chunks if range specified
    if chunk_range:
        start, end = chunk_range
        chunks = [c for c in chunks if start <= c['id'] < end]

    for chunk in chunks:
        text = clean_text(chunk.get('text', ''))
        words = text.split()

        # Count meaningful words
        meaningful_words = [w for w in words if is_meaningful_word(w)]
        word_counter.update(meaningful_words)

        # Count by category
        for word in meaningful_words:
            category = categorize_word(word)
            category_counter[category][word] += 1

        # Calculate co-occurrence for indicators only
        indicator_words = [w for w in meaningful_words if categorize_word(w) != 'other']
        for i, word1 in enumerate(indicator_words):
            for word2 in indicator_words[i+1:i+20]:  # Look ahead 20 words
                if word1 != word2:
                    pair = tuple(sorted([word1, word2]))
                    co_occurrence[pair[0]][pair[1]] += 1

    return {
        'word_frequencies': dict(word_counter.most_common(500)),
        'category_frequencies': {cat: dict(counter.most_common(100))
                                for cat, counter in category_counter.items()},
        'co_occurrence': {k: dict(v) for k, v in co_occurrence.items()}
    }

def main():
    """Main execution"""
    base_path = Path(__file__).parent.parent
    coord_path = base_path / 'coordination'

    # Load chunks
    print("Loading binder chunks...")
    with open(coord_path / 'binder_chunks.json', 'r') as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks")

    # Process each chunk category
    results = {
        'chunks': {},
        'global': {},
        'metadata': {
            'total_chunks': len(chunks),
            'categories': CHUNK_CATEGORIES,
            'indicator_categories': INDICATOR_CATEGORIES
        }
    }

    print("\nProcessing chunk categories...")
    for category, chunk_range in CHUNK_CATEGORIES.items():
        print(f"  - Processing {category}: chunks {chunk_range[0]}-{chunk_range[1]}")
        results['chunks'][category] = extract_word_frequencies(chunks, chunk_range)

    print("\nProcessing global frequencies...")
    results['global'] = extract_word_frequencies(chunks)

    # Save results
    output_file = coord_path / 'html_word_frequencies.json'
    print(f"\nSaving results to {output_file}")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("HTML ANALYZER SUMMARY")
    print("="*60)
    print(f"Total chunks processed: {len(chunks)}")
    print(f"Chunk categories: {len(CHUNK_CATEGORIES)}")
    print(f"\nGlobal statistics:")
    print(f"  - Unique words: {len(results['global']['word_frequencies'])}")
    print(f"  - Top 10 words:")
    for i, (word, count) in enumerate(list(results['global']['word_frequencies'].items())[:10], 1):
        print(f"      {i:2d}. {word:20s} ({count:5d})")

    print(f"\nOutput file: {output_file}")
    print("="*60)

    return 0

if __name__ == '__main__':
    sys.exit(main())
