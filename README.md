# OMSI Stuff

Kolekce nástrojů a utilit pro OMSI 2 (Omni Bus Simulator) / Collection of tools and utilities for OMSI 2 (Omni Bus Simulator)

[🇨🇿 Česky](#česká-verze) | [🇬🇧 English](#english-version)

---

## 🇨🇿 Česká verze

Sbírka užitečných nástrojů pro práci s OMSI 2 simulátorem autobusů.

### 📦 Projekty

#### 🎙️ [TTS Generator](tts-generator/)
Generátor hlášení pro veřejnou dopravu pomocí ElevenLabs API nebo Google TTS.

**Hlavní funkce:**
- 🚌 Automatické parsování OMSI HOF souborů
- 🔊 Podpora audio značek ({nz}, {pz}, {kz})
- 🆓 Testování zdarma s Google TTS
- 🎯 Filtrování podle linek
- 💾 Inteligentní cache systém
- 🌍 Vícejazyčné hlasy (včetně češtiny)

**Status:** ✅ Aktivní vývoj
**Verze:** 2.1 (Enhanced v2)
**Dokumentace:** [README](tts-generator/README.md)

---

#### 🎵 [Engine Sound Maker & File Tools](engine-sound-maker-and-file-copier/)
Nástroje pro práci se zvuky motorů a soubory OMSI.

**Hlavní funkce:**
- 🤖 **AI Engine Sound Extractor** - Extrakce motorových zvuků z videa
  - Demucs AI separace (odstraní hlas, hudbu, okolí)
  - YAMNet AI klasifikace (přesná detekce engine sounds)
  - RPM segmentace - automatické rozdělení podle otáček
  - GUI / TUI / Google Colab verze
  - ⚡ GPU akcelerace (10x rychlejší v Colab)
- 📁 **OMSI File Copier** - Hromadné kopírování OMSI souborů
  - Kompatibilní s OMSI-Tools výstupem
  - Automatická detekce root složek
  - Progress tracking a verifikace

**Podporované motory:**
- FPT NEF 6 (SOR BN 9.5/10.5/12)
- FPT Cursor 8/9 (SOR NB 12/18)
- IVECO Cursor 8, Mercedes OM906
- Cummins ISBe/ISL
- Obecné 4V/6V diesely

**Status:** ✅ Aktivní vývoj
**Verze:** 2.0 (TUI + Colab)
**Dokumentace:** [README](engine-sound-maker-and-file-copier/README.md) | [README_TUI](engine-sound-maker-and-file-copier/README_TUI.md)

---

### 🚀 Rychlý start

```bash
# Klonuj repozitář
git clone https://github.com/odjezdy-online/omsi-stuff.git
cd omsi-stuff

# TTS Generator
cd tts-generator
pip install -r requirements.txt
python tts_generator_enhanced_v2.py

# Engine Sound Extractor (GUI)
cd engine-sound-maker-and-file-copier
pip install -r requirements.txt
python engine_sound_extractor.py

# Engine Sound Extractor (TUI - cross-platform)
pip install -r requirements_tui.txt
python engine_extractor_tui.py -i

# OMSI File Copier
python omsi_file_copier.py
```

---

### 🛠️ Plánované projekty

- 🗺️ **Map Tools** - Nástroje pro práci s mapami OMSI
- 🎨 **Repaint Manager** - Správce repaintů vozidel
- 📊 **Route Analyzer** - Analýza tras a jízdních řádů
- 🔧 **Config Editor** - Editor konfiguračních souborů
- 🚦 **Traffic Light Editor** - Editor světelných signalizací

---

### 🤝 Přispívání

Příspěvky jsou vítány! Pokud máš nápad na nový nástroj nebo vylepšení, neváhejte otevřít Issue nebo Pull Request.

**Jak přispět:**
1. Fork repozitáře
2. Vytvoř feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit změny (`git commit -m 'Add some AmazingFeature'`)
4. Push do branch (`git push origin feature/AmazingFeature`)
5. Otevři Pull Request

---

### 📄 Licence

Jednotlivé projekty mohou mít vlastní licence - viz jejich README soubory.

**Obecně:** MIT License - viz jednotlivé projekty

---

## 🇬🇧 English Version

Collection of useful tools for working with OMSI 2 bus simulator.

### 📦 Projects

#### 🎙️ [TTS Generator](tts-generator/)
Public transport announcement generator using ElevenLabs API or Google TTS.

**Key features:**
- 🚌 Automatic OMSI HOF file parsing
- 🔊 Audio tag support ({nz}, {pz}, {kz})
- 🆓 Free testing with Google TTS
- 🎯 Line filtering
- 💾 Smart caching system
- 🌍 Multilingual voices (including Czech)

**Status:** ✅ Active development
**Version:** 2.1 (Enhanced v2)
**Documentation:** [README](tts-generator/README.md)

---

#### 🎵 [Engine Sound Maker & File Tools](engine-sound-maker-and-file-copier/)
Tools for working with engine sounds and OMSI files.

**Key features:**
- 🤖 **AI Engine Sound Extractor** - Extract engine sounds from video
  - Demucs AI separation (removes voice, music, ambient)
  - YAMNet AI classification (precise engine sound detection)
  - RPM segmentation - automatic splitting by RPM
  - GUI / TUI / Google Colab versions
  - ⚡ GPU acceleration (10x faster in Colab)
- 📁 **OMSI File Copier** - Batch copying of OMSI files
  - Compatible with OMSI-Tools output
  - Automatic root folder detection
  - Progress tracking and verification

**Supported engines:**
- FPT NEF 6 (SOR BN 9.5/10.5/12)
- FPT Cursor 8/9 (SOR NB 12/18)
- IVECO Cursor 8, Mercedes OM906
- Cummins ISBe/ISL
- Generic 4cyl/6cyl diesels

**Status:** ✅ Active development
**Version:** 2.0 (TUI + Colab)
**Documentation:** [README](engine-sound-maker-and-file-copier/README.md) | [README_TUI](engine-sound-maker-and-file-copier/README_TUI.md)

---

### 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/odjezdy-online/omsi-stuff.git
cd omsi-stuff

# TTS Generator
cd tts-generator
pip install -r requirements.txt
python tts_generator_enhanced_v2.py

# Engine Sound Extractor (GUI)
cd engine-sound-maker-and-file-copier
pip install -r requirements.txt
python engine_sound_extractor.py

# Engine Sound Extractor (TUI - cross-platform)
pip install -r requirements_tui.txt
python engine_extractor_tui.py -i

# OMSI File Copier
python omsi_file_copier.py
```

---

### 🛠️ Planned Projects

- 🗺️ **Map Tools** - Tools for working with OMSI maps
- 🎨 **Repaint Manager** - Vehicle repaint manager
- 📊 **Route Analyzer** - Route and timetable analyzer
- 🔧 **Config Editor** - Configuration file editor
- 🚦 **Traffic Light Editor** - Traffic signal editor

---

### 🤝 Contributing

Contributions are welcome! If you have an idea for a new tool or improvement, feel free to open an Issue or Pull Request.

**How to contribute:**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

### 📄 License

Individual projects may have their own licenses - see their README files.

**Generally:** MIT License - see individual projects

---

## ⭐ Support

If you find these tools useful, please consider giving this repository a star!

## 🔗 Links

- [OMSI 2 Official Website](https://www.omnibussimulator.de/)
- [OMSI WebDisk](https://www.omnibuswebdisk.de/)
- [OMSI Community](https://www.omnibuscommunity.de/)

---

## 📊 Statistics

![Projects](https://img.shields.io/badge/Projects-2-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![Language](https://img.shields.io/badge/Language-Python-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

---

**Vytvořeno pro OMSI Bus Simulator komunitu** 🚌❤️
**Created for OMSI Bus Simulator community** 🚌❤️
