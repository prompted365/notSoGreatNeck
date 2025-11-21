#!/usr/bin/env python3
"""
CERT Agent 1: File Chunker
Identifies 8 strategically diverse chunks from corpus for deep analysis
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import hashlib

# Corpus directories
CORPUS_DIRS = [
    "/Users/breydentaylor/certainly/shurka-dump",
    "/Users/breydentaylor/certainly/noteworthy-raw"
]

OUTPUT_DIR = Path("/Users/breydentaylor/certainly/visualizations/coordination")
STATE_DIR = Path("/Users/breydentaylor/certainly/visualizations/state")

def get_file_inventory():
    """Get all analyzable files from corpus"""
    files = []

    for corpus_dir in CORPUS_DIRS:
        if not os.path.exists(corpus_dir):
            continue

        for root, dirs, filenames in os.walk(corpus_dir):
            # Skip hidden and system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']

            for filename in filenames:
                if filename.startswith('.'):
                    continue

                filepath = Path(root) / filename
                ext = filepath.suffix.lower()

                # Focus on HTML, JSON, TXT, MD, PDF (text extracted)
                if ext in ['.html', '.json', '.txt', '.md', '.csv']:
                    try:
                        size = filepath.stat().st_size
                        files.append({
                            'path': str(filepath),
                            'filename': filename,
                            'extension': ext,
                            'size': size,
                            'corpus': 'shurka-dump' if 'shurka-dump' in str(filepath) else 'noteworthy-raw'
                        })
                    except:
                        continue

    return files

def categorize_files(files):
    """Categorize files by type and content indicators"""
    categories = {
        'telegram': [],
        'blockchain': [],
        'legal': [],
        'financial': [],
        'websites': [],
        'communications': [],
        'documents': [],
        'data': []
    }

    for file in files:
        filename_lower = file['filename'].lower()
        path_lower = file['path'].lower()

        # Categorize based on filename patterns
        if 'telegram' in filename_lower or 'chat' in filename_lower:
            categories['telegram'].append(file)
        elif 'blockchain' in filename_lower or '0x' in filename_lower or 'transaction' in filename_lower:
            categories['blockchain'].append(file)
        elif 'court' in filename_lower or 'legal' in filename_lower or 'agreement' in filename_lower:
            categories['legal'].append(file)
        elif 'financ' in filename_lower or 'money' in filename_lower or 'payment' in filename_lower:
            categories['financial'].append(file)
        elif file['extension'] == '.html':
            categories['websites'].append(file)
        elif 'recording' in filename_lower or 'email' in filename_lower or 'chat' in filename_lower:
            categories['communications'].append(file)
        elif file['extension'] in ['.txt', '.md']:
            categories['documents'].append(file)
        elif file['extension'] in ['.json', '.csv']:
            categories['data'].append(file)

    return categories

def select_8_strategic_chunks(categories, files):
    """Select 8 diverse chunks covering different evidence types"""
    chunks = []

    # Chunk 1: Telegram Communications (largest priority)
    telegram_files = sorted(categories['telegram'], key=lambda x: x['size'], reverse=True)
    if telegram_files:
        chunks.append({
            'chunk_id': 'chunk_01_telegram',
            'chunk_name': 'Telegram Communications',
            'files': telegram_files[:20],  # Top 20 largest telegram files
            'priority': 'CRITICAL',
            'evidence_types': ['Communications', 'Victim Testimony', 'Timeline'],
            'total_size': sum(f['size'] for f in telegram_files[:20])
        })

    # Chunk 2: Blockchain Transactions
    blockchain_files = sorted(categories['blockchain'], key=lambda x: x['size'], reverse=True)
    if blockchain_files:
        chunks.append({
            'chunk_id': 'chunk_02_blockchain',
            'chunk_name': 'Blockchain Transactions',
            'files': blockchain_files[:15],
            'priority': 'HIGH',
            'evidence_types': ['Financial', 'Blockchain', 'Money Flow'],
            'total_size': sum(f['size'] for f in blockchain_files[:15])
        })

    # Chunk 3: Legal Documents
    legal_files = sorted(categories['legal'], key=lambda x: x['size'], reverse=True)
    if legal_files:
        chunks.append({
            'chunk_id': 'chunk_03_legal',
            'chunk_name': 'Legal Documents',
            'files': legal_files[:10],
            'priority': 'HIGH',
            'evidence_types': ['Legal', 'Court Filings', 'Agreements'],
            'total_size': sum(f['size'] for f in legal_files[:10])
        })

    # Chunk 4: Financial Records
    financial_files = sorted(categories['financial'], key=lambda x: x['size'], reverse=True)
    if financial_files:
        chunks.append({
            'chunk_id': 'chunk_04_financial',
            'chunk_name': 'Financial Records',
            'files': financial_files[:15],
            'priority': 'HIGH',
            'evidence_types': ['Financial', 'Money Laundering', 'Banking'],
            'total_size': sum(f['size'] for f in financial_files[:15])
        })

    # Chunk 5: Website HTML (UNIFYD, TLS, related)
    website_files = sorted(categories['websites'], key=lambda x: x['size'], reverse=True)
    if website_files:
        chunks.append({
            'chunk_id': 'chunk_05_websites',
            'chunk_name': 'Website HTML Content',
            'files': website_files[:25],
            'priority': 'MEDIUM',
            'evidence_types': ['Marketing', 'Medical Claims', 'URLs'],
            'total_size': sum(f['size'] for f in website_files[:25])
        })

    # Chunk 6: Communications (emails, recordings, chats)
    comm_files = sorted(categories['communications'], key=lambda x: x['size'], reverse=True)
    if comm_files:
        chunks.append({
            'chunk_id': 'chunk_06_communications',
            'chunk_name': 'Email & Audio Communications',
            'files': comm_files[:15],
            'priority': 'HIGH',
            'evidence_types': ['Communications', 'Victim Contact', 'Grooming'],
            'total_size': sum(f['size'] for f in comm_files[:15])
        })

    # Chunk 7: Extracted Documents (PDFs converted to text)
    doc_files = sorted(categories['documents'], key=lambda x: x['size'], reverse=True)
    if doc_files:
        # Filter for OCR/PDF extracts
        ocr_files = [f for f in doc_files if 'ocr' in f['filename'].lower() or 'pdf.txt' in f['filename'].lower()]
        chunks.append({
            'chunk_id': 'chunk_07_documents',
            'chunk_name': 'OCR Extracted Documents',
            'files': ocr_files[:20] if ocr_files else doc_files[:20],
            'priority': 'MEDIUM',
            'evidence_types': ['Documents', 'PDFs', 'Scanned Materials'],
            'total_size': sum(f['size'] for f in (ocr_files[:20] if ocr_files else doc_files[:20]))
        })

    # Chunk 8: Structured Data (JSON, CSV exports)
    data_files = sorted(categories['data'], key=lambda x: x['size'], reverse=True)
    if data_files:
        chunks.append({
            'chunk_id': 'chunk_08_data',
            'chunk_name': 'Structured Data Exports',
            'files': data_files[:20],
            'priority': 'MEDIUM',
            'evidence_types': ['Data', 'Exports', 'Transaction Lists'],
            'total_size': sum(f['size'] for f in data_files[:20])
        })

    return chunks

def main():
    print("🔬 CERT Agent 1: File Chunker")
    print("=" * 60)

    # Get file inventory
    print("📁 Scanning corpus directories...")
    files = get_file_inventory()
    print(f"   Found {len(files)} analyzable files")

    # Categorize
    print("📊 Categorizing files...")
    categories = categorize_files(files)
    for cat, cat_files in categories.items():
        print(f"   {cat}: {len(cat_files)} files")

    # Select 8 chunks
    print("🎯 Selecting 8 strategic chunks...")
    chunks = select_8_strategic_chunks(categories, files)
    print(f"   Created {len(chunks)} chunks")

    # Calculate totals
    total_files = sum(len(chunk['files']) for chunk in chunks)
    total_size = sum(chunk['total_size'] for chunk in chunks)

    # Output results
    output_data = {
        'mission': 'cert_file_chunking',
        'timestamp': Path(__file__).stat().st_mtime,
        'total_corpus_files': len(files),
        'total_selected_files': total_files,
        'total_size_bytes': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'chunks': chunks,
        'categories': {cat: len(cat_files) for cat, cat_files in categories.items()}
    }

    output_file = OUTPUT_DIR / 'cert_file_chunks.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Chunking complete!")
    print(f"   Total files selected: {total_files}")
    print(f"   Total size: {output_data['total_size_mb']} MB")
    print(f"   Output: {output_file}")

    # Update agent state
    state_file = STATE_DIR / 'cert_analytics_state.json'
    if state_file.exists():
        with open(state_file, 'r') as f:
            state = json.load(f)
        state['agents']['File_Chunker'] = {
            'status': 'completed',
            'chunks_identified': len(chunks),
            'files_selected': total_files,
            'completed_at': str(Path(__file__).stat().st_mtime)
        }
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    print("\n📝 Chunk Summary:")
    for chunk in chunks:
        print(f"   {chunk['chunk_id']}: {chunk['chunk_name']} ({len(chunk['files'])} files, {chunk['priority']})")

if __name__ == '__main__':
    main()
