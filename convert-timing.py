#!/usr/bin/env python3
"""
Converts aeneas JSON output to the simpler format used by the CYOA player.

Aeneas outputs:
{
  "fragments": [
    {"begin": "0.000", "end": "0.520", "lines": ["The"]},
    {"begin": "0.520", "end": "0.840", "lines": ["old"]},
    ...
  ]
}

We need:
{
  "words": ["The", "old", ...],
  "timing": [[0.0, 0.52], [0.52, 0.84], ...]
}

Usage:
  python3 convert-timing.py timing/opening.json
  python3 convert-timing.py timing/*.json   # batch convert all
"""

import json
import sys
import os

def convert_aeneas_json(input_path):
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    words = []
    timing = []
    
    for fragment in data.get('fragments', []):
        # Skip silence markers
        text = ' '.join(fragment.get('lines', [])).strip()
        if not text or text == 'SIL':
            continue
        
        begin = float(fragment['begin'])
        end = float(fragment['end'])
        
        # Handle multi-word fragments (shouldn't happen with word-level, but just in case)
        fragment_words = text.split()
        if len(fragment_words) > 1:
            # Distribute time evenly across words
            duration = end - begin
            word_duration = duration / len(fragment_words)
            for i, word in enumerate(fragment_words):
                words.append(word)
                timing.append([
                    round(begin + i * word_duration, 3),
                    round(begin + (i + 1) * word_duration, 3)
                ])
        else:
            words.append(text)
            timing.append([round(begin, 3), round(end, 3)])
    
    return {
        'words': words,
        'timing': timing
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 convert-timing.py <file.json> [file2.json ...]")
        sys.exit(1)
    
    for input_path in sys.argv[1:]:
        if not os.path.exists(input_path):
            print(f"File not found: {input_path}")
            continue
        
        try:
            converted = convert_aeneas_json(input_path)
            
            # Write back to same file (overwrite)
            with open(input_path, 'w') as f:
                json.dump(converted, f, indent=2)
            
            print(f"✓ Converted: {input_path} ({len(converted['words'])} words)")
        
        except Exception as e:
            print(f"✗ Error processing {input_path}: {e}")

if __name__ == '__main__':
    main()
