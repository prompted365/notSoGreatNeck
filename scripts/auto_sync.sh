#!/bin/bash
# auto_sync.sh - Automatic project sync and file discovery
# Scans for new files, updates documentation, commits, and pushes to GitHub

set -e

PROJECT_ROOT="/Users/breydentaylor/certainly/visualizations"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         CERT ANALYTICS - AUTO SYNC & FILE DISCOVERY            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "⏰ Sync started: $TIMESTAMP"
echo ""

# ============================================================================
# PHASE 1: FILE DISCOVERY
# ============================================================================
echo "📂 PHASE 1: Discovering new files..."
echo "──────────────────────────────────────────────────────────────────"

# Count files by directory
SCRIPT_COUNT=$(find scripts/ -type f -name "*.py" -o -name "*.sh" 2>/dev/null | wc -l | tr -d ' ')
STATE_COUNT=$(find state/ -type f -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
COORD_COUNT=$(find coordination/ -type f 2>/dev/null | wc -l | tr -d ' ')
AGENT_COUNT=$(find agents/ -type d -mindepth 1 -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
DOC_COUNT=$(find . -maxdepth 1 -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

echo "   Scripts:      $SCRIPT_COUNT files"
echo "   State files:  $STATE_COUNT files"
echo "   Coordination: $COORD_COUNT files"
echo "   Agent dirs:   $AGENT_COUNT directories"
echo "   Docs:         $DOC_COUNT markdown files"
echo ""

# Check for new files since last commit
NEW_FILES=$(git status --porcelain 2>/dev/null | grep "^??" | wc -l | tr -d ' ')
MODIFIED_FILES=$(git status --porcelain 2>/dev/null | grep "^ M" | wc -l | tr -d ' ')

echo "   🆕 New files:      $NEW_FILES"
echo "   📝 Modified files: $MODIFIED_FILES"
echo ""

# ============================================================================
# PHASE 2: UPDATE DIRECTORY TREE
# ============================================================================
echo "📁 PHASE 2: Updating directory tree..."
echo "──────────────────────────────────────────────────────────────────"

# Generate updated directory tree
cat > DIRECTORY_TREE.md <<'TREE_EOF'
# Directory Tree - notSoGreatNeck Investigation

**Generated**: TIMESTAMP_PLACEHOLDER
**Total Size**: ~456 MB (outputs) + 1.6 GB (corpus)
**Structure**: Organized by function (evidence, analysis, automation, documentation)

---

## 📁 **ROOT STRUCTURE**

```
visualizations/
├── README.md                          # Main project documentation
├── AI_AGENT_README.md                # AI agent operational guide
├── USER_GUIDE.md                     # User interaction guide
├── LEGAL_DISCLAIMER.md               # Confidentiality and methodology notice
├── DIRECTORY_TREE.md                 # This file
├── .gitignore                        # Git ignore rules
├── requirements.txt                   # Python dependencies
├── venv/                             # Python virtual environment (not in git)
│
├── coordination/                     # 🔴 PRIMARY OUTPUTS (56 MB, 48+ files)
│   ├── Evidence Catalogs
│   ├── Semantic Analysis
│   ├── Visualizations
│   ├── Network Analysis
│   └── Citations & Provenance
│
├── handoff-binder/                   # 🔴 PROSECUTION DELIVERABLES (8 files)
│   ├── evidence_inventory.json
│   ├── subpoena_package_final.md
│   ├── prosecution_readiness_report.json
│   └── PHASE4_EXECUTIVE_SUMMARY.md
│
├── state/                            # 🟡 AGENT STATES (21+ files)
│   ├── autonomous_phases.json
│   ├── cert_analytics_state.json
│   └── [agent].state.json files
│
├── scripts/                          # 🟢 AUTOMATION (30+ files)
│   ├── Semantic Search
│   ├── Agent Deployment
│   ├── Analysis Pipelines
│   ├── Background Monitors
│   └── auto_sync.sh (this script)
│
├── qdrant_db/                        # 🟣 VECTOR DATABASE (400 MB)
│   └── 88,721 semantic embeddings
│
├── agents/                           # 🔵 AGENT CONTEXTS (10 directories)
│   ├── Pillar_Scout/
│   ├── Gap_Filler/
│   └── [agent directories]
│
└── docs/                             # 📚 DOCUMENTATION (15+ files)
    ├── Mission Reports
    ├── Technical Guides
    └── Integration Summaries
```

---

## 🔍 **QUICK NAVIGATION**

### **For Legal Team**
1. Start with `LEGAL_DISCLAIMER.md` (REQUIRED READING)
2. Review `USER_GUIDE.md` for system interaction
3. Read `handoff-binder/PHASE4_EXECUTIVE_SUMMARY.md`
4. View visualizations in `coordination/wordcloud_*.png`

### **For Technical Analysis**
1. Use `scripts/search_corpus.py` for semantic search
2. Load `coordination/network_graph.graphml` in Gephi
3. Review `coordination/semantic_clusters.json` for themes
4. Check `coordination/citation_database.json` for provenance

### **For AI Agents**
1. Read `AI_AGENT_README.md` for operational guide
2. Check `state/` for agent completion status
3. Use functions in `AI_AGENT_README.md` for queries
4. Follow agent context files in `agents/`

---

**Last Updated**: TIMESTAMP_PLACEHOLDER
**Auto-generated by**: scripts/auto_sync.sh
**Status**: Production-ready ✅
TREE_EOF

# Replace timestamp placeholder
sed -i '' "s/TIMESTAMP_PLACEHOLDER/$TIMESTAMP/g" DIRECTORY_TREE.md

echo "   ✅ DIRECTORY_TREE.md updated"
echo ""

# ============================================================================
# PHASE 3: VALIDATE CRITICAL FILES
# ============================================================================
echo "✓ PHASE 3: Validating critical files..."
echo "──────────────────────────────────────────────────────────────────"

CRITICAL_FILES=(
    "README.md"
    "AI_AGENT_README.md"
    "USER_GUIDE.md"
    "LEGAL_DISCLAIMER.md"
    "DIRECTORY_TREE.md"
    "requirements.txt"
)

MISSING_COUNT=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ MISSING: $file"
        MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
done

echo ""
if [ $MISSING_COUNT -gt 0 ]; then
    echo "   ⚠️  $MISSING_COUNT critical files missing!"
else
    echo "   ✅ All critical files present"
fi
echo ""

# ============================================================================
# PHASE 4: GIT STAGING
# ============================================================================
echo "📦 PHASE 4: Staging changes for commit..."
echo "──────────────────────────────────────────────────────────────────"

# Stage all changes
git add -A

# Show what will be committed
STAGED_FILES=$(git diff --cached --name-only | wc -l | tr -d ' ')
echo "   📋 Staged files: $STAGED_FILES"

if [ $STAGED_FILES -gt 0 ]; then
    echo ""
    echo "   Files to be committed:"
    git diff --cached --name-status | head -20 | sed 's/^/      /'
    if [ $(git diff --cached --name-only | wc -l) -gt 20 ]; then
        echo "      ... and $((STAGED_FILES - 20)) more files"
    fi
fi
echo ""

# ============================================================================
# PHASE 5: COMMIT
# ============================================================================
echo "💾 PHASE 5: Creating commit..."
echo "──────────────────────────────────────────────────────────────────"

if [ $STAGED_FILES -gt 0 ]; then
    # Generate commit message
    COMMIT_MSG=$(cat <<EOF
chore: Auto-sync - File discovery and documentation update

Sync Summary:
- Scripts: $SCRIPT_COUNT files
- State files: $STATE_COUNT files
- Coordination: $COORD_COUNT files
- Agent directories: $AGENT_COUNT
- Documentation: $DOC_COUNT files

Changes:
- New files added: $NEW_FILES
- Modified files: $MODIFIED_FILES
- Directory tree updated
- Timestamp: $TIMESTAMP

🤖 Auto-generated by scripts/auto_sync.sh
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)

    git commit -m "$COMMIT_MSG"
    echo "   ✅ Commit created"
else
    echo "   ℹ️  No changes to commit"
fi
echo ""

# ============================================================================
# PHASE 6: PUSH TO GITHUB
# ============================================================================
echo "🚀 PHASE 6: Pushing to GitHub..."
echo "──────────────────────────────────────────────────────────────────"

if [ $STAGED_FILES -gt 0 ]; then
    if git push origin main; then
        echo "   ✅ Successfully pushed to origin/main"
    else
        echo "   ❌ Push failed - check network/authentication"
        exit 1
    fi
else
    echo "   ℹ️  Nothing to push (no changes)"
fi
echo ""

# ============================================================================
# PHASE 7: SUMMARY
# ============================================================================
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      SYNC COMPLETE                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Final Status:"
echo "   Repository: prompted365/notSoGreatNeck"
echo "   Branch: main"
echo "   Files tracked: $(git ls-files | wc -l | tr -d ' ')"
echo "   Last commit: $(git log -1 --format='%h - %s' 2>/dev/null)"
echo ""
echo "✅ Project synchronized successfully!"
echo ""
echo "⏰ Sync completed: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# Optional: Show repository URL
echo "🔗 GitHub Repository:"
echo "   https://github.com/prompted365/notSoGreatNeck"
echo ""
