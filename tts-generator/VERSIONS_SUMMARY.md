# TTS Generator Versions Summary

## Quick Comparison

| Feature | Original | Enhanced v1 | Enhanced v2 (Recommended) |
|---------|----------|-------------|---------------------------|
| **File** | `tts_generator.py` | `tts_generator_enhanced.py` | `tts_generator_enhanced_v2.py` |
| **JSON Support** | ✅ Basic | ✅ With tags | ✅ With tags |
| **Audio Tags** | ❌ | ✅ {nz}, {pz}, {kz} | ✅ {nz}, {pz}, {kz} |
| **HOF Support** | ❌ | ⚠️ Basic | ✅ Full |
| **Trip Parsing** | ❌ | ❌ | ✅ |
| **Line Filtering** | ❌ | ❌ | ✅ |
| **Next Stop Detection** | ❌ | ❌ | ✅ |
| **Encoding Support** | UTF-8 | UTF-8 | CP1250, UTF-8, Latin1 |

## When to Use Each Version

### Original (`tts_generator.py`)
✅ **Use when:**
- You only have JSON files
- You don't need audio tags
- You want the simplest, most stable version

❌ **Don't use when:**
- You need to parse HOF files
- You want to insert audio jingles

### Enhanced v1 (`tts_generator_enhanced.py`)
✅ **Use when:**
- You need audio tags ({nz}, {pz}, {kz})
- You have simple HOF files with basic structure
- You're working with JSON files and want tag support

❌ **Don't use when:**
- You have complex HOF files with trip definitions
- You need line-specific filtering

### Enhanced v2 (`tts_generator_enhanced_v2.py`) ⭐ **RECOMMENDED**
✅ **Use when:**
- You're working with OMSI HOF files
- You need automatic next-stop detection
- You want to filter announcements by line number
- You need proper handling of platform/direction naming
- You want all features (tags + HOF + filtering)

❌ **Don't use when:**
- You prefer maximum simplicity (use original instead)

## Audio Tag System

All enhanced versions support audio tags:

### Supported Tags
- **{nz}** - Na znamení (On signal) - Alert/signal jingle
- **{pz}** - Příští zastávka (Next stop) - Next stop indicator
- **{kz}** - Konečná zastávka (Terminal) - Terminal stop jingle

### Tag Processing
1. Tags are removed from TTS text
2. Only text portions sent to ElevenLabs
3. FFmpeg inserts tagged audio with 150ms delays
4. Final audio combines: gong → tags → TTS → tags

### Example
```json
{
  "Station": {
    "hlaseni": "{nz} Zastávka: Nádraží. {pz} Příští: Centrum.",
    "soubor": "nadrazi"
  }
}
```

## HOF File Support

### Enhanced v1 - Basic Parsing
- Extracts `[addterminus]` and `[addbusstop]` sections
- Simple regex-based extraction
- No trip/sequence information
- No line filtering

### Enhanced v2 - Full Parsing ⭐
- Parses tab-separated stop definitions
- Reads `[infosystem_trip]` sections
- Extracts `[infosystem_busstop_list]` sequences
- Automatic next-stop detection
- Line number filtering
- Handles complex naming:
  - Platform numbers (`Kosmonautů_1`, `Kosmonautů_2`)
  - Directional names (`31_BnLAuto_Husova`, `31_Husova_Namesti`)
  - Terminus markers (`_KZ`)

## Migration Guide

### From Original → Enhanced v1
1. Backup your `zastavky.json`
2. Add audio tags to `hlaseni` fields if desired
3. Place `nz.wav`, `pz.wav`, `kz.wav` in directory
4. Run `python tts_generator_enhanced.py`

### From Original → Enhanced v2
1. Same as above, OR
2. Use HOF file instead of JSON:
   - Select option "2" when prompted
   - Choose your `.hof` file
   - Optionally filter by line number

### From Enhanced v1 → Enhanced v2
- Both versions have identical JSON/tag functionality
- v2 adds improved HOF parsing
- Simply switch to running `tts_generator_enhanced_v2.py`

## File Requirements

### All Versions
- `config.json` - API key storage (auto-created)
- `requirements.txt` - Python dependencies
- FFmpeg in PATH

### Enhanced Versions (v1 & v2)
Optional audio files:
- `gong.wav` - Intro sound (all announcements)
- `nz.wav` - "Na znamení" jingle
- `pz.wav` - "Příští zastávka" jingle
- `kz.wav` - "Konečná zastávka" jingle

## Command Reference

```bash
# Original version
python tts_generator.py

# Enhanced v1
python tts_generator_enhanced.py

# Enhanced v2 (recommended)
python tts_generator_enhanced_v2.py
```

## Documentation

- **[README.md](README.md)** - Original version docs
- **[README_ENHANCED.md](README_ENHANCED.md)** - Enhanced features overview
- **[HOF_PARSING_GUIDE.md](HOF_PARSING_GUIDE.md)** - Detailed HOF file structure
- **[CLAUDE.md](CLAUDE.md)** - Developer documentation

## Troubleshooting

### "Audio tags not working"
- Ensure `nz.wav`, `pz.wav`, `kz.wav` exist
- Check WAV format (44.1kHz recommended)
- Verify FFmpeg is installed

### "HOF file not parsing"
- Use Enhanced v2 (v1 has limited HOF support)
- Check file encoding (should be CP1250 or UTF-8)
- Verify `[infosystem_trip]` sections exist

### "Missing next stop information"
- Only Enhanced v2 detects next stops
- Requires properly formatted `[infosystem_busstop_list]`
- Falls back to basic announcement if no next stop

## Version History

- **v1.0** - Original `tts_generator.py`
  - Basic JSON support
  - Gong prepending
  - Terminus detection

- **v2.0** - Enhanced `tts_generator_enhanced.py`
  - Audio tag system added
  - Basic HOF parsing
  - Tag-based audio insertion

- **v2.1** - Enhanced v2 `tts_generator_enhanced_v2.py` ⭐
  - Full HOF trip parsing
  - Line filtering
  - Next-stop detection
  - Multi-encoding support
  - Platform/direction handling
