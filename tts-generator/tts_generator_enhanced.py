import os
import json
import sys
import subprocess
import tempfile
import shutil
import re
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import elevenlabs

CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def setup_api_key():
    """Setup ElevenLabs API key."""
    # Try to load from .env first
    load_dotenv()

    # Check environment variable
    api_key = os.getenv("ELEVENLABS_API_KEY")

    # If not in environment, check config file
    if not api_key:
        config = load_config()
        api_key = config.get('api_key')

    # If still no API key, prompt user
    if not api_key:
        print("\nElevenLabs API key not found in config or environment.")
        api_key = input("Please enter your ElevenLabs API key: ").strip()
        config = load_config()
        config['api_key'] = api_key
        save_config(config)
        # Also suggest adding to .env file
        print("Tip: You can also add your API key to a .env file as ELEVENLABS_API_KEY=your_key")

    return api_key

def initialize_client(api_key):
    """Initialize the ElevenLabs client."""
    return ElevenLabs(api_key=api_key)

def list_voices(client):
    """List available voices and return selected voice."""
    available_voices = client.voices.get_all().voices

    print("\nAvailable voices:")
    print("=" * 50)

    for idx, voice in enumerate(available_voices):
        voice_type = "(Cloned)" if voice.category == "cloned" else "(Premium)" if voice.category == "premium" else "(Standard)"
        print(f"\n{idx + 1}. {voice.name} {voice_type}")
        print(f"   ID: {voice.voice_id}")
        if hasattr(voice, 'labels') and voice.labels:
            print(f"   Labels: {', '.join(f'{k}: {v}' for k, v in voice.labels.items())}")
        if hasattr(voice, 'description') and voice.description:
            print(f"   Description: {voice.description}")
        print(f"   Category: {voice.category}")
        print("-" * 30)

    while True:
        try:
            choice = input("\nSelect voice number (or 'q' to quit): ").strip().lower()
            if choice == 'q':
                print("Operation cancelled.")
                sys.exit(0)

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_voices):
                selected = available_voices[choice_idx]
                print(f"\nSelected voice: {selected.name}")
                print(f"Voice ID: {selected.voice_id}")
                return selected
        except ValueError:
            pass
        print("Invalid choice. Please enter a number or 'q' to quit.")

def get_voice_settings(client, voice_id):
    """Get voice generation settings from user."""
    try:
        # Get default settings for the voice
        default_settings = client.voices.get_settings(voice_id=voice_id)

        print("\nCurrent voice settings:")
        print(f"Stability: {default_settings.stability}")
        print(f"Similarity boost: {default_settings.similarity_boost}")
        print(f"Style: {default_settings.style}")

        # Get user input with defaults shown
        stability = float(input(f"\nEnter stability (0.0-1.0, default {default_settings.stability}): ") or default_settings.stability)
        similarity_boost = float(input(f"Enter similarity boost (0.0-1.0, default {default_settings.similarity_boost}): ") or default_settings.similarity_boost)
        style = float(input(f"Enter style exaggeration (0.0-1.0, default {default_settings.style}): ") or default_settings.style)

        # Get model selection
        print("\nAvailable models:")
        print("1. Eleven Multilingual v2 (eleven_multilingual_v2) - Recommended for most use cases")
        print("2. Eleven Turbo v2.5 (eleven_turbo_v2_5) - Faster, ideal when speed is crucial")

        model_choice = input("\nSelect model (1 or 2, default 1): ").strip() or "1"
        model_id = "eleven_multilingual_v2" if model_choice == "1" else "eleven_turbo_v2_5"

        return {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "model_id": model_id
        }
    except Exception as e:
        print(f"Error getting voice settings: {e}")
        # Fallback to defaults
        return {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.25,
            "model_id": "eleven_multilingual_v2"
        }

