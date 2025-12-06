# HOF File Parsing Guide

## Understanding HOF File Structure

OMSI HOF (Haltestellen-Objekt-Formatierung) files contain bus route and stop information. The enhanced TTS generator v2 can parse these files to automatically generate announcements.

## File Structure

### 1. Bus Stop Definitions (Tab-Separated)

Each stop is defined with tab-separated values:
```
StopID	DisplayName	String2	...	LineNum	...	PlatformInfo	...
```

**Example:**
```
31_BnLAuto_KZ	Bukovec n.L.,aut.nádr	Bukovec n.Luž.,,Aut. nádr.		Bukovec n.L.,aut.nádr	201			V		Bukovec n.L.,aut.nádr		8448			201
```

**Fields:**
- **StopID**: Unique identifier (e.g., `31_BnLAuto_KZ`, `Kosmonautů_1`)
- **DisplayName**: Name shown to passengers
- **LineNum**: Bus line number (usually appears multiple times in the row)

### 2. Trip Definitions

Trips group stops together for specific routes:

```
[infosystem_trip]
3101
31_Smer_ZLNadrazi
310
31

[infosystem_busstop_list]
16
31_BnLAuto_Husova
31_Husova_Namesti
31_Namesti_Poliklinika
...
31_ZLNadrazi_KZ
31_ZLNadrazi_KZ
```

**Components:**
- **Trip ID**: Unique identifier (e.g., `3101`)
- **Trip Name**: Human-readable name with direction
- **Route Code**: Internal routing code
- **Line Number**: Bus line number
- **Stop List**: Ordered list of stop IDs

## Stop Naming Conventions

### City Lines
Format: `[StationName]_[Platform]`

**Examples:**
- `Kosmonautů_1` - Platform 1
- `Kosmonautů_2` - Platform 2
- `Nádraží_1` - Station platform 1

### Intercity Lines
Format: `[Line]_[CurrentStop]_[NextStop]` or `[StationName]_[Platform]`

**Examples:**
- `31_BnLAuto_Husova` - Line 31, from Bus Station to Husova
- `31_Husova_Namesti` - Line 31, from Husova to Náměstí
- `31_ZLNadrazi_KZ` - Line 31, to Station (terminus)

### Special Suffixes
- `_KZ` - Konečná zastávka (Terminal stop)
- `_smer_[Direction]` - Direction indicator (e.g., `Poliklinika_smer_Nadrazi`)
- `(x)` - Transfer point (e.g., `Pražská (x)_1`)

## How the Parser Works

### Step 1: Extract Stop Definitions
The parser reads tab-separated lines and extracts:
- Stop ID
- Display name
- Line number

### Step 2: Parse Trip Information
For each `[infosystem_trip]` section:
- Extract trip metadata (ID, name, line number)
- Read corresponding `[infosystem_busstop_list]`
- Build stop sequence

### Step 3: Generate Announcements
For each stop in a trip:
- Determine if terminus (last stop or contains `_KZ`)
- Get next stop from sequence
- Generate Czech announcement text:
  - **Regular stop**: "Zastávka: {name}. Příští zastávka: {next}."
  - **Terminus**: "Konečná zastávka: {name}. Prosíme, vystupte."

### Step 4: Deduplicate
Stops appearing in multiple trips are only generated once, using the first occurrence.

## Features

### Line Filtering
After parsing, you can filter announcements by line number:
```
Found 150 stops across lines: 10, 31, 201, 231
Filter by specific line number (or press Enter for all): 31
Filtered to 30 stops for line 31
```

### Automatic Terminus Detection
The parser automatically identifies terminal stops:
1. Last stop in trip sequence
2. Stop ID contains `_KZ`
3. Trip name contains `KZ`

### Next Stop Detection
Regular stops include next stop information:
- Reads the next stop ID from the trip sequence
- Looks up display name from stop definitions
- Includes in announcement text

## Example Output

### Input (HOF file)
```
31_BnLAuto_KZ	Bukovec n.L.,aut.nádr	...	201
31_Husova_Namesti	Bukovec n.L.,Husova	...	201

[infosystem_trip]
3101
31_Smer_ZLNadrazi
...
[infosystem_busstop_list]
3
31_BnLAuto_Husova
31_Husova_Namesti
31_ZLNadrazi_KZ
```

### Output (Generated announcements)
```json
{
  "Bukovec n.L.,aut.nádr": {
    "hlaseni": "Zastávka: Bukovec n.L.,aut.nádr. Příští zastávka: Bukovec n.L.,Husova.",
    "soubor": "31_BnLAuto_Husova",
    "line": "201",
    "stop_id": "31_BnLAuto_Husova"
  },
  "Bukovec n.L.,Husova": {
    "hlaseni": "Zastávka: Bukovec n.L.,Husova. Příští zastávka: Zálužní Lhota,Nádraží.",
    "soubor": "31_Husova_Namesti",
    "line": "201",
    "stop_id": "31_Husova_Namesti"
  },
  "Zálužní Lhota,Nádraží (konecna)": {
    "hlaseni": "Konečná zastávka: Zálužní Lhota,Nádraží. Prosíme, vystupte.",
    "soubor": "31_ZLNadrazi_KZ",
    "line": "201",
    "stop_id": "31_ZLNadrazi_KZ"
  }
}
```

## Encoding Handling

The parser tries multiple encodings in order:
1. **CP1250** (Windows Central European)
2. **UTF-8** (Universal)
3. **Latin1** (Fallback)

This ensures compatibility with HOF files from different sources.

## Using Audio Tags with HOF

You can customize HOF-generated announcements by editing them in a JSON file and adding tags:

1. Generate announcements from HOF
2. Export to JSON (or manually create from generated structure)
3. Add audio tags to the `hlaseni` field:
   ```json
   {
     "Nádraží": {
       "hlaseni": "{nz} Zastávka: Nádraží. {pz} Příští zastávka: 28. října.",
       "soubor": "31_Nadrazi_28rijna",
       "line": "201"
     }
   }
   ```
4. Load the modified JSON file instead of HOF

## Limitations

### Current Parser Limitations
- Assumes tab-separated values (standard OMSI format)
- May not parse all custom HOF extensions
- Duplicate stops across lines are only generated once
- Platform-specific announcements need manual editing

### Future Improvements
- Support for custom announcement templates per line
- Platform-specific variations (e.g., "Platform 1" vs "Platform 2")
- Integration with line-specific audio tags
- Export parsed data to JSON for manual editing

## Troubleshooting

### "No stops found"
- Check HOF file encoding (should be CP1250 or UTF-8)
- Verify `[infosystem_trip]` sections exist
- Ensure stop definitions use tab separators

### "Incorrect stop names"
- HOF file may use custom format
- Try exporting to JSON and manually editing

### "Missing next stop information"
- Trip sequences may be incomplete
- Edit generated JSON to add next stop info

## Command Usage

```bash
# Run enhanced version v2
python tts_generator_enhanced_v2.py

# Select HOF option when prompted
Input file options:
1. JSON file (zastavky.json or custom)
2. HOF file (OMSI bus stop file)
Select input type (1 or 2, default 1): 2

# Choose HOF file
Available HOF files:
1. Bukovec_BUSE_V1.2 (testing).hof
Select HOF file (1-1): 1

# Optional: Filter by line
Found 150 stops across lines: 10, 31, 201, 231
Filter by specific line number (or press Enter for all): 31
```
