# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based Text-to-Speech (TTS) generator for public transport announcements using the ElevenLabs API. The script processes batch announcements from JSON files and generates audio files with optional gong effects using FFmpeg.

**Three versions available:**
- **tts_generator.py** - Original version with basic JSON support
- **tts_generator_enhanced.py** - Enhanced version with audio tag support and basic HOF parsing
- **tts_generator_enhanced_v2.py** - Latest version with improved HOF parser (handles trip-based stop definitions, line filtering, and free Google TTS testing mode)

## Key Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

**Original version:**
```bash
python tts_generator.py
```

**Enhanced version (with audio tags and basic HOF support):**
```bash
python tts_generator_enhanced.py
```

**Enhanced v2 (recommended - improved HOF parser with trip support and free testing):**
```bash
python tts_generator_enhanced_v2.py
```

The script runs interactively through 5 steps:
1. API key setup (first-time only, stored in config.json)
2. Voice selection from available ElevenLabs voices
3. Voice settings configuration (stability, similarity boost, style)
4. Announcements file loading (JSON or HOF in enhanced version)
5. Batch audio generation

## Architecture

### Core Components

**Main Script: tts_generator.py**
- **Configuration Management** ([tts_generator.py:13-48](tts_generator.py#L13-L48)): Handles API key storage in config.json with fallback to .env file
- **Voice Selection System** ([tts_generator.py:54-88](tts_generator.py#L54-L88)): Interactive CLI for browsing and selecting from cloned, premium, and standard voices
- **Audio Processing Pipeline** ([tts_generator.py:169-213](tts_generator.py#L169-L213)): FFmpeg integration that:
  - Converts ElevenLabs MP3 output to WAV format
  - Prepends gong.wav with 250ms delay when available
  - Cleans up temporary files automatically
- **Batch Generator** ([tts_generator.py:215-283](tts_generator.py#L215-L283)): Processes all announcements with progress tracking and error handling

**Enhanced v2: tts_generator_enhanced_v2.py**
- **Dual Provider Support**: Supports both ElevenLabs (paid, high quality) and Google TTS (free, for testing)
- **TTS Caching System**: MD5-based cache prevents regenerating identical announcements
- **HOF Parser v2** ([tts_generator_enhanced_v2.py:138-290](tts_generator_enhanced_v2.py#L138-L290)):
  - Parses tab-separated stop definitions
  - Extracts `[infosystem_trip]` and `[infosystem_busstop_list]` sections
  - Handles complex stop naming (platform numbers, direction indicators)
  - Automatic next-stop detection from trip sequences
  - Line filtering (generate announcements for specific line only)
  - Proper terminus detection (last stop in sequence or `_KZ` suffix)
  - Multi-encoding support (CP1250, UTF-8, Latin1)

### Data Flow

1. Announcements are loaded from JSON with structure:
   ```json
   {
     "Station Name (optional: (konecna))": {
       "hlaseni": "Text to speak",
       "soubor": "output_filename"
     }
   }
   ```

2. ElevenLabs API converts text to MP3 format (44.1kHz, 128kbps) OR Google TTS generates MP3 (free testing)

3. FFmpeg processes the audio:
   - Converts MP3 → WAV (PCM 16-bit, 44.1kHz)
   - Adds gong.wav prefix with audio delay filter
   - Outputs to generated_audio/ directory

4. Files with "(konecna)" in station name get "_#terminus.wav" suffix

### External Dependencies

- **ElevenLabs API** (v0.2.24): TTS generation with voice cloning support (paid)
- **gTTS**: Free Google TTS for testing (optional, robotic voice quality)
- **FFmpeg**: Required for audio format conversion and gong concatenation (must be in PATH)
- **python-dotenv**: For .env file support (optional)

### Important Files

- **config.json**: Stores ElevenLabs API key
- **zastavky.json**: Default announcements file (Czech public transport stops)
- **zastavky_with_tags_example.json**: Example file demonstrating audio tag usage
- **gong.wav**: Optional audio file prepended to all announcements
- **nz.wav**: "Na znamení" (On signal) - signal/alert jingle for {nz} tag
- **pz.wav**: "Příští zastávka" (Next stop) - next stop indicator jingle for {pz} tag
- **kz.wav**: "Konečná zastávka" (Terminal stop) - terminal stop jingle for {kz} tag
- **template.wav**: Template audio file for reference
- **generated_audio/**: Output directory for all generated WAV files
- **tts_cache/**: MD5-cached TTS audio files (enhanced v2 only)
- **\*.hof**: OMSI HOF (Haltestellen-Objekt-Formatierung) files containing bus stop/route data

## Configuration

### Voice Settings Parameters
- **stability** (0.0-1.0): Voice consistency - higher values = more consistent but less expressive
- **similarity_boost** (0.0-1.0): How closely output matches original voice
- **style** (0.0-1.0): Exaggeration of speaking style
- **speed** (0.5-2.0): Playback speed multiplier (v2 only)
- **model_id**: "eleven_multilingual_v2" (default) or "eleven_turbo_v2_5" (faster)

### API Key Management
Priority order:
1. ELEVENLABS_API_KEY environment variable
2. .env file with ELEVENLABS_API_KEY
3. config.json "api_key" field
4. Interactive prompt (stores in config.json)

## Development Notes

### Audio Processing Details
The FFmpeg filter chain uses:
- `adelay=250|250`: Delays the TTS audio by 250ms on both channels
- `concat=n=2:v=0:a=1`: Concatenates gong + delayed TTS (audio only, no video)

This ensures the gong plays fully before the announcement starts.

### Caching System (Enhanced v2)
- Uses MD5 hash of (text + provider + settings) as cache key
- Stores cached files in `tts_cache/` directory
- Prevents redundant API calls for identical announcements
- Works with both ElevenLabs and Google TTS

### Error Handling
- All failed announcements are tracked and reported in summary
- Temporary files are cleaned up even on errors (finally block)
- Network errors and invalid API keys are caught with user-friendly messages

### Windows-Specific Considerations
This codebase is developed on Windows (win32) - be aware of:
- Path separators use `os.path.join()` for cross-platform compatibility
- FFmpeg must be accessible via PATH environment variable
- Virtual environment activation uses `venv\Scripts\activate`

## Enhanced Version Features

The enhanced version ([tts_generator_enhanced.py](tts_generator_enhanced.py)) adds:

### Audio Tag System
Embed tags in announcement text to insert pre-recorded audio files:
- `{nz}` - Inserts nz.wav (Na znamení - On signal) with 150ms delay before/after
- `{pz}` - Inserts pz.wav (Příští zastávka - Next stop) with 150ms delay before/after
- `{kz}` - Inserts kz.wav (Konečná zastávka - Terminal stop) with 150ms delay before/after

**Tag Processing Flow:**
1. Parse announcement text to extract tags and text segments
2. Generate TTS only for text portions (tags removed)
3. Build FFmpeg filter chain: gong → [tag + 150ms silence] → TTS → [tag + 150ms silence] → ...
4. Output combined WAV file

Example JSON:
```json
{
  "Station": {
    "hlaseni": "{nz} Zastávka: Nádraží. {pz} Příští: Centrum.",
    "soubor": "nadrazi"
  }
}
```

### HOF File Support
Parse OMSI HOF files to auto-generate announcements:
- Extracts `[addterminus]` and `[addterminus_allexit]` → terminus announcements (v1)
- Extracts `[addbusstop]` → regular stop announcements (v1)
- Auto-generates Czech announcement text
- Uses IBIS codes for filename prefixes
- Marks terminus stops with `_#terminus.wav` suffix

**HOF Parser v1** ([tts_generator_enhanced.py:143-185](tts_generator_enhanced.py#L143-L185)):
- Basic regex-based extraction of stop definitions
- Filename sanitization (removes special characters)
- Generates appropriate announcement templates in Czech

**HOF Parser v2** ([tts_generator_enhanced_v2.py:138-290](tts_generator_enhanced_v2.py#L138-L290)) - **Recommended**:
- Parses tab-separated stop definitions
- Extracts `[infosystem_trip]` and `[infosystem_busstop_list]` sections
- Handles complex stop naming (platform numbers, direction indicators)
- Automatic next-stop detection from trip sequences
- Line filtering (generate announcements for specific line only)
- Proper terminus detection (last stop in sequence or `_KZ` suffix)
- Multi-encoding support (CP1250, UTF-8, Latin1)

### HOF File Structure

OMSI HOF files contain:
- **Stop Definitions**: Tab-separated values with stop ID, display name, line number
- **Trip Sections**: Groups of stops defining a specific route/direction
- **Naming Conventions**:
  - City lines: `[StationName]_[Platform]` (e.g., `Kosmonautů_1`)
  - Intercity: `[Line]_[CurrentStop]_[NextStop]` (e.g., `31_BnLAuto_Husova`)
  - Terminus markers: `_KZ` suffix

See [HOF_PARSING_GUIDE.md](HOF_PARSING_GUIDE.md) for comprehensive HOF structure documentation and [README_ENHANCED.md](README_ENHANCED.md) for usage instructions.

## Version Selection Guide

Use [VERSIONS_SUMMARY.md](VERSIONS_SUMMARY.md) to determine which version to use:

- **tts_generator.py**: Simple JSON-only processing
- **tts_generator_enhanced.py**: JSON with audio tags, basic HOF support
- **tts_generator_enhanced_v2.py**: Full HOF support, line filtering, next-stop detection, free Google TTS testing mode

## Testing Without Paid API

Enhanced v2 includes free Google TTS testing mode:
1. Select option "2. Google TTS (Free - Testing/Robotic)" when prompted
2. No API key required
3. Lower quality robotic voice, but useful for testing announcement text and audio processing pipeline
4. Caches generated audio to avoid redundant generation
