import os
import json
import sys
import subprocess
import tempfile
import shutil
import re
import hashlib
from dotenv import load_dotenv

# Try importing ElevenLabs, but don't crash if missing (for test mode)
try:
    from elevenlabs.client import ElevenLabs
    import elevenlabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

# Import gTTS for free testing
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

CONFIG_FILE = "config.json"
CACHE_DIR = "tts_cache"

def setup_api_key():
    """Setup ElevenLabs API key."""
    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key and os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            api_key = json.load(f).get('api_key')
    return api_key

def list_voices(client):
    """List available voices."""
    if not client: return None
    try:
        available_voices = client.voices.get_all().voices
        print("\nAvailable ElevenLabs voices:")
        for idx, voice in enumerate(available_voices):
            print(f"{idx + 1}. {voice.name}")
        
        while True:
            try:
                choice = input("\nSelect voice number: ").strip()
                return available_voices[int(choice) - 1]
            except:
                print("Invalid choice.")
    except:
        print("Could not fetch voices.")
        return None

def load_announcements():
    """Load announcements from JSON."""
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and f != 'config.json']
    if not json_files:
        print("No JSON files found.")
        sys.exit(1)
        
    print("\nSelect input file:")
    for idx, f in enumerate(json_files, 1):
        print(f"{idx}. {f}")
    
    try:
        sel = int(input("Choice: ")) - 1
        with open(json_files[sel], 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        print("Invalid selection.")
        sys.exit(1)

def parse_audio_tags(text):
    segments = []
    pattern = r'\{(nz|pz|kz)\}'
    last_end = 0
    for match in re.finditer(pattern, text):
        if match.start() > last_end:
            segments.append(('text', text[last_end:match.start()].strip()))
        segments.append(('audio', match.group(1) + '.wav'))
        last_end = match.end()
    if last_end < len(text):
        segments.append(('text', text[last_end:].strip()))
    if not segments:
        segments.append(('text', text))
    return segments

def combine_audio_files(file_list, output_file):
    if not file_list: return
    if len(file_list) == 1:
        shutil.copy2(file_list[0], output_file)
        return

    try:
        inputs = []
        filter_parts = []
        for idx, f in enumerate(file_list):
            inputs.extend(['-i', f])
            filter_parts.append(f"[{idx}:a]")
        
        filter_complex = "".join(filter_parts) + f"concat=n={len(file_list)}:v=0:a=1"
        subprocess.run(['ffmpeg', '-y', *inputs, '-filter_complex', filter_complex, output_file], 
                      check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error: {e.stderr.decode()}")

def get_cache_key(text, provider, settings):
    """Generate hash based on text and settings."""
    # Include provider in hash so Google cache doesn't mix with ElevenLabs cache
    data_string = f"{text}|{provider}|{str(settings)}"
    hash_object = hashlib.md5(data_string.encode('utf-8'))
    return f"{hash_object.hexdigest()}.mp3"

def generate_announcements(client, announcements, provider, settings, voice_obj=None):
    output_dir = "generated_audio"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    total = len(announcements)
    print(f"\nStarting generation using: {provider}")
    
    for idx, (key, data) in enumerate(announcements.items(), 1):
        print(f"[{idx}/{total}] {key}...", end="", flush=True)
        
        try:
            segments = parse_audio_tags(data["hlaseni"])
            files_to_concat = []
            
            if os.path.exists("gong.wav"):
                files_to_concat.append("gong.wav")

            for seg_type, content in segments:
                if seg_type == 'text':
                    cache_filename = get_cache_key(content, provider, settings)
                    cache_path = os.path.join(CACHE_DIR, cache_filename)

                    if not os.path.exists(cache_path):
                        if provider == "google":
                            # FREE GOOGLE GENERATION
                            tts = gTTS(text=content, lang='cs')
                            tts.save(cache_path)
                        else:
                            # PAID ELEVENLABS GENERATION
                            audio_gen = client.text_to_speech.convert(
                                text=content,
                                voice_id=voice_obj.voice_id,
                                model_id=settings["model_id"],
                                voice_settings=settings["voice_settings"],
                                output_format="mp3_44100_128"
                            )
                            with open(cache_path, "wb") as f:
                                for chunk in audio_gen:
                                    f.write(chunk)
                    
                    files_to_concat.append(cache_path)
                
                elif seg_type == 'audio':
                    if os.path.exists(content):
                        files_to_concat.append(content)

            is_terminus = "(konecna)" in key
            safe_name = data['soubor']
            output_filename = f"{safe_name}_#terminus.wav" if is_terminus else f"{safe_name}.wav"
            final_path = os.path.join(output_dir, output_filename)

            combine_audio_files(files_to_concat, final_path)
            print(" Done.")

        except Exception as e:
            print(f" Failed: {e}")

def main():
    print("--- TTS Generator (Free Testing & Paid Production) ---")
    
    if shutil.which("ffmpeg") is None:
        print("Error: FFmpeg is not installed.")
        sys.exit(1)

    print("\nSelect Provider:")
    print("1. ElevenLabs (Paid - High Quality)")
    print("2. Google TTS (Free - Testing/Robotic)")
    
    mode = input("Choice (1/2): ").strip()

    client = None
    voice_obj = None
    settings = {}
    provider = "google"

    if mode == "1":
        if not ELEVENLABS_AVAILABLE:
            print("Error: 'elevenlabs' library not installed.")
            sys.exit(1)
        provider = "elevenlabs"
        api_key = setup_api_key()
        if not api_key:
            api_key = input("API Key: ")
        
        client = ElevenLabs(api_key=api_key)
        voice_obj = list_voices(client)
        
        print("\nSettings (Press Enter for defaults):")
        stab = input("Stability (0.5): ") or "0.5"
        sim = input("Similarity (0.75): ") or "0.75"
        speed = input("Speed (1.0): ") or "1.0"
        
        settings = {
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": float(stab),
                "similarity_boost": float(sim),
                "speed": float(speed)
            }
        }
    elif mode == "2":
        if not GTTS_AVAILABLE:
            print("Error: 'gTTS' library not installed. Run: pip install gTTS")
            sys.exit(1)
        print("\nUsing Google TTS (Czech). Settings ignored.")
        settings = {"lang": "cs"} # Simple settings for cache key
    else:
        print("Invalid choice.")
        sys.exit(1)

    data = load_announcements()
    generate_announcements(client, data, provider, settings, voice_obj)

if __name__ == "__main__":
    main()