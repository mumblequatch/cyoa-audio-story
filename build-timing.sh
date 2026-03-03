#!/bin/bash

# =============================================================================
# CYOA Audio Story — Aeneas Timing Generator
# =============================================================================
# Runs forced alignment on all text/audio pairs and outputs JSON timing files.
#
# Prerequisites (Mac):
#   brew install ffmpeg espeak
#   pip install aeneas --break-system-packages
#
# Usage:
#   ./build-timing.sh
#
# Expected folder structure:
#   text/           <- Plain text files, one per node (e.g., opening.txt)
#   audio/narration/ <- MP3 files matching text filenames (e.g., opening.mp3)
#   timing/         <- Output folder (created automatically)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEXT_DIR="$SCRIPT_DIR/text"
AUDIO_DIR="$SCRIPT_DIR/audio/narration"
TIMING_DIR="$SCRIPT_DIR/timing"

# Create output directory
mkdir -p "$TIMING_DIR"

# Check for aeneas
if ! python3 -c "import aeneas" 2>/dev/null; then
    echo "ERROR: aeneas not found. Install with:"
    echo "  pip install aeneas --break-system-packages"
    exit 1
fi

# Check for text files
if [ ! -d "$TEXT_DIR" ] || [ -z "$(ls -A "$TEXT_DIR"/*.txt 2>/dev/null)" ]; then
    echo "ERROR: No .txt files found in $TEXT_DIR"
    echo "Create text files for each story node (e.g., opening.txt)"
    exit 1
fi

echo "=== CYOA Timing Generator ==="
echo ""

# Process each text file
for txt_file in "$TEXT_DIR"/*.txt; do
    basename=$(basename "$txt_file" .txt)
    audio_file="$AUDIO_DIR/$basename.mp3"
    output_file="$TIMING_DIR/$basename.json"
    
    if [ ! -f "$audio_file" ]; then
        echo "⚠️  SKIP: $basename (no matching audio file)"
        continue
    fi
    
    echo "Processing: $basename"
    
    # Run aeneas with word-level alignment
    python3 -m aeneas.tools.execute_task \
        "$audio_file" \
        "$txt_file" \
        "task_language=eng|os_task_file_format=json|is_text_type=plain|task_adjust_boundary_algorithm=auto|task_adjust_boundary_nonspeech_min=0.1|task_adjust_boundary_nonspeech_string=SIL" \
        "$output_file" \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "   ✓ Created: timing/$basename.json"
    else
        echo "   ✗ Failed: $basename"
    fi
done

echo ""
echo "Converting aeneas output to player format..."
python3 "$SCRIPT_DIR/convert-timing.py" "$TIMING_DIR"/*.json

echo ""
echo "=== Done ==="
echo "Timing files are in: $TIMING_DIR"
