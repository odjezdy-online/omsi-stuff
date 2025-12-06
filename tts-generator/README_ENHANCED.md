# ElevenLabs TTS Generator (Enhanced Version)

An enhanced Python script for generating Text-to-Speech (TTS) announcements using the ElevenLabs API with support for audio tag insertion and OMSI HOF file parsing.

## New Features in Enhanced Version

### 1. Audio Tag Support

You can now embed audio tags in your announcement text to insert pre-recorded audio files:

- `{nz}` - **Na znamení** (On signal) - Inserts nz.wav with 150ms delay before and after
- `{pz}` - **Příští zastávka** (Next stop) - Inserts pz.wav with 150ms delay before and after
- `{kz}` - **Konečná zastávka** (Terminal stop) - Inserts kz.wav with 150ms delay before and after

**Example:**
```json
{
  "Station Name": {
    "hlaseni": "{nz} Main announcement text here {pz} More text {kz}",
    "soubor": "output_filename"
  }
}
```

The system will:
1. Generate TTS only for the text portions (not the tags)
2. Insert the tagged audio files at the specified positions
3. Add 150ms silence before and after each tagged audio
4. Combine everything with gong.wav (if present) at the beginning

### 2. HOF File Support

The enhanced version can now parse OMSI HOF (Haltestellen-Objekt-Formatierung) files and automatically generate announcements for all bus stops and termini defined in the file.

**What it extracts:**
- `[addterminus]` entries → Generates terminus announcements with "Konečná zastávka" message
- `[addterminus_allexit]` entries → Same as above
- `[addbusstop]` entries → Generates regular stop announcements

**Auto-generated format:**
- Terminus: "Konečná zastávka: {Name}. Prosíme, vystupte."
- Bus stop: "Zastávka: {Name}."

## Prerequisites

- Python 3.7 or higher
- ElevenLabs API key (get it from https://elevenlabs.io)
- FFmpeg installed and in PATH
- Audio files for tags (nz.wav, pz.wav, kz.wav) - optional
- gong.wav - optional intro sound

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure FFmpeg is installed and accessible via PATH

## Usage

### Running the Enhanced Version

```bash
python tts_generator_enhanced.py
```

### Interactive Workflow

The script guides you through:

1. **API Key Setup** - First time only, stored in config.json
2. **Voice Selection** - Choose from cloned, premium, or standard voices
3. **Voice Settings** - Configure stability, similarity boost, and style
4. **Input Selection**:
   - Option 1: JSON file (supports audio tags)
   - Option 2: HOF file (auto-generates announcements)
5. **Audio Generation** - Batch processes all announcements

### Using Audio Tags

Create a JSON file with tags embedded in the text:

```json
{
  "Stop with intro jingle": {
    "hlaseni": "{nz} Zastávka: Nádraží. Přestup na vlak.",
    "soubor": "nadrazi"
  },
  "Stop with multiple jingles": {
    "hlaseni": "{nz} Linka 31. {pz} Zastávka: Centrum. {kz}",
    "soubor": "centrum"
  }
}
```

**Tag Processing:**
- Tags are removed from the TTS text
- Only text portions are sent to ElevenLabs
- Tagged audio files are inserted during FFmpeg processing
- Each tag adds 150ms silence before and after the audio file

### Using HOF Files

1. Place your .hof file in the script directory
2. Run the enhanced script
3. Select option "2" for HOF file input
4. Choose your HOF file from the list
5. Script automatically extracts and generates announcements

The HOF parser will:
- Extract IBIS codes and stop names
- Create sanitized filenames
- Mark terminus stops with "(konecna)" suffix
- Generate appropriate Czech announcements

## Output

Generated audio files are saved in `generated_audio/` with WAV format:

```
generated_audio/
  ├── filename.wav
  ├── filename_with_tags.wav
  ├── terminus_#terminus.wav
  └── ...
```

Files marked as terminus (containing "(konecna)" in the key) get `_#terminus.wav` suffix.

## Audio Tag Files

Ensure these files are in the script directory for tag functionality:

- **nz.wav** - "Na znamení" (On signal) - Signal/alert jingle
- **pz.wav** - "Příští zastávka" (Next stop) - Next stop indicator jingle
- **kz.wav** - "Konečná zastávka" (Terminal stop) - Terminal/final stop jingle
- **gong.wav** - Optional intro sound for all announcements

All should be WAV format, 44.1kHz sample rate recommended.

## Configuration

### Voice Settings Parameters
- **stability** (0.0-1.0): Voice consistency - higher = more consistent but less expressive
- **similarity_boost** (0.0-1.0): How closely output matches original voice
- **style** (0.0-1.0): Exaggeration of speaking style
- **model_id**: "eleven_multilingual_v2" (default) or "eleven_turbo_v2_5" (faster)

### API Key Management
Priority order:
1. ELEVENLABS_API_KEY environment variable
2. .env file with ELEVENLABS_API_KEY
3. config.json "api_key" field
4. Interactive prompt (stores in config.json)

## FFmpeg Processing Details

### Audio Tag Chain
When tags are present, the FFmpeg filter builds:
1. Gong.wav (if present)
2. [Tag audio with 150ms delay before]
3. [150ms silence]
4. TTS audio
5. [Tag audio with 150ms delay before]
6. [150ms silence]
7. (repeat for all segments)

### Without Tags
Standard processing:
1. Convert MP3 → WAV (PCM 16-bit, 44.1kHz)
2. Prepend gong.wav with 250ms delay (if present)
3. Output final WAV

## Example Files

- **zastavky_with_tags_example.json** - Example JSON with audio tags
- **Bukovec_BUSE_V1.2 (testing).hof** - Example HOF file

## Differences from Original

| Feature | Original | Enhanced |
|---------|----------|----------|
| Input formats | JSON only | JSON + HOF |
| Audio tags | No | Yes ({nz}, {pz}, {kz}) |
| Auto-generation | No | Yes (from HOF) |
| Tag delays | N/A | 150ms before/after |
| HOF parsing | No | Yes |

## Troubleshooting

**Tags not working:**
- Ensure nz.wav, pz.wav, kz.wav exist in script directory
- Check WAV files are valid format
- Verify FFmpeg is installed correctly

**HOF parsing errors:**
- Check HOF file encoding (should be UTF-8 or CP1250)
- Verify HOF file structure matches OMSI format
- Look for [addterminus] and [addbusstop] sections

**Audio quality issues:**
- Ensure all WAV files have same sample rate (44.1kHz recommended)
- Check source audio files aren't corrupted
- Try adjusting voice settings for TTS quality

## Support

For issues or questions:
1. Check the ElevenLabs API documentation
2. Verify FFmpeg installation: `ffmpeg -version`
3. Ensure all required audio files are present
4. Check HOF file format against OMSI documentation