def parse_hof_file(file_path):
    """Parse HOF file and extract bus stops and termini.

    Returns a dictionary with structure:
    {
        "Stop Name": {
            "hlaseni": "Text from stop name",
            "soubor": "sanitized_filename",
            "is_terminus": False
        }
    }
    """
    announcements = {}

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find all [addterminus] and [addterminus_allexit] sections
        terminus_pattern = r'\[addterminus(?:_allexit)?\]\s*\n(\d+)\s*\n([^\n]+)'
        terminus_matches = re.finditer(terminus_pattern, content, re.MULTILINE)

        for match in terminus_matches:
            ibis_code = match.group(1).strip()
            name = match.group(2).strip()

            if name and name not in announcements:
                # Create filename from name
                safe_filename = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')

                announcements[f"{name} (konecna)"] = {
                    "hlaseni": f"Konečná zastávka: {name}. Prosíme, vystupte.",
                    "soubor": f"{ibis_code}_{safe_filename}_KZ"
                }

        # Find all [addbusstop] sections
        busstop_pattern = r'\[addbusstop\]\s*\n([^\n]+)'
        busstop_matches = re.finditer(busstop_pattern, content, re.MULTILINE)

        for match in busstop_matches:
            name = match.group(1).strip()

            if name and name not in announcements:
                # Create filename from name
                safe_filename = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')

                announcements[name] = {
                    "hlaseni": f"Zastávka: {name}.",
                    "soubor": safe_filename
                }

        print(f"Successfully parsed HOF file: {len(announcements)} stops found")
        return announcements

    except Exception as e:
        print(f"Error parsing HOF file: {e}")
        return {}

def load_announcements():
    """Load announcements from JSON or HOF file."""
    default_json = "zastavky.json"

    # Ask user what type of file to load
    print("\nInput file options:")
    print("1. JSON file (zastavky.json or custom)")
    print("2. HOF file (OMSI bus stop file)")

    choice = input("\nSelect input type (1 or 2, default 1): ").strip() or "1"

    if choice == "2":
        # HOF file mode
        hof_files = [f for f in os.listdir('.') if f.endswith('.hof')]

        if hof_files:
            print("\nAvailable HOF files:")
            for idx, hof_file in enumerate(hof_files, 1):
                print(f"{idx}. {hof_file}")

            hof_choice = input(f"\nSelect HOF file (1-{len(hof_files)}): ").strip()
            try:
                hof_idx = int(hof_choice) - 1
                if 0 <= hof_idx < len(hof_files):
                    return parse_hof_file(hof_files[hof_idx])
            except ValueError:
                pass

        # If no files or invalid choice, ask for path
        file_path = input("\nEnter path to HOF file: ").strip()
        if file_path and os.path.exists(file_path):
            return parse_hof_file(file_path)
        else:
            print("HOF file not found. Exiting.")
            sys.exit(0)

    # JSON file mode (default)
    # Try to load default file first
    if os.path.exists(default_json):
        print(f"\nFound default announcements file: {default_json}")
        try:
            with open(default_json, 'r', encoding='utf-8') as f:
                announcements = json.load(f)
                print(f"Successfully loaded {len(announcements)} announcements.")
                return announcements
        except Exception as e:
            print(f"Error loading default file: {e}")
    else:
        print("\nNo default announcements file found.")

    # If default file doesn't exist or failed to load, ask for path
    while True:
        file_path = input("\nEnter path to announcements JSON file (or press Enter to exit): ").strip()
        if not file_path:
            print("No file provided. Exiting.")
            sys.exit(0)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                announcements = json.load(f)
                print(f"Successfully loaded {len(announcements)} announcements.")

                # Ask for confirmation before proceeding
                confirm = input("\nProceed with generating announcements? (y/N): ").strip().lower()
                if confirm != 'y':
                    print("Operation cancelled. Exiting.")
                    sys.exit(0)

                return announcements
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            print("Please try again or press Enter to exit.")

def parse_audio_tags(text):
    """Parse audio tags from text and return list of audio segments.

    Tags: {nz}, {pz}, {kz}
    Returns: list of tuples [(type, content), ...]
    where type is 'text' or 'audio' and content is the text or audio filename
    """
    segments = []
    pattern = r'\{(nz|pz|kz)\}'

    last_end = 0
    for match in re.finditer(pattern, text):
        # Add text before the tag
        if match.start() > last_end:
            text_before = text[last_end:match.start()]
            if text_before.strip():
                segments.append(('text', text_before.strip()))

        # Add audio tag
        audio_file = match.group(1) + '.wav'
        segments.append(('audio', audio_file))

        last_end = match.end()

    # Add remaining text after last tag
    if last_end < len(text):
        remaining_text = text[last_end:]
        if remaining_text.strip():
            segments.append(('text', remaining_text.strip()))

    # If no tags found, return the whole text
    if not segments:
        segments.append(('text', text))

    return segments

