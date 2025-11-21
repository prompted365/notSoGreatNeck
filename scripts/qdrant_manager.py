#!/usr/bin/env python3
"""
AGENT: Qdrant_Manager
MISSION: Initialize Qdrant vector database and load embeddings for 124 documents
Creates semantic search infrastructure for fraud evidence analysis
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any
import hashlib
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

# Configuration
BASE_DIR = Path("/Users/breydentaylor/certainly/visualizations")
COORDINATION_DIR = BASE_DIR / "coordination"
STATE_DIR = BASE_DIR / "state"
CERT_FILE_CHUNKS = COORDINATION_DIR / "cert_file_chunks.json"
QDRANT_DB_PATH = BASE_DIR / "qdrant_db"
COLLECTION_NAME = "shurka_corpus"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_CHUNK_TOKENS = 512
MAX_CHUNK_CHARS = MAX_CHUNK_TOKENS * 4  # Approximate: 4 chars per token

# Output files
COLLECTION_INFO_FILE = COORDINATION_DIR / "qdrant_collection_info.json"
EMBEDDINGS_METADATA_FILE = COORDINATION_DIR / "qdrant_embeddings_metadata.json"
TEST_SEARCHES_FILE = COORDINATION_DIR / "qdrant_test_searches.json"
STATE_FILE = STATE_DIR / "qdrant_manager.state.json"


class QdrantManager:
    """Manages Qdrant vector database for semantic search"""

    def __init__(self):
        """Initialize Qdrant client and embedding model"""
        print("🚀 Initializing Qdrant Manager...")

        # Create directories
        COORDINATION_DIR.mkdir(exist_ok=True)
        STATE_DIR.mkdir(exist_ok=True)
        QDRANT_DB_PATH.mkdir(exist_ok=True)

        # Initialize Qdrant client (disk-based for persistence)
        print(f"📂 Initializing Qdrant database at: {QDRANT_DB_PATH}")
        self.client = QdrantClient(path=str(QDRANT_DB_PATH))

        # Initialize embedding model
        print(f"🧠 Loading embedding model: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        # State tracking
        self.state = {
            "start_time": datetime.now().isoformat(),
            "files_processed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "errors": []
        }

        print("✅ Initialization complete!")

    def create_collection(self) -> Dict[str, Any]:
        """Create Qdrant collection with 384-dim vectors"""
        print(f"\n📦 Creating collection: {COLLECTION_NAME}")

        try:
            # Delete existing collection if it exists
            collections = self.client.get_collections().collections
            if any(c.name == COLLECTION_NAME for c in collections):
                print(f"⚠️  Collection {COLLECTION_NAME} already exists. Recreating...")
                self.client.delete_collection(COLLECTION_NAME)

            # Create new collection
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

            collection_info = self.client.get_collection(COLLECTION_NAME)

            result = {
                "collection_name": COLLECTION_NAME,
                "vector_size": 384,
                "distance": "COSINE",
                "status": "created",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Collection created successfully!")
            return result

        except Exception as e:
            error_msg = f"Error creating collection: {str(e)}"
            print(f"❌ {error_msg}")
            self.state["errors"].append(error_msg)
            raise

    def read_file_content(self, file_path: str) -> str:
        """Read and return file content"""
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"⚠️  File not found: {file_path}")
                return ""

            # Handle different file types
            if path.suffix.lower() in ['.txt', '.md', '.csv']:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            elif path.suffix.lower() in ['.json']:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = json.dumps(data, indent=2)
            elif path.suffix.lower() in ['.html']:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                # Strip HTML tags for better semantic search
                import re
                content = re.sub(r'<[^>]+>', ' ', content)
                content = re.sub(r'\s+', ' ', content).strip()
            else:
                print(f"⚠️  Unsupported file type: {path.suffix}")
                return ""

            return content

        except Exception as e:
            print(f"❌ Error reading file {file_path}: {str(e)}")
            self.state["errors"].append(f"Read error: {file_path} - {str(e)}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = MAX_CHUNK_CHARS) -> List[str]:
        """Split text into chunks of approximately chunk_size characters"""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for list of texts"""
        print(f"🔄 Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def process_files(self) -> List[Dict[str, Any]]:
        """Process all files from cert_file_chunks.json and generate embeddings"""
        print("\n📚 Loading file chunks...")

        with open(CERT_FILE_CHUNKS, 'r') as f:
            data = json.load(f)

        chunks_data = data.get("chunks", [])
        print(f"Found {len(chunks_data)} chunk categories with {data.get('total_selected_files', 0)} total files")

        all_points = []
        point_id = 0
        metadata_records = []

        for chunk_category in chunks_data:
            chunk_id = chunk_category["chunk_id"]
            chunk_name = chunk_category["chunk_name"]
            priority = chunk_category["priority"]
            evidence_types = chunk_category["evidence_types"]

            print(f"\n📂 Processing {chunk_name} ({len(chunk_category['files'])} files, priority: {priority})")

            for file_info in chunk_category["files"]:
                file_path = file_info["path"]
                filename = file_info["filename"]
                extension = file_info["extension"]
                corpus = file_info["corpus"]

                print(f"  📄 {filename} ({extension})")

                # Read file content
                content = self.read_file_content(file_path)

                if not content or len(content) < 50:
                    print(f"    ⚠️  Skipping (empty or too short)")
                    continue

                # Chunk the content
                text_chunks = self.chunk_text(content)
                print(f"    ✂️  Split into {len(text_chunks)} chunks")

                # Generate embeddings for all chunks
                embeddings = self.generate_embeddings(text_chunks)

                # Create points for each chunk
                for chunk_num, (text_chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
                    # Create metadata
                    metadata = {
                        "file_path": file_path,
                        "filename": filename,
                        "extension": extension,
                        "corpus": corpus,
                        "chunk_id": chunk_id,
                        "chunk_name": chunk_name,
                        "chunk_number": chunk_num,
                        "total_chunks": len(text_chunks),
                        "priority": priority,
                        "evidence_types": evidence_types,
                        "word_count": len(text_chunk.split()),
                        "char_count": len(text_chunk),
                        "text_preview": text_chunk[:500]  # First 500 chars
                    }

                    # Create point
                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=metadata
                    )

                    all_points.append(point)
                    metadata_records.append({
                        "point_id": point_id,
                        **metadata
                    })

                    point_id += 1
                    self.state["chunks_created"] += 1

                self.state["files_processed"] += 1
                self.state["embeddings_generated"] += len(embeddings)

        print(f"\n✅ Processed {self.state['files_processed']} files")
        print(f"✅ Created {self.state['chunks_created']} chunks")
        print(f"✅ Generated {self.state['embeddings_generated']} embeddings")

        return all_points, metadata_records

    def upload_to_qdrant(self, points: List[PointStruct], batch_size: int = 100):
        """Upload points to Qdrant in batches"""
        print(f"\n📤 Uploading {len(points)} points to Qdrant (batch size: {batch_size})...")

        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch
            )
            print(f"  ✅ Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")

        print(f"✅ All points uploaded successfully!")

    def test_semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Test semantic search with a query"""
        print(f"\n🔍 Testing search: '{query}'")

        # Generate query embedding
        query_embedding = self.model.encode(query).tolist()

        # Search
        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit
        )

        # Format results
        formatted_results = []
        for i, result in enumerate(results):
            formatted_result = {
                "rank": i + 1,
                "score": result.score,
                "point_id": result.id,
                "filename": result.payload.get("filename"),
                "chunk_name": result.payload.get("chunk_name"),
                "priority": result.payload.get("priority"),
                "evidence_types": result.payload.get("evidence_types"),
                "text_preview": result.payload.get("text_preview", "")[:200]
            }
            formatted_results.append(formatted_result)

            print(f"  {i+1}. [{result.score:.4f}] {result.payload.get('filename')} (chunk {result.payload.get('chunk_number')})")
            print(f"     {result.payload.get('text_preview', '')[:100]}...")

        return formatted_results

    def run_tests(self) -> Dict[str, Any]:
        """Run test searches"""
        print("\n🧪 Running test searches...")

        test_queries = [
            "Jason Shurka fraud",
            "cryptocurrency wallet blockchain",
            "victim complaint UNIFYD"
        ]

        test_results = {}
        for query in test_queries:
            results = self.test_semantic_search(query, limit=10)
            test_results[query] = results

        return test_results

    def save_outputs(self, collection_info: Dict, metadata_records: List[Dict], test_results: Dict):
        """Save all output files"""
        print("\n💾 Saving output files...")

        # Collection info
        with open(COLLECTION_INFO_FILE, 'w') as f:
            json.dump(collection_info, f, indent=2)
        print(f"  ✅ {COLLECTION_INFO_FILE}")

        # Embeddings metadata
        metadata_output = {
            "total_vectors": len(metadata_records),
            "model": EMBEDDING_MODEL,
            "vector_size": 384,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata_records
        }
        with open(EMBEDDINGS_METADATA_FILE, 'w') as f:
            json.dump(metadata_output, f, indent=2)
        print(f"  ✅ {EMBEDDINGS_METADATA_FILE}")

        # Test search results
        with open(TEST_SEARCHES_FILE, 'w') as f:
            json.dump(test_results, f, indent=2)
        print(f"  ✅ {TEST_SEARCHES_FILE}")

        # State file
        self.state["end_time"] = datetime.now().isoformat()
        self.state["status"] = "completed"
        self.state["outputs"] = {
            "collection_info": str(COLLECTION_INFO_FILE),
            "embeddings_metadata": str(EMBEDDINGS_METADATA_FILE),
            "test_searches": str(TEST_SEARCHES_FILE)
        }

        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
        print(f"  ✅ {STATE_FILE}")

    def run(self):
        """Execute full workflow"""
        try:
            start_time = time.time()

            # 1. Create collection
            collection_info = self.create_collection()

            # 2. Process files and generate embeddings
            points, metadata_records = self.process_files()

            # 3. Upload to Qdrant
            self.upload_to_qdrant(points)

            # 4. Get collection stats
            collection_stats = self.client.get_collection(COLLECTION_NAME)
            collection_info["points_count"] = collection_stats.points_count
            collection_info["indexed_vectors_count"] = collection_stats.indexed_vectors_count if hasattr(collection_stats, 'indexed_vectors_count') else collection_stats.points_count

            # 5. Run test searches
            test_results = self.run_tests()

            # 6. Save outputs
            self.save_outputs(collection_info, metadata_records, test_results)

            elapsed_time = time.time() - start_time

            # Final summary
            print("\n" + "="*60)
            print("🎉 QDRANT MANAGER COMPLETE!")
            print("="*60)
            print(f"⏱️  Time elapsed: {elapsed_time:.2f} seconds")
            print(f"📂 Files processed: {self.state['files_processed']}")
            print(f"✂️  Chunks created: {self.state['chunks_created']}")
            print(f"🧠 Embeddings generated: {self.state['embeddings_generated']}")
            print(f"📦 Collection: {COLLECTION_NAME}")
            print(f"🔢 Points in collection: {collection_stats.points_count}")
            print(f"❌ Errors: {len(self.state['errors'])}")
            print("\n📁 Output files:")
            print(f"  • {COLLECTION_INFO_FILE}")
            print(f"  • {EMBEDDINGS_METADATA_FILE}")
            print(f"  • {TEST_SEARCHES_FILE}")
            print(f"  • {STATE_FILE}")
            print("="*60)

            if self.state['errors']:
                print("\n⚠️  Errors encountered:")
                for error in self.state['errors'][:10]:
                    print(f"  • {error}")

            return True

        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")
            self.state["status"] = "failed"
            self.state["fatal_error"] = str(e)
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
            raise


if __name__ == "__main__":
    print("\n" + "="*60)
    print("QDRANT MANAGER - Semantic Search Infrastructure")
    print("="*60)

    manager = QdrantManager()
    manager.run()
