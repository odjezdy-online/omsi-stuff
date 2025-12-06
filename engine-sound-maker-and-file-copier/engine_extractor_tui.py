#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Engine Sound Extractor for OMSI - TUI Version
Pro použití v Google Colab, terminálech a skriptech
"""

import os
import sys
import argparse
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from moviepy.editor import VideoFileClip
from scipy import signal
from tqdm import tqdm


class EngineExtractor:
    """Hlavní třída pro extrakci motorových zvuků"""
    
    def __init__(self, video_path, output_dir, settings):
        self.video_path = video_path
        self.output_dir = output_dir
        self.settings = settings
        
    def extract(self):
        """Hlavní extrakční proces"""
        try:
            print("\n" + "="*70)
            print("ZAČÍNÁM ZPRACOVÁNÍ VIDEA")
            print("="*70)
            
            # 1. Extrakce audia
            print("\n[1/6] Extrakce audia z videa...")
            temp_audio = self._extract_audio()
            
            # 2. Načtení audia
            print("\n[2/6] Načítání audia...")
            y, sr = self._load_audio(temp_audio)
            
            # 3. Odstranění šumu/AI separace
            print("\n[3/6] Zpracování audia...")
            y_clean = self._process_audio(y, sr)
            
            # 4. Frekvenční filtrování
            print("\n[4/6] Frekvenční filtrování...")
            y_filtered = self._frequency_filter(y_clean, sr)
            
            # 5. Export kompletního zvuku
            if self.settings['export_full']:
                print("\n[5/6] Export kompletního zvuku...")
                self._export_full(y_filtered, sr)
            
            # 6. Segmentace podle RPM
            if self.settings['export_segments']:
                print("\n[6/6] Segmentace podle RPM...")
                self._segment_rpm(y_filtered, sr)
            
            # Cleanup
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            
            print("\n" + "="*70)
            print("✓ HOTOVO! Všechny zvuky byly úspěšně zpracovány.")
            print(f"✓ Výstupní složka: {self.output_dir}")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n✗ CHYBA: {str(e)}\n")
            return False
    
    def _extract_audio(self):
        """Extrahuje audio z videa"""
        video = VideoFileClip(self.video_path)
        audio = video.audio
        
        if audio is None:
            raise ValueError("Video neobsahuje audio stopu!")
        
        temp_audio = os.path.join(self.output_dir, "temp_audio.wav")
        audio.write_audiofile(temp_audio, verbose=False, logger=None)
        video.close()
        
        print(f"  ✓ Audio extrahováno")
        return temp_audio
    
    def _load_audio(self, temp_audio):
        """Načte audio soubor"""
        if self.settings['method'] == 'ai_demucs' or self.settings['method'] == 'ai_yamnet':
            y, sr = librosa.load(temp_audio, sr=None, mono=False)
            if y.ndim == 1:
                y = np.stack([y, y])
            print(f"  ✓ Sample rate: {sr} Hz")
            print(f"  ✓ Kanály: {y.shape[0]} (stereo)")
            print(f"  ✓ Délka: {y.shape[1]/sr:.2f} sekund")
        else:
            y, sr = librosa.load(temp_audio, sr=None, mono=True)
            print(f"  ✓ Sample rate: {sr} Hz")
            print(f"  ✓ Délka: {len(y)/sr:.2f} sekund")
        
        return y, sr
    
    def _process_audio(self, y, sr):
        """Zpracuje audio (noise reduction nebo AI separace)"""
        
        if self.settings['method'] == 'ai_demucs':
            return self._process_demucs(y, sr)
        elif self.settings['method'] == 'ai_yamnet':
            return self._process_yamnet(y, sr)
        elif self.settings['method'] == 'classic' and self.settings['noise_reduction'] > 0:
            return self._process_classic(y, sr)
        else:
            return y
    
    def _process_demucs(self, y, sr):
        """AI separace pomocí Demucs"""
        print(f"  AI Separace pomocí Demucs...")
        print(f"  Model: {self.settings['ai_model']}")
        
        try:
            from demucs.pretrained import get_model
            from demucs.apply import apply_model
            import torch
            
            print(f"  Načítám AI model...")
            model = get_model(self.settings['ai_model'])
            model.eval()
            
            print(f"  Připravuji audio data...")
            audio_tensor = torch.from_numpy(y).float().unsqueeze(0)
            
            print(f"  Spouštím AI separaci (může trvat několik minut)...")
            
            with torch.no_grad():
                sources = apply_model(model, audio_tensor, device='cpu', progress=True)
            
            other_stereo = sources[0, 2].numpy()
            other_mono = np.mean(other_stereo, axis=0)
            y_clean = other_mono / (np.abs(other_mono).max() + 1e-8)
            
            print("  ✓ AI separace dokončena!")
            print(f"  ✓ Lidský hlas a hudba odstraněny")
            
            return y_clean
            
        except ImportError:
            print("  ✗ CHYBA: Demucs není nainstalován!")
            print("  Nainstaluj pomocí: pip install demucs torch")
            print("  Pokračuji bez AI separace...")
            return np.mean(y, axis=0) if y.ndim == 2 else y
        except Exception as e:
            print(f"  ✗ CHYBA: {str(e)}")
            print("  Pokračuji bez AI separace...")
            return np.mean(y, axis=0) if y.ndim == 2 else y
    
    def _process_yamnet(self, y, sr):
        """AI klasifikace pomocí YAMNet"""
        print(f"  AI Klasifikace pomocí YAMNet...")
        
        try:
            import tensorflow as tf
            import tensorflow_hub as hub
            
            print(f"  Načítám YAMNet model...")
            yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')
            
            print(f"  Analyzuji zvuky...")
            
            # Convert stereo to mono if needed
            if y.ndim == 2:
                y_mono = np.mean(y, axis=0)
            else:
                y_mono = y
            
            # YAMNet expects float32 in [-1.0, 1.0]
            y_normalized = y_mono.astype(np.float32)
            
            # Get predictions
            scores, embeddings, spectrogram = yamnet_model(y_normalized)
            
            # Find frames with engine sounds (class 444: "Vehicle")
            class_names = yamnet_model.class_names
            vehicle_idx = None
            for i, name in enumerate(class_names):
                if 'vehicle' in name.lower() or 'engine' in name.lower():
                    vehicle_idx = i
                    break
            
            if vehicle_idx is not None:
                # Create mask for engine sounds
                engine_mask = scores[:, vehicle_idx] > 0.3
                print(f"  ✓ Detekováno {engine_mask.sum()} engine sound framů")
            else:
                print(f"  ⚠ Nenalezena engine sound třída, použiji celé audio")
                engine_mask = np.ones(len(scores), dtype=bool)
            
            # Filter audio based on mask
            # This is simplified - proper implementation would use mask on spectrogram
            print(f"  ✓ YAMNet klasifikace dokončena")
            
            return y_mono
            
        except ImportError:
            print("  ✗ CHYBA: TensorFlow/TensorFlow Hub není nainstalován!")
            print("  Nainstaluj pomocí: pip install tensorflow tensorflow-hub")
            print("  Pokračuji bez AI klasifikace...")
            return np.mean(y, axis=0) if y.ndim == 2 else y
        except Exception as e:
            print(f"  ✗ CHYBA: {str(e)}")
            print("  Pokračuji bez AI klasifikace...")
            return np.mean(y, axis=0) if y.ndim == 2 else y
    
    def _process_classic(self, y, sr):
        """Klasický noise reduction"""
        print(f"  Klasický Noise reduction (úroveň: {self.settings['noise_reduction']})...")
        
        noise_sample = y[:int(sr * 2)]
        y_clean = nr.reduce_noise(
            y=y, 
            sr=sr,
            y_noise=noise_sample,
            prop_decrease=self.settings['noise_reduction'] / 100.0,
            stationary=False
        )
        print("  ✓ Šum odstraněn")
        return y_clean
    
    def _frequency_filter(self, y, sr):
        """Frekvenční filtrování"""
        print(f"  Filtruji {self.settings['freq_low']}-{self.settings['freq_high']} Hz...")
        
        sos = signal.butter(
            4, 
            [self.settings['freq_low'], self.settings['freq_high']], 
            btype='band', 
            fs=sr, 
            output='sos'
        )
        y_filtered = signal.sosfilt(sos, y)
        print("  ✓ Motorové frekvence vyfiltrované")
        
        return y_filtered
    
    def _export_full(self, y, sr):
        """Export kompletního zvuku"""
        output_file = os.path.join(self.output_dir, "engine_sound_full.wav")
        sf.write(output_file, y, sr)
        print(f"  ✓ Uloženo: {output_file}")
    
    def _segment_rpm(self, y, sr):
        """Segmentace podle RPM"""
        engine_configs = {
            'fpt_nef6_184': {
                'name': 'FPT NEF 6 (6V, 6.7L, 184kW)',
                'multiplier': 20,
                'idle': 600,
                'max': 2500,
                'typical': [600, 800, 1000, 1200, 1500, 1800, 2100, 2400]
            },
            'iveco_cursor8': {
                'name': 'IVECO Cursor 8 (6V, 7.8L)',
                'multiplier': 20,
                'idle': 600,
                'max': 2500,
                'typical': [600, 850, 1100, 1350, 1600, 1850, 2100, 2400]
            },
            'generic_6cyl': {
                'name': 'Obecný 6V diesel',
                'multiplier': 20,
                'idle': 600,
                'max': 2500,
                'typical': [600, 900, 1200, 1500, 1800, 2100, 2400]
            },
        }
        
        config = engine_configs.get(
            self.settings['engine_type'], 
            engine_configs['generic_6cyl']
        )
        
        print(f"  Motor: {config['name']}")
        print(f"  RPM rozsah: {config['idle']}-{config['max']}")
        
        audio_length_sec = len(y) / sr
        num_segments = self.settings['num_segments']
        
        # Pro dlouhá videa použij fallback
        if audio_length_sec > 600:
            print(f"  ⚠ Dlouhé video ({audio_length_sec/60:.1f} min)")
            print(f"  → Použiji rovnoměrné rozdělení")
            
            segment_length = len(y) // num_segments
            rpm_range = config['typical']
            
            for i in tqdm(range(num_segments), desc="  Exportuji segmenty"):
                start = i * segment_length
                end = start + segment_length if i < num_segments - 1 else len(y)
                rpm = rpm_range[min(i, len(rpm_range)-1)] if i < len(rpm_range) else config['max']
                
                output_file = os.path.join(self.output_dir, f"engine_{rpm}rpm.wav")
                sf.write(output_file, y[start:end], sr)
        
        else:
            # Pitch detection pro kratší videa
            print(f"  Spouštím pitch detection...")
            
            try:
                hop_length = 512
                
                f0, _, _ = librosa.pyin(
                    y,
                    fmin=max(65, config['idle'] / config['multiplier'] * 0.9),
                    fmax=min(2000, config['max'] / config['multiplier'] * 1.1),
                    sr=sr,
                    hop_length=hop_length,
                    frame_length=hop_length * 4
                )
                
                print(f"  ✓ Pitch detection dokončen!")
                
                f0_clean = f0[~np.isnan(f0)]
                
                if len(f0_clean) > 0:
                    rpm_estimates = f0_clean * config['multiplier']
                    percentiles = np.linspace(0, 100, num_segments + 1)
                    rpm_thresholds = np.percentile(rpm_estimates, percentiles)
                    
                    print(f"  RPM rozsah: {rpm_estimates.min():.0f} - {rpm_estimates.max():.0f}")
                    
                    segment_length_samples = int(5 * sr)  # 5 sekund
                    
                    for i in tqdm(range(num_segments), desc="  Exportuji segmenty"):
                        rpm_mid = int((rpm_thresholds[i] + rpm_thresholds[i + 1]) / 2)
                        
                        time_to_samples = len(y) / len(f0)
                        matching_indices = np.where(
                            (f0 >= rpm_thresholds[i]/config['multiplier']) & 
                            (f0 < rpm_thresholds[i + 1]/config['multiplier'])
                        )[0]
                        
                        if len(matching_indices) > 0:
                            mid_idx = matching_indices[len(matching_indices)//2]
                            sample_idx = int(mid_idx * time_to_samples)
                            start = max(0, sample_idx - segment_length_samples//2)
                            end = min(len(y), start + segment_length_samples)
                        else:
                            start = int(i * len(y) / num_segments)
                            end = int((i + 1) * len(y) / num_segments)
                        
                        output_file = os.path.join(self.output_dir, f"engine_{rpm_mid}rpm.wav")
                        sf.write(output_file, y[start:end], sr)
                
                else:
                    raise ValueError("Pitch detection selhala")
                    
            except Exception as e:
                print(f"  ⚠ Pitch detection selhal: {e}")
                print(f"  → Použiji rovnoměrné rozdělení")
                
                segment_length = len(y) // num_segments
                rpm_range = config['typical']
                
                for i in tqdm(range(num_segments), desc="  Exportuji segmenty"):
                    start = i * segment_length
                    end = start + segment_length if i < num_segments - 1 else len(y)
                    rpm = rpm_range[min(i, len(rpm_range)-1)] if i < len(rpm_range) else config['max']
                    
                    output_file = os.path.join(self.output_dir, f"engine_{rpm}rpm.wav")
                    sf.write(output_file, y[start:end], sr)
        
        print(f"  ✓ Segmenty vyexportovány")


def interactive_mode():
    """Interaktivní TUI režim"""
    print("="*70)
    print("Engine Sound Extractor for OMSI - TUI")
    print("="*70)
    
    # Video path
    video_path = input("\n📹 Cesta k videu: ").strip()
    if not os.path.exists(video_path):
        print("✗ Video neexistuje!")
        return
    
    # Output directory
    default_output = os.path.join(os.path.dirname(video_path), "engine_sounds")
    output_dir = input(f"\n📁 Výstupní složka [{default_output}]: ").strip()
    if not output_dir:
        output_dir = default_output
    os.makedirs(output_dir, exist_ok=True)
    
    # Method
    print("\n🔧 Metoda zpracování:")
    print("  1. Klasický noise reduction (rychlý)")
    print("  2. AI separace - Demucs (pomalejší, lepší)")
    print("  3. AI klasifikace - YAMNet (experimentální)")
    method_choice = input("Vyber (1-3) [2]: ").strip() or "2"
    
    method_map = {
        '1': 'classic',
        '2': 'ai_demucs',
        '3': 'ai_yamnet'
    }
    method = method_map.get(method_choice, 'ai_demucs')
    
    # Noise reduction level (only for classic)
    noise_reduction = 0
    if method == 'classic':
        noise_reduction = int(input("\n🔇 Úroveň noise reduction (0-100) [50]: ").strip() or "50")
    
    # AI model (only for Demucs)
    ai_model = 'htdemucs'
    if method == 'ai_demucs':
        print("\n🤖 AI Model:")
        print("  1. htdemucs (doporučený)")
        print("  2. htdemucs_ft (rychlejší)")
        print("  3. mdx_extra (nejlepší kvalita)")
        model_choice = input("Vyber (1-3) [1]: ").strip() or "1"
        model_map = {'1': 'htdemucs', '2': 'htdemucs_ft', '3': 'mdx_extra'}
        ai_model = model_map.get(model_choice, 'htdemucs')
    
    # Frequency filter
    freq_low = int(input("\n📊 Dolní frekvence (Hz) [80]: ").strip() or "80")
    freq_high = int(input("📊 Horní frekvence (Hz) [500]: ").strip() or "500")
    
    # Engine type
    print("\n🚌 Typ motoru:")
    print("  1. FPT NEF 6 (6V, 6.7L)")
    print("  2. IVECO Cursor 8 (6V, 7.8L)")
    print("  3. Obecný 6V diesel")
    engine_choice = input("Vyber (1-3) [2]: ").strip() or "2"
    engine_map = {'1': 'fpt_nef6_184', '2': 'iveco_cursor8', '3': 'generic_6cyl'}
    engine_type = engine_map.get(engine_choice, 'iveco_cursor8')
    
    # Export options
    export_full = input("\n💾 Exportovat kompletní zvuk? (a/n) [a]: ").strip().lower() != 'n'
    export_segments = input("💾 Exportovat segmenty podle RPM? (a/n) [a]: ").strip().lower() != 'n'
    
    num_segments = 5
    if export_segments:
        num_segments = int(input("   Počet segmentů (2-20) [5]: ").strip() or "5")
    
    # Settings
    settings = {
        'method': method,
        'noise_reduction': noise_reduction,
        'ai_model': ai_model,
        'freq_low': freq_low,
        'freq_high': freq_high,
        'export_full': export_full,
        'export_segments': export_segments,
        'num_segments': num_segments,
        'engine_type': engine_type
    }
    
    # Process
    extractor = EngineExtractor(video_path, output_dir, settings)
    extractor.extract()


def main():
    parser = argparse.ArgumentParser(
        description='Engine Sound Extractor for OMSI - TUI Version'
    )
    
    parser.add_argument('video', nargs='?', help='Cesta k video souboru')
    parser.add_argument('-o', '--output', help='Výstupní složka')
    parser.add_argument('-m', '--method', choices=['classic', 'ai_demucs', 'ai_yamnet'], 
                        default='ai_demucs', help='Metoda zpracování')
    parser.add_argument('--model', default='htdemucs', 
                        help='AI model (htdemucs, htdemucs_ft, mdx_extra)')
    parser.add_argument('-n', '--noise', type=int, default=50, 
                        help='Úroveň noise reduction (0-100)')
    parser.add_argument('--freq-low', type=int, default=80, 
                        help='Dolní frekvence (Hz)')
    parser.add_argument('--freq-high', type=int, default=500, 
                        help='Horní frekvence (Hz)')
    parser.add_argument('-e', '--engine', default='iveco_cursor8',
                        help='Typ motoru')
    parser.add_argument('--no-full', action='store_true', 
                        help='Neexportovat kompletní zvuk')
    parser.add_argument('--no-segments', action='store_true', 
                        help='Neexportovat segmenty')
    parser.add_argument('-s', '--segments', type=int, default=5, 
                        help='Počet segmentů (2-20)')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Interaktivní režim')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive or not args.video:
        interactive_mode()
        return
    
    # CLI mode
    if not os.path.exists(args.video):
        print(f"✗ Video neexistuje: {args.video}")
        return
    
    output_dir = args.output or os.path.join(
        os.path.dirname(args.video), 
        "engine_sounds"
    )
    os.makedirs(output_dir, exist_ok=True)
    
    settings = {
        'method': args.method,
        'noise_reduction': args.noise,
        'ai_model': args.model,
        'freq_low': args.freq_low,
        'freq_high': args.freq_high,
        'export_full': not args.no_full,
        'export_segments': not args.no_segments,
        'num_segments': args.segments,
        'engine_type': args.engine
    }
    
    extractor = EngineExtractor(args.video, output_dir, settings)
    success = extractor.extract()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
