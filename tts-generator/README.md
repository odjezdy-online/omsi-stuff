# TTS Generátor pro Veřejnou Dopravu / Public Transport TTS Generator

[🇨🇿 Česká verze](#česká-verze) | [🇬🇧 English Version](#english-version)

---

## 🇨🇿 Česká verze

Python skript pro generování hlášení pomocí ElevenLabs API nebo Google TTS. Speciálně navržen pro hlášení veřejné dopravy s podporou OMSI HOF souborů.

### ✨ Funkce

- 🎙️ **Tři verze skriptu** - od základní až po plně vybavenou
- 🔊 **Podpora audio značek** - vkládání vlastních audio souborů ({nz}, {pz}, {kz})
- 🚌 **OMSI HOF parser** - automatické generování hlášení z HOF souborů
- 🆓 **Testovací režim zdarma** - Google TTS pro testování bez API klíče
- 🎯 **Filtrování podle linek** - generování pouze pro vybranou linku
- 💾 **Inteligentní cache** - neopakuje generování stejných hlášení
- 🌍 **Vícejazyčné hlasy** - včetně podpory češtiny
- ⚡ **Hromadné zpracování** - zpracuje všechna hlášení najednou

### 📦 Verze

| Verze | Soubor | Popis |
|-------|--------|-------|
| **Základní** | `tts_generator.py` | Jednoduchý JSON → TTS převod |
| **Rozšířená** | `tts_generator_enhanced.py` | + audio značky, základní HOF |
| **Rozšířená v2** ⭐ | `tts_generator_enhanced_v2.py` | + pokročilý HOF parser, Google TTS zdarma |

👉 **Doporučujeme:** `tts_generator_enhanced_v2.py` - nejnovější verze se všemi funkcemi

📖 **Podrobné srovnání:** [VERSIONS_SUMMARY.md](VERSIONS_SUMMARY.md)

### 🚀 Rychlý start

#### 1. Instalace

```bash
# Klonování repozitáře
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Vytvoření virtuálního prostředí
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalace závislostí
pip install -r requirements.txt
```

#### 2. Konfigurace API klíče (volitelné pro testování)

**Pro ElevenLabs (placené, vysoká kvalita):**
```bash
# Zkopírujte ukázkový config
copy config.json.example config.json

# Upravte config.json a vložte svůj API klíč
# Získejte klíč na: https://elevenlabs.io
```

**Pro Google TTS (zdarma, robotický hlas):**
```bash
# Není potřeba API klíč - vyberte při spuštění
```

#### 3. Spuštění

```bash
# Doporučená verze (s HOF podporou + testování zdarma)
python tts_generator_enhanced_v2.py

# Základní verze (pouze JSON)
python tts_generator.py
```

### 📋 Formát JSON

```json
{
  "Název zastávky": {
    "hlaseni": "Zastávka: Nádraží. Příští zastávka: Centrum.",
    "soubor": "nadrazi"
  },
  "Konečná (konecna)": {
    "hlaseni": "Konečná zastávka: Terminál. Prosíme, vystupte.",
    "soubor": "terminal"
  }
}
```

**S audio značkami:**
```json
{
  "Zastávka": {
    "hlaseni": "{nz} Zastávka: Nádraží. {pz} Příští: Centrum.",
    "soubor": "nadrazi"
  }
}
```

Značky:
- `{nz}` - Na znamení (vloží nz.wav)
- `{pz}` - Příští zastávka (vloží pz.wav)
- `{kz}` - Konečná zastávka (vloží kz.wav)

### 🚌 OMSI HOF Soubory

Rozšířená verze v2 umí parsovat OMSI HOF soubory a automaticky generovat hlášení:

```bash
python tts_generator_enhanced_v2.py
# Vyberte: 2. HOF file (OMSI bus stop file)
# Zvolte HOF soubor
# Volitelně filtrujte podle linky
```

**Co extrahuje:**
- ✅ Názvy zastávek z `[infosystem_trip]` sekcí
- ✅ Pořadí zastávek pro detekci "příští zastávky"
- ✅ Konečné zastávky (poslední nebo `_KZ`)
- ✅ Čísla linek pro filtrování

📖 **Podrobný průvodce:** [HOF_PARSING_GUIDE.md](HOF_PARSING_GUIDE.md)

### 🎵 Audio Soubory

Umístěte do hlavní složky:
- `gong.wav` - Úvodní zvuk (volitelné)
- `nz.wav` - "Na znamení" jingle
- `pz.wav` - "Příští zastávka" jingle
- `kz.wav` - "Konečná zastávka" jingle

**Doporučený formát:** WAV, 44.1kHz, mono/stereo

### 🛠️ Požadavky

- **Python 3.7+**
- **FFmpeg** (musí být v PATH)
- **ElevenLabs API klíč** (volitelné - jen pro placenou verzi)

### 📚 Dokumentace

- [README_ENHANCED.md](README_ENHANCED.md) - Rozšířené funkce
- [HOF_PARSING_GUIDE.md](HOF_PARSING_GUIDE.md) - Struktura HOF souborů
- [VERSIONS_SUMMARY.md](VERSIONS_SUMMARY.md) - Srovnání verzí
- [CLAUDE.md](CLAUDE.md) - Developer dokumentace

### 🐛 Řešení problémů

**"FFmpeg not found"**
```bash
# Stáhněte FFmpeg z: https://ffmpeg.org/download.html
# Přidejte do PATH
```

**"API key invalid"**
```bash
# Zkontrolujte config.json
# Nebo použijte Google TTS (zdarma)
```

**"HOF file parsing errors"**
```bash
# Použijte enhanced v2 verzi
# Zkontrolujte kódování souboru (CP1250/UTF-8)
```

### 📄 Licence

MIT License - viz [LICENSE](LICENSE)

---

## 🇬🇧 English Version

Python script for generating Text-to-Speech announcements using ElevenLabs API or Google TTS. Specifically designed for public transport announcements with OMSI HOF file support.

### ✨ Features

- 🎙️ **Three script versions** - from basic to fully featured
- 🔊 **Audio tag support** - insert custom audio files ({nz}, {pz}, {kz})
- 🚌 **OMSI HOF parser** - auto-generate announcements from HOF files
- 🆓 **Free testing mode** - Google TTS for testing without API key
- 🎯 **Line filtering** - generate only for specific bus line
- 💾 **Smart caching** - avoids regenerating identical announcements
- 🌍 **Multilingual voices** - including Czech support
- ⚡ **Batch processing** - processes all announcements at once

### 📦 Versions

| Version | File | Description |
|---------|------|-------------|
| **Original** | `tts_generator.py` | Simple JSON → TTS conversion |
| **Enhanced** | `tts_generator_enhanced.py` | + audio tags, basic HOF |
| **Enhanced v2** ⭐ | `tts_generator_enhanced_v2.py` | + advanced HOF parser, free Google TTS |

👉 **Recommended:** `tts_generator_enhanced_v2.py` - latest version with all features

📖 **Detailed comparison:** [VERSIONS_SUMMARY.md](VERSIONS_SUMMARY.md)

### 🚀 Quick Start

#### 1. Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure API Key (optional for testing)

**For ElevenLabs (paid, high quality):**
```bash
# Copy example config
copy config.json.example config.json

# Edit config.json and insert your API key
# Get key at: https://elevenlabs.io
```

**For Google TTS (free, robotic voice):**
```bash
# No API key needed - select when running
```

#### 3. Run

```bash
# Recommended version (with HOF support + free testing)
python tts_generator_enhanced_v2.py

# Basic version (JSON only)
python tts_generator.py
```

### 📋 JSON Format

```json
{
  "Station Name": {
    "hlaseni": "Stop: Station. Next stop: Center.",
    "soubor": "station"
  },
  "Terminal (konecna)": {
    "hlaseni": "Terminal stop: Terminal. Please exit.",
    "soubor": "terminal"
  }
}
```

**With audio tags:**
```json
{
  "Station": {
    "hlaseni": "{nz} Stop: Station. {pz} Next: Center.",
    "soubor": "station"
  }
}
```

Tags:
- `{nz}` - Signal (inserts nz.wav)
- `{pz}` - Next stop (inserts pz.wav)
- `{kz}` - Terminal stop (inserts kz.wav)

### 🚌 OMSI HOF Files

Enhanced v2 can parse OMSI HOF files and auto-generate announcements:

```bash
python tts_generator_enhanced_v2.py
# Select: 2. HOF file (OMSI bus stop file)
# Choose HOF file
# Optionally filter by line
```

**What it extracts:**
- ✅ Stop names from `[infosystem_trip]` sections
- ✅ Stop sequences for "next stop" detection
- ✅ Terminal stops (last or `_KZ`)
- ✅ Line numbers for filtering

📖 **Detailed guide:** [HOF_PARSING_GUIDE.md](HOF_PARSING_GUIDE.md)

### 🎵 Audio Files

Place in main folder:
- `gong.wav` - Intro sound (optional)
- `nz.wav` - Signal jingle
- `pz.wav` - Next stop jingle
- `kz.wav` - Terminal stop jingle

**Recommended format:** WAV, 44.1kHz, mono/stereo

### 🛠️ Requirements

- **Python 3.7+**
- **FFmpeg** (must be in PATH)
- **ElevenLabs API key** (optional - only for paid version)

### 📚 Documentation

- [README_ENHANCED.md](README_ENHANCED.md) - Enhanced features
- [HOF_PARSING_GUIDE.md](HOF_PARSING_GUIDE.md) - HOF file structure
- [VERSIONS_SUMMARY.md](VERSIONS_SUMMARY.md) - Version comparison
- [CLAUDE.md](CLAUDE.md) - Developer documentation

### 🐛 Troubleshooting

**"FFmpeg not found"**
```bash
# Download FFmpeg from: https://ffmpeg.org/download.html
# Add to PATH
```

**"API key invalid"**
```bash
# Check config.json
# Or use Google TTS (free)
```

**"HOF file parsing errors"**
```bash
# Use enhanced v2 version
# Check file encoding (CP1250/UTF-8)
```

### 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⭐ Support

If you find this project useful, please consider giving it a star on GitHub!
