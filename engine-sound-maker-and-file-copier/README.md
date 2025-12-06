# Engine Sound & File Tools for OMSI / Nástroje pro zvuky a soubory OMSI

[🇨🇿 Česká verze](#česká-verze) | [🇬🇧 English Version](#english-version)

---

## 🇨🇿 Česká verze

Kolekce nástrojů pro práci s OMSI Bus Simulator.

### 📦 Obsah

---

## 📁 OMSI File Copier

**GUI nástroj pro hromadné kopírování OMSI souborů a modelů.**

### 🔗 [📖 Detailní návod → README_FILE_COPIER.md](README_FILE_COPIER.md)

Kompletní průvodce s krokovým návodem, tipy a řešením problémů.

### ⚡ Rychlý přehled

**Funguje nejlépe s výstupem z OMSI-Tools:**

![Jak získat formát z OMSI-Tools](https://s3-server.ente.odjezdy.online/raw/mPTh37.gif)

```
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_1\BL1.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_2\BL2.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Lazurowa_2\Bl_Laz_2.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Lazurowa_3\Bl_Laz_3.sco
Sceneryobjects\251_VelkeOpatovice-Kninice\Budka_CTK.sco
```

**Hlavní funkce:**
- 📋 Automatická detekce root složek
- 🔄 Hromadné kopírování sceneryobjects
- 📊 Progress tracking
- ✅ Verifikace zkopírovaných souborů
- 🔗 Kompatibilní s OMSI-Tools výstupem

**Rychlý start:**
```bash
pip install -r requirements.txt
python omsi_file_copier.py
```

**📖 Pro detailní návod viz [README_FILE_COPIER.md](README_FILE_COPIER.md)**

---

## 🎵 Engine Sound Extractor

**Extrahuje a zpracovává motorové zvuky z videa pomocí AI.**

### 🔗 [📖 Detailní TUI návod → README_TUI.md](README_TUI.md)

### ⚡ Rychlý přehled

**Tři způsoby použití:**
- 🖥️ **GUI** - Drag & drop aplikace pro Windows (`engine_sound_extractor.py`)
- 💻 **TUI** - Terminálová verze (`engine_extractor_tui.py`)
- ☁️ **Google Colab** - Cloud s GPU zdarma (`Engine_Sound_Extractor_Colab.ipynb`)

**Hlavní funkce:**
- 🤖 **AI Separace (Demucs)** - Odstraní hlas, hudbu, okolní hluk
- 🎯 **AI Klasifikace (YAMNet)** - Přesná detekce motorových zvuků
- 🔧 **Klasický noise reduction** - Rychlá metoda
- 📊 **Frekvenční filtrování** - Izoluje motorové frekvence (80-500 Hz)
- 🔢 **RPM Segmentace** - Automatické rozdělení podle otáček
- ⚡ **GPU Akcelerace** - 10x rychlejší v Google Colab

**Podporované motory:**
- FPT NEF 6 (184kW, 210kW) - SOR BN 9.5/10.5/12
- FPT NEF 4 - SOR BN 8.5
- FPT Cursor 8/9 - SOR NB 12/18
- IVECO Cursor 8 - Starší SOR
- Mercedes OM906, Cummins ISBe/ISL
- Obecné 4V/6V diesely

---

### 🚀 Rychlý start

#### OMSI File Copier

```bash
pip install -r requirements.txt
python omsi_file_copier.py
```

#### Engine Sound Extractor (GUI)

```bash
pip install -r requirements.txt
python engine_sound_extractor.py
```

#### Engine Sound Extractor (TUI - všechny platformy)

```bash
pip install -r requirements_tui.txt
python engine_extractor_tui.py -i  # Interaktivní režim
```

#### Engine Sound Extractor (Google Colab - doporučeno pro AI)

1. Otevři `Engine_Sound_Extractor_Colab.ipynb` v Google Colab
2. Runtime → Change runtime type → **GPU**
3. Runtime → Run all
4. Nahraj video a počkej na výsledky

---

### 📋 Engine Sound Extractor - TUI Parametry CLI

**Základní použití:**
```bash
python engine_extractor_tui.py video.mp4
```

**S parametry:**
```bash
python engine_extractor_tui.py video.mp4 \
  -o output/ \
  -m ai_demucs \
  --model htdemucs \
  --freq-low 80 \
  --freq-high 500 \
  -e iveco_cursor8 \
  -s 5
```

**Všechny parametry:**

| Parametr | Popis | Default |
|----------|-------|---------|
| `video` | Cesta k video souboru | - |
| `-o, --output` | Výstupní složka | `./engine_sounds` |
| `-m, --method` | `classic`, `ai_demucs`, `ai_yamnet` | `ai_demucs` |
| `--model` | AI model: `htdemucs`, `htdemucs_ft`, `mdx_extra` | `htdemucs` |
| `-n, --noise` | Úroveň noise reduction (0-100) | `50` |
| `--freq-low` | Dolní frekvence (Hz) | `80` |
| `--freq-high` | Horní frekvence (Hz) | `500` |
| `-e, --engine` | Typ motoru (viz seznam) | `iveco_cursor8` |
| `--no-full` | Neexportovat kompletní zvuk | `False` |
| `--no-segments` | Neexportovat segmenty | `False` |
| `-s, --segments` | Počet segmentů (2-20) | `5` |
| `-i, --interactive` | Interaktivní režim | `False` |

---

### 🔧 Engine Sound Extractor - Porovnání metod

| Metoda | Rychlost (20min video) | Kvalita | GPU |
|--------|------------------------|---------|-----|
| **Classic** | 5-7 min | ⭐⭐ | Ne |
| **AI Demucs** | 60-90 min (CPU) / 10-15 min (GPU) | ⭐⭐⭐⭐⭐ | Ano |
| **AI YAMNet** | 15-20 min (CPU) / 5-10 min (GPU) | ⭐⭐⭐⭐ | Ano |

**💡 Doporučení:** Použij **Google Colab s GPU** pro AI metody - je to **10x rychlejší a zdarma**!

---

### 🎯 Engine Sound Extractor - Použití v OMSI

1. **Zkopíruj výsledné soubory:**
```
Vehicles\[tvůj_autobus]\sound\
  ├── engine_sound_full.wav
  ├── engine_600rpm.wav
  ├── engine_1200rpm.wav
  ├── engine_1800rpm.wav
  └── engine_2400rpm.wav
```

2. **Uprav `sound.cfg`:**
```ini
[engine]
idle=engine_600rpm.wav
low=engine_1200rpm.wav
medium=engine_1800rpm.wav
high=engine_2400rpm.wav

[engine_parameters]
idle_rpm=600
low_rpm=1200
medium_rpm=1800
high_rpm=2400
```

3. **Testuj v OMSI** a případně uprav RPM thresholdy

---

### 🛠️ Požadavky

**Pro OMSI File Copier:**
- Python 3.7+
- PySide6
- Balíčky: `pip install -r requirements.txt`

**Pro Engine Sound Extractor (GUI):**
- Python 3.10+
- FFmpeg
- Balíčky: `pip install -r requirements.txt`

**Pro Engine Sound Extractor (TUI):**
- Python 3.10+
- FFmpeg
- Balíčky: `pip install -r requirements_tui.txt`

**Pro Google Colab:**
- Žádné (vše v cloudu)
- Pouze Google účet

---

### 🐛 Řešení problémů

**"FFmpeg not found"**
```bash
# Windows
winget install ffmpeg

# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt      # pro File Copier nebo GUI
pip install -r requirements_tui.txt  # pro TUI
```

**Engine Sound Extractor - Špatná kvalita výstupu**
- Použij AI separaci (Demucs) místo classic
- Zvyš noise reduction (50-80%)
- Uprav frekvenční rozsah podle typu motoru

**Engine Sound Extractor - Pitch detection selhává (dlouhá videa)**
- Automaticky použije fallback (rovnoměrné rozdělení)
- Nebo použij Google Colab s více RAM

**OMSI File Copier - Podrobné řešení problémů viz [README_FILE_COPIER.md](README_FILE_COPIER.md)**

---

### 📚 Dokumentace

- **[README_FILE_COPIER.md](README_FILE_COPIER.md)** - 📁 Detailní návod pro OMSI File Copier
- **[README_TUI.md](README_TUI.md)** - 🎵 Detailní TUI dokumentace pro Engine Sound Extractor
- **[Engine_Sound_Extractor_Colab.ipynb](Engine_Sound_Extractor_Colab.ipynb)** - ☁️ Google Colab notebook

---

## 🇬🇧 English Version

Collection of tools for working with OMSI Bus Simulator.

### 📦 Contents

---

## 📁 OMSI File Copier

**GUI tool for batch copying OMSI files and models.**

### 🔗 [📖 Detailed guide → README_FILE_COPIER.md](README_FILE_COPIER.md)

Complete guide with step-by-step instructions, tips, and troubleshooting.

### ⚡ Quick Overview

**Works best with OMSI-Tools output:**

![How to get format from OMSI-Tools](https://s3-server.ente.odjezdy.online/raw/mPTh37.gif)

```
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_1\BL1.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_2\BL2.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Lazurowa_2\Bl_Laz_2.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Lazurowa_3\Bl_Laz_3.sco
Sceneryobjects\251_VelkeOpatovice-Kninice\Budka_CTK.sco
```

**Key Features:**
- 📋 Automatic root folder detection
- 🔄 Batch copying of sceneryobjects
- 📊 Progress tracking
- ✅ Verification of copied files
- 🔗 Compatible with OMSI-Tools output

**Quick Start:**
```bash
pip install -r requirements.txt
python omsi_file_copier.py
```

**📖 For detailed instructions see [README_FILE_COPIER.md](README_FILE_COPIER.md)**

---

## 🎵 Engine Sound Extractor

**Extracts and processes engine sounds from videos using AI.**

### 🔗 [📖 Detailed TUI guide → README_TUI.md](README_TUI.md)

### ⚡ Quick Overview

**Three usage modes:**
- 🖥️ **GUI** - Drag & drop application for Windows (`engine_sound_extractor.py`)
- 💻 **TUI** - Terminal version (`engine_extractor_tui.py`)
- ☁️ **Google Colab** - Cloud with free GPU (`Engine_Sound_Extractor_Colab.ipynb`)

**Key Features:**
- 🤖 **AI Separation (Demucs)** - Removes voice, music, ambient noise
- 🎯 **AI Classification (YAMNet)** - Precise engine sound detection
- 🔧 **Classic noise reduction** - Fast method
- 📊 **Frequency filtering** - Isolates engine frequencies (80-500 Hz)
- 🔢 **RPM Segmentation** - Automatic splitting by RPM
- ⚡ **GPU Acceleration** - 10x faster in Google Colab

**Supported Engines:**
- FPT NEF 6 (184kW, 210kW) - SOR BN 9.5/10.5/12
- FPT NEF 4 - SOR BN 8.5
- FPT Cursor 8/9 - SOR NB 12/18
- IVECO Cursor 8 - Older SOR
- Mercedes OM906, Cummins ISBe/ISL
- Generic 4cyl/6cyl diesels

---

### 🚀 Quick Start

#### OMSI File Copier

```bash
pip install -r requirements.txt
python omsi_file_copier.py
```

#### Engine Sound Extractor (GUI)

```bash
pip install -r requirements.txt
python engine_sound_extractor.py
```

#### Engine Sound Extractor (TUI - all platforms)

```bash
pip install -r requirements_tui.txt
python engine_extractor_tui.py -i  # Interactive mode
```

#### Engine Sound Extractor (Google Colab - recommended for AI)

1. Open `Engine_Sound_Extractor_Colab.ipynb` in Google Colab
2. Runtime → Change runtime type → **GPU**
3. Runtime → Run all
4. Upload video and wait for results

---

### 📋 Engine Sound Extractor - TUI CLI Parameters

**Basic usage:**
```bash
python engine_extractor_tui.py video.mp4
```

**With parameters:**
```bash
python engine_extractor_tui.py video.mp4 \
  -o output/ \
  -m ai_demucs \
  --model htdemucs \
  --freq-low 80 \
  --freq-high 500 \
  -e iveco_cursor8 \
  -s 5
```

**All parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `video` | Path to video file | - |
| `-o, --output` | Output folder | `./engine_sounds` |
| `-m, --method` | `classic`, `ai_demucs`, `ai_yamnet` | `ai_demucs` |
| `--model` | AI model: `htdemucs`, `htdemucs_ft`, `mdx_extra` | `htdemucs` |
| `-n, --noise` | Noise reduction level (0-100) | `50` |
| `--freq-low` | Low frequency (Hz) | `80` |
| `--freq-high` | High frequency (Hz) | `500` |
| `-e, --engine` | Engine type (see list) | `iveco_cursor8` |
| `--no-full` | Don't export full sound | `False` |
| `--no-segments` | Don't export segments | `False` |
| `-s, --segments` | Number of segments (2-20) | `5` |
| `-i, --interactive` | Interactive mode | `False` |

---

### 🔧 Engine Sound Extractor - Method Comparison

| Method | Speed (20min video) | Quality | GPU |
|--------|---------------------|---------|-----|
| **Classic** | 5-7 min | ⭐⭐ | No |
| **AI Demucs** | 60-90 min (CPU) / 10-15 min (GPU) | ⭐⭐⭐⭐⭐ | Yes |
| **AI YAMNet** | 15-20 min (CPU) / 5-10 min (GPU) | ⭐⭐⭐⭐ | Yes |

**💡 Recommendation:** Use **Google Colab with GPU** for AI methods - it's **10x faster and free**!

---

### 🎯 Engine Sound Extractor - Usage in OMSI

1. **Copy result files:**
```
Vehicles\[your_bus]\sound\
  ├── engine_sound_full.wav
  ├── engine_600rpm.wav
  ├── engine_1200rpm.wav
  ├── engine_1800rpm.wav
  └── engine_2400rpm.wav
```

2. **Edit `sound.cfg`:**
```ini
[engine]
idle=engine_600rpm.wav
low=engine_1200rpm.wav
medium=engine_1800rpm.wav
high=engine_2400rpm.wav

[engine_parameters]
idle_rpm=600
low_rpm=1200
medium_rpm=1800
high_rpm=2400
```

3. **Test in OMSI** and adjust RPM thresholds if needed

---

### 🛠️ Requirements

**For OMSI File Copier:**
- Python 3.7+
- PySide6
- Packages: `pip install -r requirements.txt`

**For Engine Sound Extractor (GUI):**
- Python 3.10+
- FFmpeg
- Packages: `pip install -r requirements.txt`

**For Engine Sound Extractor (TUI):**
- Python 3.10+
- FFmpeg
- Packages: `pip install -r requirements_tui.txt`

**For Google Colab:**
- None (everything in cloud)
- Only Google account

---

### 🐛 Troubleshooting

**"FFmpeg not found"**
```bash
# Windows
winget install ffmpeg

# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt      # for File Copier or GUI
pip install -r requirements_tui.txt  # for TUI
```

**Engine Sound Extractor - Poor output quality**
- Use AI separation (Demucs) instead of classic
- Increase noise reduction (50-80%)
- Adjust frequency range for engine type

**Engine Sound Extractor - Pitch detection fails (long videos)**
- Automatically uses fallback (equal distribution)
- Or use Google Colab with more RAM

**OMSI File Copier - Detailed troubleshooting see [README_FILE_COPIER.md](README_FILE_COPIER.md)**

---

### 📚 Documentation

- **[README_FILE_COPIER.md](README_FILE_COPIER.md)** - 📁 Detailed guide for OMSI File Copier
- **[README_TUI.md](README_TUI.md)** - 🎵 Detailed TUI documentation for Engine Sound Extractor
- **[Engine_Sound_Extractor_Colab.ipynb](Engine_Sound_Extractor_Colab.ipynb)** - ☁️ Google Colab notebook

---

## 📄 License

MIT License - see individual files for details

## 🤝 Contributing

Contributions welcome! Feel free to open issues or pull requests.

---

**Vytvořeno pro OMSI Bus Simulator komunitu** 🚌❤️
**Created for OMSI Bus Simulator community** 🚌❤️
