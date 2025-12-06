# 🚌 Engine Sound Extractor for OMSI

Extrahuje a zpracovává motorové zvuky z videa pro použití v OMSI Bus Simulator.

## 🎯 Tři způsoby použití:

### 1. **GUI Aplikace** (Windows Desktop)
- Drag & drop rozhraní
- Nejjednodušší pro běžné použití
- Soubor: `engine_sound_extractor.py`

### 2. **TUI - Terminal** (Všude)
- Příkazová řádka / terminál
- Google Colab kompatibilní
- Soubor: `engine_extractor_tui.py`

### 3. **Google Colab** (Cloud, zdarma GPU!)
- Běží v prohlížeči
- 10x rychlejší s GPU
- Soubor: `Engine_Sound_Extractor_Colab.ipynb`

---

## 📋 Features

- 🎵 **AI Separace - Demucs**: Odstraní lidský hlas a hudbu
- 🎯 **AI Klasifikace - YAMNet**: Detekuje přesně engine sounds
- 🔧 **Klasický noise reduction**: Rychlá metoda
- 📊 **Frekvenční filtrování**: Izoluje motorové frekvence (80-500 Hz)
- 🔢 **RPM Segmentace**: Automaticky rozdělí na různé otáčky
- 🚀 **GPU Akcelerace**: 10x rychlejší v Google Colab

---

## 🚀 Rychlý start

### Varianta A: GUI (Windows)

```bash
pip install -r requirements.txt
python engine_sound_extractor.py
```

### Varianta B: TUI (Terminal)

**Interaktivní režim:**
```bash
pip install -r requirements_tui.txt
python engine_extractor_tui.py -i
```

**CLI režim:**
```bash
python engine_extractor_tui.py video.mp4 -o output/ -m ai_demucs
```

### Varianta C: Google Colab

1. Otevři `Engine_Sound_Extractor_Colab.ipynb` v Google Colab
2. Runtime → Change runtime type → **GPU**
3. Runtime → Run all (nebo Ctrl+F9)
4. Nahraj video a počkej
5. Stáhni výsledky

