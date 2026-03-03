# CYOA Audio Story — HTML5 Prototype

A choose-your-own-adventure engine with word-level audio sync, background music, and sound effects.

## Quick Start

1. **Record narration** — One MP3 per story node, saved to `audio/narration/`
2. **Run alignment** — `./build-timing.sh` generates word-level timing via aeneas
3. **Open in browser** — `index.html` (use a local server for audio to work)

## Folder Structure

```
cyoa-prototype/
├── index.html           # The player (edit story data here)
├── build-timing.sh      # Runs aeneas on all text/audio pairs
├── convert-timing.py    # Converts aeneas output to player format
├── text/                # Plain text files, one per node
│   ├── opening.txt
│   ├── enter_gate.txt
│   └── ...
├── timing/              # Generated JSON timing files
│   ├── opening.json
│   └── ...
└── audio/
    ├── narration/       # Your recorded VO (MP3)
    │   ├── opening.mp3
    │   └── ...
    ├── music/           # Background music (loops)
    └── sfx/             # Sound effects
```

## Prerequisites (Mac)

```bash
# Install dependencies
brew install ffmpeg espeak
pip install aeneas --break-system-packages
```

## Workflow

### 1. Write your story

Edit the `story` object in `index.html`. Each node has:

```javascript
"node_id": {
  text: "The prose that appears on screen...",
  audio: {
    narration: "audio/narration/node_id.mp3",
    music: "audio/music/track.mp3",      // optional, loops
    sfx: [                                // optional
      { file: "audio/sfx/sound.mp3", at: 2.5 },           // plays at 2.5s
      { file: "audio/sfx/ambient.mp3", at: 0, loop: true } // loops from start
    ]
  },
  choices: [
    { text: "Choice text", goto: "next_node_id" }
  ]
}
```

### 2. Export text files

For each node, save the prose to `text/<node_id>.txt`. The text must match exactly what's in the HTML.

### 3. Record narration

Record one MP3 per node: `audio/narration/<node_id>.mp3`

Clean VO only — no music or SFX baked in.

### 4. Run alignment

```bash
./build-timing.sh
```

This runs aeneas on each text/audio pair and outputs JSON timing files to `timing/`.

### 5. Add music & SFX

Drop ambient tracks into `audio/music/` and sound effects into `audio/sfx/`. Reference them in the story data.

### 6. Test

```bash
# Start a local server (required for audio loading)
python3 -m http.server 8000

# Open in browser
open http://localhost:8000
```

## Features

- **Word-level highlighting**: Words fade from grey to white as narration progresses
- **Music crossfade**: Background music fades between different tracks
- **Timed SFX**: Sound effects trigger at specific timestamps
- **Read mode**: Skip audio, show all text immediately
- **Separate volume controls**: Voice, music, and SFX have independent sliders

## Fallback Behavior

If a timing file is missing, the player falls back to evenly distributing words across the audio duration. Works but less accurate.

If audio files are missing, the player logs a warning and continues (useful for testing before recording).

## Tips

- Keep node text under ~100 words for pacing
- Record in a consistent environment for seamless transitions
- Use sentence-level pauses in your narration — aeneas handles them well
- Test on mobile — touch interactions work out of the box
