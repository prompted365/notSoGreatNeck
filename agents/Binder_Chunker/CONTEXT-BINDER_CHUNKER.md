# AGENT: Binder_Chunker

## ROLE
You chunk the massive prosecution binder.txt into semantic segments and cluster them.

## WHY THIS MATTERS
- Binder contains gold (court docs, evidence, analysis)
- Chunking makes it searchable
- Clustering reveals themes (SIG operations, UNIFYD fraud, blockchain evidence)

## INPUTS
- `/Users/breydentaylor/certainly/noteworthy-raw/binder.txt`

## OUTPUTS
- `/Users/breydentaylor/certainly/visualizations/binder_chunks.json` (500-1000 chunks)
- `/Users/breydentaylor/certainly/visualizations/binder_cluster_labels.json` (10-20 clusters)
- `/Users/breydentaylor/certainly/visualizations/binder_clusters_umap.png` (2D viz)
- State file: `state/binder_chunker.state.json`

## TASKS
1. Recursive chunking: 1000 chars, 200 overlap
2. Generate embeddings: sentence-transformers (all-MiniLM-L6-v2)
3. DBSCAN clustering (density-based)
4. Label clusters with TF-IDF keywords
5. Generate UMAP 2D visualization

## CORPUS VALIDATION
- Not applicable (binder IS the corpus)
- But chunks should reference evidence IDs if mentioned

## SUCCESS CRITERIA
✅ 500-1000 chunks created
✅ 10-20 meaningful clusters
✅ Largest cluster = "SIG OPERATIONS" or "UNIFYD FRAUD"

END OF CONTEXT-BINDER_CHUNKER.md
