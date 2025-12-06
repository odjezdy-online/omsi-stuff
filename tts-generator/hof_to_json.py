import os
import json
import sys
import re

# ==========================================
# CUSTOM PRONUNCIATION DICTIONARY
# Key = The text found in IBIS 2 column (or Display Name)
# Value = The FULL text you want spoken (include City if needed)
# ==========================================
REPLACEMENTS = {
    "Masokomb. závod": "Bukovec nad Lužnicí, Masokombinát, závod",
    "Masokomb. točna": "Bukovec nad Lužnicí, Masokombinát, točna",
    "Nám. T. Bati": "Bukovec nad Lužnicí, Náměstí Tomáše Baťi",
    "Sídl. M. střed": "Bukovec nad Lužnicí, Sídliště Míru střed",
    "Sídl. Míru": "Bukovec nad Lužnicí, Sídliště Míru",
    "Eller-MÚ": "Bukovec nad Lužnicí, Ellerova - Městský úřad",
    "Ellerova - MÚ": "Bukovec nad Lužnicí, Ellerova - Městský úřad",
    "Nový Svět, rozc.": "Nový Svět, rozcestí",
    "Nový Svět, kruh. objezd": "Nový Svět, kruhový objezd",
    "Jir. sady": "Bukovec nad Lužnicí, Jiráskovy sady",
    "Nem., areál": "Bukovec nad Lužnicí, Nemocnice, areál",
    "Budapešťská": "Bukovec nad Lužnicí, Budapešťská",
    "Bratislavská": "Bukovec nad Lužnicí, Bratislavská",
    "28. října": "Bukovec nad Lužnicí, 28. října",
    "Nádraží": "Bukovec nad Lužnicí, Nádraží",
    "Poliklinika": "Bukovec nad Lužnicí, Poliklinika",
    "Pražská": "Bukovec nad Lužnicí, Pražská",
    "Žižkovo nám.": "Bukovec nad Lužnicí, Žižkovo náměstí",
    "Evropská": "Bukovec nad Lužnicí, Evropská",
    "Nám. Svobody": "Bukovec nad Lužnicí, Náměstí Svobody",
    "Husova": "Bukovec nad Lužnicí, Husova",
    "Autobusové nádraží": "Bukovec nad Lužnicí, Autobusové nádraží",
    "Kosmonautů": "Bukovec nad Lužnicí, Kosmonautů",
    "Politických vězňů": "Bukovec nad Lužnicí, Politických vězňů",
    "Třeboňská": "Bukovec nad Lužnicí, Třeboňská",
    "Budovatelská": "Bukovec nad Lužnicí, Budovatelská",
    "Škola SNP": "Bukovec nad Lužnicí, Škola SNP",
    "Na Vyhlídce": "Bukovec nad Lužnicí, Na Vyhlídce",
    "Harantova": "Bukovec nad Lužnicí, Harantova",
    "Vozovna Ražická": "Bukovec nad Lužnicí, Vozovna Ražická",
    "Ražická": "Bukovec nad Lužnicí, Ražická",
    "Chýnovská most": "Bukovec nad Lužnicí, Chýnovská most",
    "Dům peč. služby": "Bukovec nad Lužnicí, Dům pečovatelské služby",
}

def get_clean_tts_name(parts):
    """
    Constructs the clean name for TTS.
    Prioritizes the REPLACEMENTS dictionary first.
    """
    
    # 1. Get the raw stop name (Prefer IBIS 2 [Index 4] -> Display [Index 1])
    if len(parts) > 4 and parts[4].strip():
        stop_raw = parts[4].strip()
    else:
        stop_raw = parts[1].strip()

    # Clean (x) for matching
    clean_key = re.sub(r'\s*\(x\)', '', stop_raw, flags=re.IGNORECASE).strip()
    
    # 2. CHECK DICTIONARY (Highest Priority)
    if clean_key in REPLACEMENTS:
        # If found in dictionary, use that EXACTLY.
        # We assume the dictionary contains the full correct name including city.
        return REPLACEMENTS[clean_key] + "."

    # --- FALLBACK LOGIC (Only if not in dictionary) ---
    
    stop_name = clean_key

    # 3. Clean up the stop name (Remove existing city prefixes to avoid duplication)
    stop_name = re.sub(r'^Bukovec\s*n\.?L\.?,?\s*', '', stop_name, flags=re.IGNORECASE)
    stop_name = re.sub(r'^B\.?n\.?L\.?,?\s*', '', stop_name, flags=re.IGNORECASE)
    
    # 4. Get Ticket Name (Col 10) to determine the City
    ticket_raw = parts[10].strip() if len(parts) > 10 else ""

    # 5. Determine City Prefix
    city_prefix = ""
    
    if re.search(r'B\.?n\.?L\.?|Bukovec', ticket_raw, re.IGNORECASE):
        city_prefix = "Bukovec nad Lužnicí"
    elif ',' in ticket_raw:
        potential_city = ticket_raw.split(',')[0].strip()
        if potential_city.lower() not in stop_name.lower():
            city_prefix = potential_city

    # 6. Combine City and Stop
    if city_prefix:
        if city_prefix.lower() not in stop_name.lower():
            final_name = f"{city_prefix}, {stop_name}"
        else:
            final_name = stop_name
    else:
        final_name = stop_name

    # 7. Final cosmetic cleanup
    final_name = final_name.replace("..", ".")
    final_name = final_name.replace(",", ", ")
    final_name = re.sub(r'\s+', ' ', final_name).strip(" .,")
    
    if not final_name.endswith('.'):
        final_name += "."

    return final_name