def process_audio_with_ffmpeg(input_file, output_file, audio_segments, is_terminus=False):
    """Process audio file with ffmpeg to add tags and gong.

    audio_segments: list of tuples [(type, content), ...]
    """
    temp_dir = None
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_files = []

        # Convert input TTS to wav
        main_audio = os.path.join(temp_dir, "main.wav")
        subprocess.run([
            'ffmpeg', '-y', '-i', input_file,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            main_audio
        ], check=True, capture_output=True)

        # Build the audio chain with tags
        audio_chain = []

        # Add gong at the beginning if it exists
        if os.path.exists('gong.wav'):
            audio_chain.append(('gong', 'gong.wav'))

        # Process segments to build audio chain
        for seg_type, content in audio_segments:
            if seg_type == 'audio':
                # Insert tagged audio file
                audio_chain.append(('tag', content))
            # Text segments are already in main_audio

        # If we have tags or gong, build complex filter
        if len(audio_chain) > 0 or len([s for s in audio_segments if s[0] == 'audio']) > 0:
            # Prepare input files
            inputs = []
            filter_parts = []
            input_idx = 0

            # Add gong if exists
            if os.path.exists('gong.wav'):
                inputs.extend(['-i', 'gong.wav'])
                filter_parts.append(f'[{input_idx}:a]')
                input_idx += 1

            # Check if we need to split main audio for tags
            if len([s for s in audio_segments if s[0] == 'audio']) > 0:
                # We have tags in the text - need to split and insert
                # For now, we'll use a simpler approach: add delays
                delay_ms = 0

                # Add main audio with initial delay if we have tags before it
                first_tag_count = 0
                for seg_type, _ in audio_segments:
                    if seg_type == 'audio':
                        first_tag_count += 1
                    else:
                        break

                if first_tag_count > 0:
                    delay_ms = first_tag_count * 300  # 150ms before + 150ms after per tag

                # Add tagged audio files
                for seg_type, content in audio_segments:
                    if seg_type == 'audio' and os.path.exists(content):
                        inputs.extend(['-i', content])

                # Add main TTS audio
                inputs.extend(['-i', main_audio])

                # Build filter complex
                # Simple concatenation with delays
                filter_complex = ""
                concat_inputs = []

                current_idx = 0
                if os.path.exists('gong.wav'):
                    concat_inputs.append(f'[{current_idx}:a]')
                    current_idx += 1

                # Add tag audio files
                for seg_type, content in audio_segments:
                    if seg_type == 'audio' and os.path.exists(content):
                        # Add 150ms silence before
                        filter_complex += f'[{current_idx}:a]adelay=150|150[tag{current_idx}_delayed];'
                        concat_inputs.append(f'[tag{current_idx}_delayed]')
                        # Add 150ms silence after (will be in the silence between this and next)
                        filter_complex += f'aevalsrc=0:d=0.15[silence{current_idx}];'
                        concat_inputs.append(f'[silence{current_idx}]')
                        current_idx += 1

                # Add main audio with delay if needed
                if delay_ms > 0:
                    filter_complex += f'[{current_idx}:a]adelay={delay_ms}|{delay_ms}[main_delayed];'
                    concat_inputs.append('[main_delayed]')
                else:
                    concat_inputs.append(f'[{current_idx}:a]')

                # Concatenate all
                filter_complex += f'{"".join(concat_inputs)}concat=n={len(concat_inputs)}:v=0:a=1'

                subprocess.run([
                    'ffmpeg', '-y',
                    *inputs,
                    '-filter_complex', filter_complex,
                    output_file
                ], check=True, capture_output=True)
            else:
                # No tags, just gong + main audio
                if os.path.exists('gong.wav'):
                    subprocess.run([
                        'ffmpeg', '-y',
                        '-i', 'gong.wav',
                        '-i', main_audio,
                        '-filter_complex',
                        '[1:a]adelay=250|250[delayed];[0:a][delayed]concat=n=2:v=0:a=1',
                        output_file
                    ], check=True, capture_output=True)
                else:
                    # No gong, just copy
                    shutil.copy2(main_audio, output_file)
        else:
            # No tags, no gong
            shutil.copy2(main_audio, output_file)

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        raise
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        raise
    finally:
        # Cleanup in finally block to ensure it runs even if there's an error
        try:
            if os.path.exists(input_file):
                os.remove(input_file)
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Cleanup error: {e}")