**🔗 Přímý link:** [Otevřít v Colab](https://colab.research.google.com/)

---

## 📖 TUI - Detailní návod

### Interaktivní režim

```bash
python engine_extractor_tui.py -i
```

Program se tě zeptá na vše:
- Cesta k videu
- Výstupní složka
- Metoda zpracování (Classic/Demucs/YAMNet)
- Typ motoru
- Export nastavení

### CLI režim (pro skripty)

**Základní použití:**
```bash
python engine_extractor_tui.py video.mp4
```

**S parametry:**
```bash
python engine_extractor_tui.py video.mp4 \
  -o output_folder \
  -m ai_demucs \
  --model htdemucs \
  --freq-low 80 \
  --freq-high 500 \
  -e iveco_cursor8 \
  -s 5
```

### Parametry CLI

| Parametr | Popis | Default |
|----------|-------|---------|
| `video` | Cesta k video souboru | - |
| `-o, --output` | Výstupní složka | `./engine_sounds` |
| `-m, --method` | Metoda: `classic`, `ai_demucs`, `ai_yamnet` | `ai_demucs` |
| `--model` | AI model: `htdemucs`, `htdemucs_ft`, `mdx_extra` | `htdemucs` |
| `-n, --noise` | Úroveň noise reduction (0-100) | `50` |
| `--freq-low` | Dolní frekvence (Hz) | `80` |
| `--freq-high` | Horní frekvence (Hz) | `500` |
| `-e, --engine` | Typ motoru | `iveco_cursor8` |
| `--no-full` | Neexportovat kompletní zvuk | `False` |
| `--no-segments` | Neexportovat segmenty | `False` |
| `-s, --segments` | Počet segmentů (2-20) | `5` |
| `-i, --interactive` | Interaktivní režim | `False` |

### Typy motorů

| Kód | Popis |
|-----|-------|
| `fpt_nef6_184` | FPT NEF 6 (6V, 6.7L, 184kW) - SOR BN 9.5/10.5/12 |
| `fpt_nef6_210` | FPT NEF 6 (6V, 6.7L, 210kW) - SOR BN 12 |
| `fpt_nef4` | FPT NEF 4 (4V, 4.5L) - SOR BN 8.5 |
| `fpt_cursor8` | FPT Cursor 8 (6V, 6.7L) - SOR NB 12 |
| `fpt_cursor9` | FPT Cursor 9 (6V, 8.7L) - SOR NB 18 |
| `iveco_cursor8` | IVECO Cursor 8 (6V, 7.8L) - Starší SOR |
| `mercedes_om906` | Mercedes OM906 (6V, 6.4L) |
| `cummins_isbe` | Cummins ISBe (6V, 6.7L) |
| `cummins_isl` | Cummins ISL (6V, 8.9L) |
| `generic_6cyl` | Obecný 6V diesel |
| `generic_4cyl` | Obecný 4V diesel |

---

## 🎮 Google Colab - Detailní návod

### Krok za krokem:

1. **Otevři notebook:**
   - Nahraj `Engine_Sound_Extractor_Colab.ipynb` do Colab
   - Nebo použij přímý link

2. **Aktivuj GPU:**
   ```
   Runtime → Change runtime type → Hardware accelerator: GPU
   ```

3. **Spusť všechny buňky:**
   ```
   Runtime → Run all (Ctrl+F9)
   ```

4. **Nahraj video:**
   - **Varianta A**: Upload z počítače (tlačítko v notebooku)
   - **Varianta B**: Z Google Drive (připoj Drive)

5. **Nastav konfiguraci** (buňka 4):
   ```python
   METHOD = 'ai_demucs'  # nebo 'ai_yamnet', 'classic'
   ENGINE_TYPE = 'iveco_cursor8'
   NUM_SEGMENTS = 5
   ```

6. **Počkej na zpracování:**
   - S GPU: ~10-20 minut pro 20min video
   - Bez GPU: ~1-2 hodiny

7. **Stáhni výsledky:**
   - ZIP soubor se automaticky stáhne
   - Nebo poslechni náhled přímo v notebooku

### Výhody Colab:

✅ **Zdarma GPU** (Tesla T4, 15 GB VRAM)
✅ **Rychlejší 10x** než na běžném počítači
✅ **15 GB RAM** - pitch detection funguje i pro dlouhá videa
✅ **Žádná instalace** - běží v prohlížeči
✅ **Cloud storage** - propojení s Google Drive

### Limity:

⚠️ **Runtime limit**: ~12 hodin (pak se restartuje)
⚠️ **Disk space**: ~100 GB (dost pro většinu videí)
⚠️ **Upload rychlost**: Záleží na твém připojení

---

## 🔧 Porovnání metod

### Classic Noise Reduction
- ✅ **Nejrychlejší** (~5 minut pro 20min video)
- ✅ **Žádná závislost na AI modelech**
- ⚠️ **Horší kvalita** - hrubé odstranění šumu
- ⚠️ **Může poškodit zvuk motoru**

### AI Separace - Demucs
- ✅ **Výborná kvalita** - čisté motorové zvuky
- ✅ **Odstraní hlas, hudbu, okolí**
- ⚠️ **Pomalé** (~1 hodina CPU, ~10 min GPU)
- ⚠️ **Velké modely** (~250 MB)

### AI Klasifikace - YAMNet
- ✅ **Přesná detekce** engine sounds
- ✅ **Rychlejší** než Demucs
- ⚠️ **Experimentální** - méně testováno
- ⚠️ **TensorFlow závislost**

---

## 📊 Časové odhady

### Pro 20minutové video:

| Metoda | CPU (lokálně) | GPU (Colab) |
|--------|---------------|-------------|
| Classic | 5-7 min | 5-7 min |
| Demucs | 60-90 min | 10-15 min |
| YAMNet | 15-20 min | 5-10 min |

**Pitch detection** (RPM segmentace):
- Krátká videa (<10 min): 2-4 minuty
- Dlouhá videa (>10 min): Fallback (bez pitch detection)

---

## 🎯 Použití výsledků v OMSI

### 1. Zkopíruj soubory:

```
Vehicles\
  └── [tvůj_autobus]\
      └── sound\
          ├── engine_sound_full.wav
          ├── engine_600rpm.wav
          ├── engine_1200rpm.wav
          ├── engine_1800rpm.wav
          └── engine_2400rpm.wav
```

### 2. Uprav `sound.cfg`:

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

### 3. Testuj v OMSI:

- Nastartuj autobus
- Poslouchej zvuky při různých otáčkách
- Případně uprav RPM thresholdy

---

## 🐛 Řešení problémů

### "ModuleNotFoundError: No module named 'X'"

```bash
pip install -r requirements_tui.txt
```

### "FFmpeg not found"

**Windows:**
```bash
winget install ffmpeg
```

**Linux/Mac:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

### "Unable to allocate X GB for array" (Pitch detection)

- Video je příliš dlouhé (>10 min)
- Script automaticky použije fallback (rovnoměrné rozdělení)
- Nebo použij Google Colab s více RAM

### Demucs stahování selhalo

- Vodafone blokuje Facebook servery
- Řešení:
  1. Zapni VPN
  2. Nebo stáhni model ručně a dej do cache
  3. Nebo použij Google Colab

### Špatná kvalita výstupu

- Zvyš noise reduction (50-80%)
- Uprav frekvenční rozsah
- Zkus AI separaci místo classic
- Ujisti se že vstupní video má dobrou kvalitu zvuku

---

## 💡 Tipy & Triky

### Pro nejlepší výsledky:

1. **Použij kvalitní video**
   - Dobrý mikrofon
   - Minimum vedlejšího hluku
   - Bez hudby/mluvení

2. **Optimální délka videa:**
   - Ideálně 5-10 minut
   - Pro delší videa použij Google Colab

3. **Frekvenční rozsah:**
   - Diesely: 80-500 Hz
   - Benzínové: 100-600 Hz
   - Pro hlubší zvuk: snižte dolní frekvenci

4. **RPM segmentace:**
   - Více segmentů (7-10) = plynulejší přechody
   - Méně segmentů (3-5) = menší velikost

5. **GPU Akcelerace:**
   - Google Colab s GPU je 10x rychlejší!
   - Zdarma a jednoduché

---

## 📝 Changelog

### v2.0 (TUI + Colab)
- ✨ Přidána TUI verze
- ✨ Google Colab notebook
- ✨ YAMNet AI klasifikace
- ✨ CLI parametry
- ✨ Interaktivní režim
- 🐛 Opravy pitch detection pro dlouhá videa

### v1.0 (GUI)
- ✨ Základní GUI aplikace
- ✨ Demucs AI separace
- ✨ Klasický noise reduction
- ✨ RPM segmentace
- ✨ Podpora všech SOR motorů

---

## 🤝 Přispívání

Máš nápad na vylepšení? Pull requesty vítány!

---

## 📄 Licence

MIT License - můžeš použít, modifikovat a sdílet!

---

## 🎉 Užij si realistické zvuky v OMSI!

**Vytvořeno pro OMSI Bus Simulator komunitu** 🚌❤️

---

**Pro otázky nebo problémy:**
- GitHub Issues
- Discord: [tvůj discord]
- Email: [tvůj email]
