#!/usr/bin/env python3
"""
CYOA Audio Story — Timing Generator (faster-whisper)

Generates word-level timing JSON from audio, mapped to clean text files.

Whisper is used ONLY for timestamp extraction. The actual words come from
your text/*.txt files (the authoritative source).

Usage:
    python3 build-timing.py

Expected folder structure:
    text/           <- Plain text files, one per node (e.g., opening.txt)
    audio/narration/ <- MP3 files matching text filenames (e.g., opening.mp3)
    timing/         <- Output folder (created automatically)
"""

import os
import json
import sys
import re
from pathlib import Path

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("ERROR: faster-whisper not found. Install with:")
    print("  pip3 install faster-whisper --break-system-packages")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
TEXT_DIR = SCRIPT_DIR / "text"
AUDIO_DIR = SCRIPT_DIR / "audio" / "narration"
TIMING_DIR = SCRIPT_DIR / "timing"


def get_words_from_text(text_file):
    """Extract words from clean text file, preserving punctuation attached to words."""
    with open(text_file, 'r') as f:
        text = f.read().strip()
    # Split on whitespace, keeping punctuation attached to words
    words = text.split()
    return words


def get_whisper_timing(model, audio_file):
    """Get word timestamps from Whisper (we only care about the timing, not the words)."""
    segments, info = model.transcribe(
        str(audio_file),
        word_timestamps=True,
        language="en"
    )
    
    timings = []
    for segment in segments:
        if segment.words:
            for word_info in segment.words:
                if word_info.word.strip():
                    timings.append([
                        round(word_info.start, 3),
                        round(word_info.end, 3)
                    ])
    return timings


def align_timing_to_words(clean_words, whisper_timings):
    """
    Map Whisper timings to clean text words.
    
    If counts match: direct 1:1 mapping
    If counts differ: interpolate/stretch timing to fit clean word count
    """
    clean_count = len(clean_words)
    timing_count = len(whisper_timings)
    
    if clean_count == 0:
        return []
    
    if timing_count == 0:
        # No timing data — return empty (player will use fallback)
        return []
    
    if clean_count == timing_count:
        # Perfect match — use directly
        return whisper_timings
    
    # Counts differ — interpolate
    # Get total duration from Whisper timing
    start_time = whisper_timings[0][0]
    end_time = whisper_timings[-1][1]
    total_duration = end_time - start_time
    
    # Distribute evenly across clean words
    aligned_timings = []
    word_duration = total_duration / clean_count
    
    for i in range(clean_count):
        word_start = start_time + (i * word_duration)
        word_end = start_time + ((i + 1) * word_duration)
        aligned_timings.append([round(word_start, 3), round(word_end, 3)])
    
    return aligned_timings


def main():
    # Create output directory
    TIMING_DIR.mkdir(exist_ok=True)

    # Check for text files
    text_files = list(TEXT_DIR.glob("*.txt"))
    if not text_files:
        print(f"ERROR: No .txt files found in {TEXT_DIR}")
        sys.exit(1)

    print("=== CYOA Timing Generator (faster-whisper) ===")
    print("Loading large-v3 model (this will take a minute on first run)...")
    
    # Use large-v3 for best alignment accuracy
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")
    
    print("Model loaded.\n")

    for txt_file in sorted(text_files):
        node_id = txt_file.stem
        audio_file = AUDIO_DIR / f"{node_id}.mp3"
        output_file = TIMING_DIR / f"{node_id}.json"

        if not audio_file.exists():
            print(f"⚠️  SKIP: {node_id} (no matching audio file)")
            continue

        print(f"Processing: {node_id}")

        try:
            # Get clean words from text file (authoritative)
            clean_words = get_words_from_text(txt_file)
            
            # Get timing from Whisper
            whisper_timings = get_whisper_timing(model, audio_file)
            
            # Align timing to clean words
            aligned_timings = align_timing_to_words(clean_words, whisper_timings)
            
            # Report alignment
            timing_count = len(whisper_timings)
            word_count = len(clean_words)
            if timing_count != word_count:
                print(f"   ⚡ Word count mismatch: text={word_count}, whisper={timing_count} (interpolated)")
            
            # Write output with clean words + aligned timing
            output_data = {
                "words": clean_words,
                "timing": aligned_timings
            }

            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=2)

            print(f"   ✓ Created: timing/{node_id}.json ({word_count} words)")

        except Exception as e:
            print(f"   ✗ Failed: {node_id} — {e}")

    print("")
    print("=== Done ===")
    print(f"Timing files are in: {TIMING_DIR}")


if __name__ == "__main__":
    main()