def generate_announcements(client, announcements, voice_id, settings):
    """Generate TTS for all announcements."""
    output_dir = "generated_audio"
    os.makedirs(output_dir, exist_ok=True)

    total = len(announcements)
    success_count = 0
    failed_items = []

    print(f"\nStarting generation of {total} announcements...")
    print(f"Output directory: {output_dir}")
    print("\nSupported audio tags: {nz}, {pz}, {kz}")
    print("Tags will insert corresponding audio files with 150ms delay before and after\n")

    for idx, (station, data) in enumerate(announcements.items(), 1):
        progress = (idx / total) * 100
        print(f"\n[{progress:.1f}%] Processing {idx}/{total}")
        print(f"Station: {station}")

        try:
            announcement_text = data["hlaseni"]

            # Parse audio tags from the text
            audio_segments = parse_audio_tags(announcement_text)

            # Extract only text segments for TTS
            text_only = " ".join([content for seg_type, content in audio_segments if seg_type == 'text'])

            # Show what we're processing
            has_tags = any(seg_type == 'audio' for seg_type, _ in audio_segments)
            if has_tags:
                tag_list = [content for seg_type, content in audio_segments if seg_type == 'audio']
                print(f"Tags found: {', '.join(tag_list)}")

            print("Generating audio...", end="", flush=True)

            # Generate audio with the new API (only for text, not tags)
            audio_generator = client.text_to_speech.convert(
                text=text_only,
                voice_id=voice_id,
                model_id=settings["model_id"],
                voice_settings={
                    "stability": settings["stability"],
                    "similarity_boost": settings["similarity_boost"],
                    "style": settings["style"]
                },
                output_format="mp3_44100_128"
            )

            audio_bytes = b"".join(audio_generator)

            # Audio is now directly bytes that we can write to a file
            temp_mp3 = os.path.join(output_dir, "temp.mp3")
            with open(temp_mp3, "wb") as f:
                f.write(audio_bytes)

            # Determine if this is a terminus announcement
            is_terminus = "(konecna)" in station
            output_filename = f"{data['soubor']}_#terminus.wav" if is_terminus else f"{data['soubor']}.wav"
            output_file = os.path.join(output_dir, output_filename)

            # Process with ffmpeg
            print(" Processing audio...", end="", flush=True)
            process_audio_with_ffmpeg(temp_mp3, output_file, audio_segments, is_terminus)
            print(" ✓")
            print(f"Saved to: {output_file}")
            success_count += 1

        except Exception as e:
            print(" ✗")
            print(f"Error: {str(e)}")
            failed_items.append((station, str(e)))
            continue

    # Print summary
    print("\n" + "="*50)
    print("Generation Summary:")
    print(f"Total announcements: {total}")
    print(f"Successfully generated: {success_count}")
    print(f"Failed: {len(failed_items)}")

    if failed_items:
        print("\nFailed items:")
        for station, error in failed_items:
            print(f"- {station}: {error}")

def main():
    """Main execution function."""
    try:
        print("\nElevenLabs TTS Generator (Enhanced)")
        print("=" * 50)
        print("\nWorkflow:")
        print("1. Setup API key")
        print("2. Select voice")
        print("3. Configure voice settings")
        print("4. Load announcements (JSON or HOF)")
        print("5. Generate audio files with tag support")
        print("=" * 50)

        # Setup API key
        print("\nStep 1: Setting up API key...")
        api_key = setup_api_key()

        # Initialize client
        client = initialize_client(api_key)

        # Select voice
        print("\nStep 2: Selecting voice...")
        try:
            selected_voice = list_voices(client)
            print(f"\nSelected voice: {selected_voice.name}")
        except Exception as e:
            print("\nError: Failed to list voices. Please check your API key and internet connection.")
            print(f"Details: {str(e)}")
            sys.exit(1)

        # Get settings
        print("\nStep 3: Configuring voice settings...")
        settings = get_voice_settings(client, selected_voice.voice_id)

        # Load announcements
        print("\nStep 4: Loading announcements...")
        announcements = load_announcements()

        # Generate TTS
        print("\nStep 5: Generating audio files...")
        generate_announcements(client, announcements, selected_voice.voice_id, settings)

        print("\n" + "=" * 50)
        print("Generation process completed!")
        print("Check the 'generated_audio' directory for the output files.")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
