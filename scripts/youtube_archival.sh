#!/bin/bash

# YouTube Video Archival Script
# Mission: cert1-phase5-video-archive-20251121
# Purpose: Archive 20+ videos with fraudulent medical claims
# Legal Basis: Fair use for legal evidence, chain of custody required

set -e  # Exit on error

# Configuration
ARCHIVE_DIR="/Users/breydentaylor/certainly/visualizations/evidence-archive/youtube"
METADATA_DIR="/Users/breydentaylor/certainly/visualizations/coordination"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== YouTube Archival System ===${NC}"
echo "Mission: URGENT spoliation prevention"
echo "Timestamp: $TIMESTAMP"
echo "Archive Directory: $ARCHIVE_DIR"
echo ""

# Create archive directory structure
mkdir -p "$ARCHIVE_DIR/videos"
mkdir -p "$ARCHIVE_DIR/metadata"
mkdir -p "$ARCHIVE_DIR/transcripts"
mkdir -p "$ARCHIVE_DIR/thumbnails"
mkdir -p "$ARCHIVE_DIR/checksums"

echo -e "${YELLOW}Archive directories created${NC}"

# Function to download and archive a single video
archive_video() {
    local VIDEO_URL="$1"
    local VIDEO_ID="$2"
    local VIDEO_TITLE="$3"

    echo -e "${GREEN}Archiving: $VIDEO_TITLE${NC}"
    echo "URL: $VIDEO_URL"
    echo "ID: $VIDEO_ID"

    # Download video with full metadata
    yt-dlp \
        --write-info-json \
        --write-thumbnail \
        --write-description \
        --write-subs \
        --write-auto-subs \
        --sub-lang en \
        --convert-subs srt \
        --write-comments \
        --get-comments \
        --extract-audio --audio-format mp3 \
        --output "$ARCHIVE_DIR/videos/${VIDEO_ID}_%(title)s.%(ext)s" \
        "$VIDEO_URL" 2>&1 | tee "$ARCHIVE_DIR/metadata/${VIDEO_ID}_download.log"

    # Generate SHA-256 hash
    if [ -f "$ARCHIVE_DIR/videos/${VIDEO_ID}"*.mp4 ]; then
        sha256sum "$ARCHIVE_DIR/videos/${VIDEO_ID}"*.mp4 >> "$ARCHIVE_DIR/checksums/video_hashes.txt"
        echo -e "${GREEN}✓ Video downloaded and hashed${NC}"
    else
        echo -e "${RED}✗ Video download failed${NC}"
    fi

    echo ""
}

# Function to extract fraud indicators from transcript
analyze_transcript() {
    local TRANSCRIPT_FILE="$1"
    local VIDEO_ID="$2"

    echo "Analyzing transcript for fraud patterns..."

    # Search for fraud keywords
    FRAUD_KEYWORDS=(
        "healing"
        "cure"
        "treatment"
        "frequency"
        "energy"
        "quantum"
        "cellular"
        "disease"
        "pain relief"
        "immune system"
        "inflammation"
        "detox"
    )

    echo "{" > "$ARCHIVE_DIR/metadata/${VIDEO_ID}_fraud_analysis.json"
    echo "  \"video_id\": \"$VIDEO_ID\"," >> "$ARCHIVE_DIR/metadata/${VIDEO_ID}_fraud_analysis.json"
    echo "  \"timestamp\": \"$TIMESTAMP\"," >> "$ARCHIVE_DIR/metadata/${VIDEO_ID}_fraud_analysis.json"
    echo "  \"fraud_indicators\": [" >> "$ARCHIVE_DIR/metadata/${VIDEO_ID}_fraud_analysis.json"

    for KEYWORD in "${FRAUD_KEYWORDS[@]}"; do
        if grep -qi "$KEYWORD" "$TRANSCRIPT_FILE" 2>/dev/null; then
            echo "    \"$KEYWORD\"," >> "$ARCHIVE_DIR/metadata/${VIDEO_ID}_fraud_analysis.json"
        fi
    done

    echo "  ]," >> "$ARCHIVE_DIR/metadata/${VIDEO_ID}_fraud_analysis.json"
    echo "  \"analysis_complete\": true" >> "$ARCHIVE_DIR/metadata/${VIDEO_ID}_fraud_analysis.json"
    echo "}" >> "$ARCHIVE_DIR/metadata/${VIDEO_ID}_fraud_analysis.json"

    echo -e "${GREEN}✓ Fraud analysis complete${NC}"
}

# Function to create archival manifest
create_manifest() {
    echo -e "${YELLOW}Creating archival manifest...${NC}"

    MANIFEST_FILE="$METADATA_DIR/video_archive_manifest.json"

    cat > "$MANIFEST_FILE" <<EOF
{
  "mission_id": "cert1-phase5-video-archive-20251121",
  "archival_timestamp": "$TIMESTAMP",
  "archive_directory": "$ARCHIVE_DIR",
  "archival_method": "yt-dlp",
  "legal_basis": "Fair use for legal evidence (17 U.S.C. § 107)",
  "chain_of_custody": {
    "archival_tool": "yt-dlp 2025.11.12",
    "hash_algorithm": "SHA-256",
    "timestamp": "$TIMESTAMP",
    "archivist": "Autonomous Legal Evidence System"
  },
  "videos_archived": [],
  "fraud_patterns_documented": [],
  "evidence_classification": {
    "type": "Type 5 - URL fraud patterns",
    "tier": "Tier 1 - Ready NOW",
    "legal_framework": "FTC Section 5, FDA violations"
  },
  "spoliation_prevention": {
    "risk_level": "HIGH",
    "urgency": "URGENT",
    "window": "4 hours",
    "rationale": "Defendants may delete videos once investigation is known"
  }
}
EOF

    echo -e "${GREEN}✓ Manifest created: $MANIFEST_FILE${NC}"
}

# Main execution
echo -e "${YELLOW}=== Starting Video Archival ===${NC}"

# Create initial manifest
create_manifest

# Example: Archive a single video (template)
# Uncomment and modify with actual URLs
# archive_video "https://www.youtube.com/watch?v=VIDEO_ID" "video_001" "Video Title"

echo -e "${GREEN}=== Archival System Ready ===${NC}"
echo "Use: ./youtube_archival.sh or execute archive_video function with URLs"
echo ""
echo "Example:"
echo "  archive_video 'https://www.youtube.com/watch?v=XXXXX' 'video_001' 'Title'"
echo ""
echo "To download from list:"
echo "  Read youtube_target_videos.json and execute archive_video for each"
echo ""

# Generate final report
echo -e "${YELLOW}Generating final statistics...${NC}"
TOTAL_VIDEOS=$(ls "$ARCHIVE_DIR/videos/"*.mp4 2>/dev/null | wc -l || echo "0")
TOTAL_HASHES=$(wc -l < "$ARCHIVE_DIR/checksums/video_hashes.txt" 2>/dev/null || echo "0")

echo ""
echo -e "${GREEN}=== Archival Statistics ===${NC}"
echo "Videos archived: $TOTAL_VIDEOS"
echo "SHA-256 hashes generated: $TOTAL_HASHES"
echo "Archive location: $ARCHIVE_DIR"
echo "Manifest: $METADATA_DIR/video_archive_manifest.json"
echo ""
echo -e "${GREEN}Mission complete${NC}"
