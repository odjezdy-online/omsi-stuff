import os
import json
import sys
import subprocess
import tempfile
import shutil
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

def load_announcements():
    """Load announcements from JSON file."""
    default_file = "zastavky.json"
    
    # Try to load default file first
    if os.path.exists(default_file):
        print(f"\nFound default announcements file: {default_file}")
        try:
            with open(default_file, 'r', encoding='utf-8') as f:
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

def process_audio_with_ffmpeg(input_file, output_file, is_terminus=False):
    """Process audio file with ffmpeg to add gong and convert to wav."""
    temp_dir = None
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_output = os.path.join(temp_dir, "temp_output.wav")
        
        # Convert to wav first
        subprocess.run([
            'ffmpeg', '-y', '-i', input_file,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            temp_output
        ], check=True, capture_output=True)
        
        if os.path.exists('gong.wav'):
            # Create the final output with gong
            subprocess.run([
                'ffmpeg', '-y',
                '-i', 'gong.wav',
                '-i', temp_output,
                '-filter_complex',
                '[1:a]adelay=250|250[delayed];[0:a][delayed]concat=n=2:v=0:a=1',
                output_file
            ], check=True, capture_output=True)
        else:
            # If no gong file, just copy the temp wav
            shutil.copy2(temp_output, output_file)
            
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
    
    for idx, (station, data) in enumerate(announcements.items(), 1):
        progress = (idx / total) * 100
        print(f"\n[{progress:.1f}%] Processing {idx}/{total}")
        print(f"Station: {station}")
        
        try:
            print("Generating audio...", end="", flush=True)
            
            # Generate audio with the new API
            audio_generator = client.text_to_speech.convert(
                text=data["hlaseni"],
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
            process_audio_with_ffmpeg(temp_mp3, output_file, is_terminus)
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
        print("\nElevenLabs TTS Generator")
        print("=" * 50)
        print("\nWorkflow:")
        print("1. Setup API key")
        print("2. Select voice")
        print("3. Configure voice settings")
        print("4. Load announcements")
        print("5. Generate audio files")
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