def parse_hof_file(file_path):
    announcements = {}
    content = None
    
    for encoding in ['cp1250', 'utf-8', 'latin1']:
        try:
            with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                content = f.read()
            print(f"Successfully read file with {encoding} encoding")
            break
        except Exception:
            continue

    if not content:
        return {}

    # --- 1. Parse Stop Definitions ---
    stop_definitions = {}
    busstop_block_match = re.search(r'\[addbusstop_list\](.*?)\[end\]', content, re.DOTALL)
    
    if busstop_block_match:
        raw_stops = busstop_block_match.group(1).strip().split('\n')
        for line in raw_stops:
            line = line.strip('\r')
            if not line: continue
            
            parts = line.split('\t')
            parts = [p.strip() for p in parts]
            
            if len(parts) >= 2:
                stop_id = parts[0]
                display_name = parts[1]
                tts_name = get_clean_tts_name(parts)
                
                stop_definitions[stop_id] = {
                    'display_name': display_name,
                    'tts_name': tts_name
                }
    
    print(f"Found {len(stop_definitions)} stop definitions.")

    # --- 2. Parse Trips ---
    trip_pattern = r'\[infosystem_trip\]\s*\n(.*?)\s*\n(.*?)\s*\n(.*?)\s*\n(.*?)\s*\n'
    trip_matches = list(re.finditer(trip_pattern, content))
    
    for match in trip_matches:
        line_num = match.group(4).strip()
        
        list_start_marker = '[infosystem_busstop_list]'
        start_pos = match.end()
        list_start_pos = content.find(list_start_marker, start_pos)
        
        if list_start_pos == -1: continue
        
        next_bracket = content.find('[', list_start_pos + len(list_start_marker))
        if next_bracket == -1: next_bracket = len(content)
        
        busstop_section = content[list_start_pos:next_bracket]
        lines = busstop_section.split('\n')
        
        stop_ids_in_trip = []
        for l in lines:
            l = l.strip()
            if l and l != list_start_marker and not l.isdigit() and not l.startswith('['):
                stop_ids_in_trip.append(l)

        # --- 3. Generate Announcements ---
        total_stops = len(stop_ids_in_trip)
        
        for i, stop_id in enumerate(stop_ids_in_trip):
            if stop_id not in stop_definitions:
                continue
                
            stop_info = stop_definitions[stop_id]
            current_tts = stop_info['tts_name']
            
            is_terminus = (i == total_stops - 1) or ('_KZ' in stop_id) or ('_kz' in stop_id.lower())
            
            # Use Display Name for key/filename
            base_key = stop_info['display_name']
            
            if is_terminus:
                key_name = f"{base_key} (konecna)"
                voice_text = f"{current_tts} {{kz}}"
            else:
                key_name = base_key
                if i + 1 < total_stops:
                    next_stop_id = stop_ids_in_trip[i+1]
                    if next_stop_id in stop_definitions:
                        next_tts = stop_definitions[next_stop_id]['tts_name']
                        voice_text = f"{current_tts} {{pz}} {next_tts}"
                    else:
                        voice_text = f"{current_tts}"
                else:
                    voice_text = f"{current_tts}"

            safe_filename = stop_id.replace('/', '-').replace('\\', '-')

            # Deduplication
            if key_name in announcements:
                existing = announcements[key_name]
                if existing['stop_id'] != stop_id:
                    key_name = f"{base_key} (ID: {safe_filename})"
            
            if key_name not in announcements:
                announcements[key_name] = {
                    "hlaseni": voice_text,
                    "soubor": safe_filename,
                    "line": line_num,
                    "stop_id": stop_id
                }

    return announcements

def main():
    print("--- Bukovec HOF to TTS JSON (Force Full Names) ---")
    
    hof_files = [f for f in os.listdir('.') if f.lower().endswith('.hof')]
    if not hof_files:
        print("No .hof files found.")
        sys.exit()
        
    print("Found files:")
    for idx, f in enumerate(hof_files):
        print(f"{idx + 1}. {f}")
        
    try:
        choice = int(input("\nSelect file number: ")) - 1
        filename = hof_files[choice]
    except:
        print("Invalid selection.")
        sys.exit()

    data = parse_hof_file(filename)
    
    if not data:
        print("No data extracted.")
        sys.exit()

    output_name = filename.replace('.hof', '.json')
    with open(output_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"\nSuccess! Created {output_name}")
    print(f"Total unique announcements: {len(data)}")
    print("Dictionary rules applied strictly.")

if __name__ == "__main__":
    main()