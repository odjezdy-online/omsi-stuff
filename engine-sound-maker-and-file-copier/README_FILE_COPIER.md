# OMSI File Copier / OMSI Kopírovač Souborů

[🇨🇿 Česká verze](#česká-verze) | [🇬🇧 English Version](#english-version)

---

## 🇨🇿 Česká verze

GUI nástroj pro hromadné kopírování OMSI souborů a modelů z jedné instalace do druhé.

### 🎯 K čemu to slouží?

Když chceš zkopírovat modely a objekty (sceneryobjects) z jedné OMSI mapy do druhé, nebo ze staré instalace OMSI do nové, tento nástroj ti to výrazně usnadní. Místo ručního kopírování stovek složek a souborů stačí:

1. Vygenerovat seznam souborů pomocí OMSI-Tools
2. Vložit ho do aplikace
3. Vybrat zdrojovou a cílovou složku
4. Počkat, než se všechno zkopíruje

### 🚀 Rychlý start

#### 1. Instalace

```bash
pip install -r requirements.txt
python omsi_file_copier.py
```

#### 2. Získání seznamu souborů z OMSI-Tools

**OMSI-Tools** je nástroj, který ti pomůže zjistit, které soubory jsou potřeba pro konkrétní mapu.

![Jak získat seznam z OMSI-Tools](https://s3-server.ente.odjezdy.online/raw/mPTh37.gif)

**Výsledný formát:**
```
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_1\BL1.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_2\BL2.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Lazurowa_2\Bl_Laz_2.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Lazurowa_3\Bl_Laz_3.sco
Sceneryobjects\251_VelkeOpatovice-Kninice\Budka_CTK.sco
Splines\Animations\roadworks_narr.sli
Splines\Roadway\texture\511_road.sli
```

### 📖 Jak používat aplikaci

#### Krok 1: Spuštění aplikace

```bash
python omsi_file_copier.py
```

Otevře se GUI okno s těmito poli:

#### Krok 2: Vyplnění polí

**📂 OMSI Path (Zdrojová složka):**
- Cesta k tvé OMSI instalaci, odkud chceš kopírovat
- Příklad: `C:\Program Files (x86)\Steam\steamapps\common\OMSI 2`
- Klikni na **"Browse"** a vyber složku s OMSI

**📂 Target Path (Cílová složka):**
- Kam chceš soubory zkopírovat
- Může to být:
  - Jiná OMSI instalace
  - Záložní složka
  - Sdílená složka pro kolegy
- Příklad: `D:\OMSI_Backup` nebo `C:\OMSI_2_New`
- Klikni na **"Browse"** a vyber cílovou složku

**📝 File List (Seznam souborů):**
- Velké textové pole pro seznam souborů
- **Vlož sem výstup z OMSI-Tools** (viz GIF výše)
- Každý soubor na vlastním řádku
- Cesty relativní vůči OMSI složce

#### Krok 3: Spuštění kopírování

1. Zkontroluj, že máš vyplněné všechny tři pole
2. Klikni na **"Start Copy"**
3. Aplikace:
   - Analyzuje root složky (např. `Sceneryobjects\149_Warszawa`)
   - Zkopíruje celé složky najednou (rychlejší než jednotlivé soubory)
   - Zobrazuje progress bar
   - Loguje každou akci do spodního okna

#### Krok 4: Sledování průběhu

**Progress bar:**
- Ukazuje kolik složek už bylo zkopírováno
- Např. "5/20" znamená 5 z 20 složek hotovo

**Log okno:**
- Zobrazuje detailní info o každé akci:
  - ✅ `Zkopírováno: Sceneryobjects\149_Warszawa`
  - ⚠️ `Nenalezeno: Sceneryobjects\neexistujici_model`
  - 📊 Souhrn na konci

### 🔧 Jak to funguje

#### Inteligentní kopírování celých složek

Místo kopírování jednotlivých souborů (např. 500 .sco souborů po jednom) aplikace:

1. **Analyzuje cesty** a najde root složky:
   ```
   Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_1\BL1.sco
   Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_2\BL2.sco
   ↓
   Root složka: Sceneryobjects\149_Warszawa
   ```

2. **Kopíruje celou složku najednou:**
   - Rychlejší (méně operací)
   - Kompletní struktura zachována
   - Všechny související soubory (.cfg, .x, textury) zkopírované automaticky

3. **Deduplikace:**
   - Pokud je `Sceneryobjects\149_Warszawa` v seznamu vícekrát, zkopíruje se jen jednou
   - Šetří čas a místo

### 💡 Tipy a triky

**Pro nejlepší výsledky:**

1. **Zkontroluj volné místo na disku**
   - Sceneryobjects můžou zabrat i několik GB
   - Ujisti se, že máš dost místa na cílovém disku

2. **Použij záložní složku poprvé**
   - Nejdřív zkopíruj do testovací složky
   - Ověř, že se vše zkopírovalo správně
   - Pak teprve kopíruj do finální OMSI instalace

3. **OMSI-Tools výstup ulož do souboru**
   - OMSI-Tools → Export → Soubor.txt
   - Otevři v Notepadu
   - Ctrl+A → Ctrl+C → Vlož do aplikace

4. **Sleduj log okno**
   - Pokud vidíš hodně "Nenalezeno", možná:
     - Máš špatnou zdrojovou cestu
     - Seznam je z jiné OMSI instalace
     - Některé modely v původní instalaci chybí

### 🐛 Řešení problémů

**"Access denied" / "Přístup odepřen"**
- Spusť aplikaci jako administrátor (pravý klik → Spustit jako správce)
- Zkontroluj oprávnění ke složkám

**"Nenalezeno" u všech souborů**
- Zkontroluj, že OMSI Path skutečně ukazuje na hlavní složku OMSI (kde je `Omsi.exe`)
- Zkontroluj, že cesty v seznamu jsou relativní (např. `Sceneryobjects\...`, ne `C:\OMSI\Sceneryobjects\...`)

**Aplikace se zasekne**
- Kopírování velkých složek může trvat několik minut
- Sleduj log okno - pokud se objevují nové zprávy, aplikace běží
- Nerušit během kopírování!

**Některé složky se nezkopírovaly**
- Zkontroluj log okno - tam je přesný důvod
- Možné příčiny:
  - Složka v původní OMSI neexistuje
  - Nedostatek místa na disku
  - Zamčené soubory (OMSI běží?)

**Duplikáty/přepisy**
- Aplikace **přepíše** existující soubory v cílové složce
- Pokud nechceš přepsat, použij jinou cílovou složku

### 📂 Příklad použití

**Scénář:** Chceš přenést Warszawa mapu ze staré instalace do nové

1. **Otevři OMSI-Tools** na staré instalaci
2. **Vyber Warszawa mapu** → Zobraz potřebné soubory
3. **Zkopíruj seznam** (jak ukazuje GIF)
4. **Spusť OMSI File Copier:**
   - OMSI Path: `C:\Program Files\OMSI 2 (stará instalace)`
   - Target Path: `D:\OMSI 2 (nová instalace)`
   - File List: *vložit seznam z OMSI-Tools*
5. **Start Copy**
6. **Počkej** až se všechno zkopíruje (může trvat 5-15 minut)
7. **Zkontroluj log** - mělo by být "Zkopírováno: X složek"
8. **Spusť novou OMSI instalaci** a zkontroluj, že mapa funguje

### 🎯 Co aplikace NEKOPÍRUJE

Aplikace kopíruje **pouze složky/soubory uvedené v seznamu**. Automaticky se NEKOPÍRUJE:
- Celá mapa (pokud není v seznamu)
- Autobusy (pokud nejsou v seznamu)
- Konfigurace OMSI
- Nastavení grafiky
- Savegames

Pokud potřebuješ zkopírovat mapu celou, přidej do seznamu:
```
Maps\Warszawa
```

### 📄 Formát seznamu souborů

**Podporované formáty:**

✅ **Relativní cesty (doporučeno):**
```
Sceneryobjects\149_Warszawa\objekt.sco
Splines\texture\511_road.sli
```

✅ **S nebo bez koncového souboru:**
```
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_1\BL1.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_2
```
(Obojí zkopíruje celou root složku)

❌ **Absolutní cesty (nepodporováno):**
```
C:\OMSI\Sceneryobjects\149_Warszawa\objekt.sco
```

---

## 🇬🇧 English Version

GUI tool for batch copying OMSI files and models from one installation to another.

### 🎯 What is it for?

When you want to copy models and objects (sceneryobjects) from one OMSI map to another, or from an old OMSI installation to a new one, this tool makes it much easier. Instead of manually copying hundreds of folders and files, you just:

1. Generate a file list using OMSI-Tools
2. Paste it into the application
3. Select source and target folders
4. Wait for everything to copy

### 🚀 Quick Start

#### 1. Installation

```bash
pip install -r requirements.txt
python omsi_file_copier.py
```

#### 2. Getting File List from OMSI-Tools

**OMSI-Tools** helps you identify which files are needed for a specific map.

![How to get list from OMSI-Tools](https://s3-server.ente.odjezdy.online/raw/mPTh37.gif)

**Result format:**
```
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_1\BL1.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_2\BL2.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Lazurowa_2\Bl_Laz_2.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Lazurowa_3\Bl_Laz_3.sco
Sceneryobjects\251_VelkeOpatovice-Kninice\Budka_CTK.sco
Splines\Animations\roadworks_narr.sli
Splines\Roadway\texture\511_road.sli
```

### 📖 How to Use the Application

#### Step 1: Launch Application

```bash
python omsi_file_copier.py
```

A GUI window will open with these fields:

#### Step 2: Fill in Fields

**📂 OMSI Path (Source folder):**
- Path to your OMSI installation to copy from
- Example: `C:\Program Files (x86)\Steam\steamapps\common\OMSI 2`
- Click **"Browse"** to select OMSI folder

**📂 Target Path (Destination folder):**
- Where you want to copy files to
- Can be:
  - Another OMSI installation
  - Backup folder
  - Shared folder for colleagues
- Example: `D:\OMSI_Backup` or `C:\OMSI_2_New`
- Click **"Browse"** to select target folder

**📝 File List:**
- Large text box for file list
- **Paste OMSI-Tools output here** (see GIF above)
- Each file on its own line
- Paths relative to OMSI folder

#### Step 3: Start Copying

1. Verify all three fields are filled
2. Click **"Start Copy"**
3. The application will:
   - Analyze root folders (e.g., `Sceneryobjects\149_Warszawa`)
   - Copy entire folders at once (faster than individual files)
   - Show progress bar
   - Log every action to bottom window

#### Step 4: Monitor Progress

**Progress bar:**
- Shows how many folders copied
- E.g., "5/20" means 5 out of 20 folders done

**Log window:**
- Shows detailed info about each action:
  - ✅ `Copied: Sceneryobjects\149_Warszawa`
  - ⚠️ `Not found: Sceneryobjects\nonexistent_model`
  - 📊 Summary at the end

### 🔧 How It Works

#### Intelligent Whole-Folder Copying

Instead of copying individual files (e.g., 500 .sco files one by one), the application:

1. **Analyzes paths** to find root folders:
   ```
   Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_1\BL1.sco
   Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_2\BL2.sco
   ↓
   Root folder: Sceneryobjects\149_Warszawa
   ```

2. **Copies entire folder at once:**
   - Faster (fewer operations)
   - Complete structure preserved
   - All related files (.cfg, .x, textures) copied automatically

3. **Deduplication:**
   - If `Sceneryobjects\149_Warszawa` appears multiple times in list, only copied once
   - Saves time and space

### 💡 Tips and Tricks

**For best results:**

1. **Check free disk space**
   - Sceneryobjects can take several GB
   - Ensure enough space on target disk

2. **Use backup folder first**
   - Copy to test folder first
   - Verify everything copied correctly
   - Then copy to final OMSI installation

3. **Save OMSI-Tools output to file**
   - OMSI-Tools → Export → File.txt
   - Open in Notepad
   - Ctrl+A → Ctrl+C → Paste into application

4. **Watch log window**
   - If you see many "Not found", possibly:
     - Wrong source path
     - List is from different OMSI installation
     - Some models missing in original installation

### 🐛 Troubleshooting

**"Access denied"**
- Run application as administrator (right-click → Run as administrator)
- Check folder permissions

**"Not found" for all files**
- Verify OMSI Path actually points to main OMSI folder (where `Omsi.exe` is)
- Verify paths in list are relative (e.g., `Sceneryobjects\...`, not `C:\OMSI\Sceneryobjects\...`)

**Application freezes**
- Copying large folders can take several minutes
- Watch log window - if new messages appear, application is running
- Don't interrupt during copying!

**Some folders didn't copy**
- Check log window - exact reason is there
- Possible causes:
  - Folder doesn't exist in original OMSI
  - Not enough disk space
  - Locked files (is OMSI running?)

**Duplicates/overwrites**
- Application **will overwrite** existing files in target folder
- If you don't want to overwrite, use different target folder

### 📂 Example Usage

**Scenario:** Transfer Warszawa map from old installation to new

1. **Open OMSI-Tools** on old installation
2. **Select Warszawa map** → Show required files
3. **Copy list** (as shown in GIF)
4. **Run OMSI File Copier:**
   - OMSI Path: `C:\Program Files\OMSI 2 (old installation)`
   - Target Path: `D:\OMSI 2 (new installation)`
   - File List: *paste list from OMSI-Tools*
5. **Start Copy**
6. **Wait** for everything to copy (can take 5-15 minutes)
7. **Check log** - should say "Copied: X folders"
8. **Launch new OMSI installation** and verify map works

### 🎯 What the Application Does NOT Copy

The application copies **only folders/files listed**. Does NOT automatically copy:
- Entire map (unless in list)
- Buses (unless in list)
- OMSI configuration
- Graphics settings
- Savegames

If you need to copy entire map, add to list:
```
Maps\Warszawa
```

### 📄 File List Format

**Supported formats:**

✅ **Relative paths (recommended):**
```
Sceneryobjects\149_Warszawa\object.sco
Splines\texture\511_road.sli
```

✅ **With or without end file:**
```
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_1\BL1.sco
Sceneryobjects\149_Warszawa\Bloki\Blok_Kocjana_2
```
(Both will copy entire root folder)

❌ **Absolute paths (not supported):**
```
C:\OMSI\Sceneryobjects\149_Warszawa\object.sco
```

---

## 📄 License

MIT License - see main project LICENSE

## 🤝 Contributing

Found a bug or have a suggestion? Open an issue or pull request!

---

**Vytvořeno pro OMSI Bus Simulator komunitu** 🚌❤️
**Created for OMSI Bus Simulator community** 🚌❤️
