#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Engine Sound Extractor for OMSI - Version 2.0
Extrahuje a zpracovává motorové zvuky z videa pro použití v OMSI Bus Simulator
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QCheckBox, QProgressBar, 
    QFileDialog, QGroupBox, QSpinBox, QComboBox, QRadioButton,
    QButtonGroup, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont

import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from moviepy.editor import VideoFileClip
from scipy import signal


class AudioProcessor(QThread):
    """Thread pro zpracování audia na pozadí"""
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, video_path, output_dir, settings):
        super().__init__()
        self.video_path = video_path
        self.output_dir = output_dir
        self.settings = settings
        
    def run(self):
        try:
            print("\n" + "="*70)
            print("ZAČÍNÁM ZPRACOVÁNÍ VIDEA")
            print("="*70)
            
            # 1. Extrakce audia z videa
            self.status.emit("Extrahuji audio z videa...")
            self.progress.emit(10)
            print("\n[1/6] Extrakce audia z videa...")
            
            video = VideoFileClip(self.video_path)
            audio = video.audio
            
            if audio is None:
                self.finished.emit(False, "Video neobsahuje audio stopu!")
                return
            
            temp_audio = os.path.join(self.output_dir, "temp_audio.wav")
            audio.write_audiofile(temp_audio, verbose=False, logger=None)
            video.close()
            
            print(f"✓ Audio extrahováno: {temp_audio}")
            
            # 2. Načtení audia
            self.status.emit("Načítám audio...")
            self.progress.emit(20)
            print("\n[2/6] Načítání audia...")
            
            if self.settings['use_ai_separation']:
                y, sr = librosa.load(temp_audio, sr=None, mono=False)
                if y.ndim == 1:
                    y = np.stack([y, y])
                print(f"✓ Sample rate: {sr} Hz")
                print(f"✓ Kanály: {y.shape[0]} (stereo)")
                print(f"✓ Délka: {y.shape[1]/sr:.2f} sekund")
            else:
                y, sr = librosa.load(temp_audio, sr=None, mono=True)
                print(f"✓ Sample rate: {sr} Hz")
                print(f"✓ Délka: {len(y)/sr:.2f} sekund")
            
            # 3. Noise reduction / AI separace
            if self.settings['use_ai_separation']:
                self.status.emit("Spouštím AI separaci (Demucs)...")
                self.progress.emit(35)
                print(f"\n[3/6] AI Separace pomocí Demucs...")
                print(f"  Model: {self.settings['ai_model']}")
                print(f"  ⚠️ První spuštění stáhne model (~250 MB)")
                print(f"  ⏱️ Zpracování může trvat 2-5 minut...")
                
                try:
                    from demucs.pretrained import get_model
                    from demucs.apply import apply_model
                    import torch
                    
                    print(f"  Načítám AI model...")
                    model = get_model(self.settings['ai_model'])
                    model.eval()
                    
                    print(f"  Připravuji audio data...")
                    audio_tensor = torch.from_numpy(y).float().unsqueeze(0)
                    
                    print(f"  Spouštím AI separaci...")
                    self.status.emit("AI zpracovává audio (může trvat několik minut)...")
                    
                    with torch.no_grad():
                        sources = apply_model(model, audio_tensor, device='cpu', progress=True)
                    
                    other_stereo = sources[0, 2].numpy()
                    other_mono = np.mean(other_stereo, axis=0)
                    y_clean = other_mono / (np.abs(other_mono).max() + 1e-8)
                    
                    print("  ✓ AI separace dokončena!")
                    print(f"  ✓ Lidský hlas a hudba odstraněny")
                    print(f"  ✓ Výstup: mono, {len(y_clean)/sr:.1f}s")
                    
                except ImportError:
                    print("  ✗ CHYBA: Demucs není nainstalován!")
                    print("  Nainstaluj pomocí: pip install demucs torch")
                    print("  Pokračuji bez AI separace...")
                    y_clean = np.mean(y, axis=0) if y.ndim == 2 else y
                except Exception as e:
                    print(f"  ✗ CHYBA při AI separaci: {str(e)}")
                    print("  Pokračuji bez AI separace...")
                    y_clean = np.mean(y, axis=0) if y.ndim == 2 else y
                    
            elif self.settings['noise_reduction'] > 0:
                self.status.emit("Odstraňuji šum...")
                self.progress.emit(35)
                print(f"\n[3/6] Klasický Noise reduction (úroveň: {self.settings['noise_reduction']})...")
                
                noise_sample = y[:int(sr * 2)]
                y_clean = nr.reduce_noise(
                    y=y, 
                    sr=sr,
                    y_noise=noise_sample,
                    prop_decrease=self.settings['noise_reduction'] / 100.0,
                    stationary=False
                )
                print("  ✓ Šum odstraněn")
            else:
                y_clean = y
                print("\n[3/6] Noise reduction přeskočen")
            
            # 4. Frekvenční filtrování
            self.status.emit("Filtruji motorové frekvence...")
            self.progress.emit(50)
            print(f"\n[4/6] Frekvenční filtrování ({self.settings['freq_low']}-{self.settings['freq_high']} Hz)...")
            
            sos = signal.butter(
                4, 
                [self.settings['freq_low'], self.settings['freq_high']], 
                btype='band', 
                fs=sr, 
                output='sos'
            )
            y_filtered = signal.sosfilt(sos, y_clean)
            print("  ✓ Motorové frekvence vyfiltrované")
            
            # 5. Export kompletního zvuku
            if self.settings['export_full']:
                self.status.emit("Ukládám kompletní zvuk...")
                self.progress.emit(65)
                print("\n[5/6] Export kompletního zvuku...")
                
                output_file = os.path.join(self.output_dir, "engine_sound_full.wav")
                sf.write(output_file, y_filtered, sr)
                print(f"  ✓ Uloženo: {output_file}")
            
            # 6. Segmentace podle RPM
            if self.settings['export_segments']:
                self.status.emit("Analyzuji a segmentuji podle RPM...")
                self.progress.emit(70)
                print("\n[6/6] Segmentace podle RPM...")
                
                segments = self._segment_by_rpm(
                    y_filtered, 
                    sr, 
                    self.settings['num_segments'],
                    self.settings['engine_type']
                )
                
                print(f"\n  Exportuji {len(segments)} segmentů...")
                for i, (segment_data, rpm_estimate) in enumerate(segments):
                    progress = 70 + int((i / len(segments)) * 25)
                    self.progress.emit(progress)
                    
                    self.status.emit(f"Ukládám segment {i+1}/{len(segments)}: {rpm_estimate} RPM...")
                    
                    output_file = os.path.join(
                        self.output_dir, 
                        f"engine_{rpm_estimate}rpm.wav"
                    )
                    sf.write(output_file, segment_data, sr)
                    print(f"  ✓ Segment {i+1}/{len(segments)}: {rpm_estimate} RPM ({len(segment_data)/sr:.1f}s) → {os.path.basename(output_file)}")
            else:
                print("\n[6/6] Segmentace podle RPM přeskočena")
            
            # Cleanup
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            
            self.progress.emit(100)
            print("\n" + "="*70)
            print("✓ HOTOVO! Všechny zvuky byly úspěšně zpracovány.")
            print("="*70 + "\n")
            
            self.finished.emit(True, "Zpracování dokončeno!")
            
        except Exception as e:
            print(f"\n✗ CHYBA: {str(e)}\n")
            self.finished.emit(False, f"Chyba: {str(e)}")
    
    def _segment_by_rpm(self, y, sr, num_segments, engine_type):
        """Segmentuje audio podle odhadovaných RPM"""
        
        engine_configs = {
            'fpt_nef6_184': {
                'name': 'FPT NEF 6 (6V, 6.7L, 184kW)',
                'multiplier': 20,
                'idle': 600,
                'max': 2500,
                'typical': [600, 800, 1000, 1200, 1500, 1800, 2100, 2400]
            },
            'fpt_nef6_210': {
                'name': 'FPT NEF 6 (6V, 6.7L, 210kW)',
                'multiplier': 20,
                'idle': 600,
                'max': 2500,
                'typical': [600, 850, 1050, 1250, 1500, 1800, 2100, 2400]
            },
            'fpt_nef4': {
                'name': 'FPT NEF 4 (4V, 4.5L)',
                'multiplier': 30,
                'idle': 650,
                'max': 2800,
                'typical': [650, 900, 1150, 1400, 1700, 2000, 2400, 2700]
            },
            'fpt_cursor8': {
                'name': 'FPT Cursor 8 (6V, 6.7L) - NB 12',
                'multiplier': 20,
                'idle': 600,
                'max': 2500,
                'typical': [600, 800, 1000, 1250, 1500, 1750, 2100, 2400]
            },
            'fpt_cursor9': {
                'name': 'FPT Cursor 9 (6V, 8.7L) - NB 18',
                'multiplier': 20,
                'idle': 550,
                'max': 2300,
                'typical': [550, 750, 950, 1150, 1400, 1650, 1900, 2200]
            },
            'iveco_cursor8': {
                'name': 'IVECO Cursor 8 (6V, 7.8L)',
                'multiplier': 20,
                'idle': 600,
                'max': 2500,
                'typical': [600, 850, 1100, 1350, 1600, 1850, 2100, 2400]
            },
            'mercedes_om906': {
                'name': 'Mercedes OM906 (6V, 6.4L)',
                'multiplier': 20,
                'idle': 650,
                'max': 2400,
                'typical': [650, 850, 1050, 1250, 1500, 1750, 2000, 2300]
            },
            'cummins_isbe': {
                'name': 'Cummins ISBe (6V, 6.7L)',
                'multiplier': 20,
                'idle': 600,
                'max': 2500,
                'typical': [600, 850, 1100, 1350, 1600, 1850, 2100, 2400]
            },
            'cummins_isl': {
                'name': 'Cummins ISL (6V, 8.9L)',
                'multiplier': 20,
                'idle': 550,
                'max': 2300,
                'typical': [550, 750, 950, 1150, 1400, 1650, 1900, 2200]
            },
            'generic_6cyl': {
                'name': 'Obecný 6V diesel',
                'multiplier': 20,
                'idle': 600,
                'max': 2500,
                'typical': [600, 900, 1200, 1500, 1800, 2100, 2400]
            },
            'generic_4cyl': {
                'name': 'Obecný 4V diesel',
                'multiplier': 30,
                'idle': 700,
                'max': 3000,
                'typical': [700, 1000, 1300, 1600, 2000, 2400, 2800]
            }
        }
        
        config = engine_configs.get(engine_type, engine_configs['generic_6cyl'])
        
        print(f"\n  Detekuji změny v pitch/RPM...")
        print(f"  Motor: {config['name']}")
        print(f"  RPM rozsah: {config['idle']}-{config['max']}")
        
        self.status.emit(f"Vytvářím RPM segmenty...")
        
        # Pro dlouhá videa (>10 min) přeskoč pitch detection - moc RAM náročné
        audio_length_sec = len(y) / sr
        
        if audio_length_sec > 600:  # Delší než 10 minut
            print(f"  ⚠️ Dlouhé video ({audio_length_sec/60:.1f} min)")
            print(f"  ⚠️ Pitch detection je moc náročný na RAM pro dlouhá videa")
            print(f"  → Použiji rovnoměrné rozdělení podle typických RPM pro tento motor")
            
            # Rovnoměrné rozdělení bez pitch detection
            segment_length = len(y) // num_segments
            segments = []
            rpm_range = config['typical']
            
            for i in range(num_segments):
                start = i * segment_length
                end = start + segment_length if i < num_segments - 1 else len(y)
                rpm = rpm_range[min(i, len(rpm_range)-1)] if i < len(rpm_range) else config['max']
                segments.append((y[start:end], rpm))
                print(f"  Segment {i+1}/{num_segments}: {rpm} RPM ({len(y[start:end])/sr:.1f}s)")
            
            return segments
        
        # Pro kratší videa použij pitch detection
        print(f"  Spouštím pitch detection...")
        hop_length = 512
        
        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                fmin=config['idle'] / config['multiplier'] * 0.8,
                fmax=config['max'] / config['multiplier'] * 1.2,
                sr=sr,
                hop_length=hop_length
            )
        except (MemoryError, ValueError) as e:
            print(f"  ✗ Chyba při pitch detection: {str(e)}")
            print(f"  Použiji fallback: rovnoměrné rozdělení podle typu motoru")
            # Fallback bez pitch detection
            segment_length = len(y) // num_segments
            segments = []
            rpm_range = config['typical']
            for i in range(num_segments):
                start = i * segment_length
                end = start + segment_length if i < num_segments - 1 else len(y)
                rpm = rpm_range[min(i, len(rpm_range)-1)] if i < len(rpm_range) else config['max']
                segments.append((y[start:end], rpm))
                print(f"  Segment {i+1}: {rpm} RPM ({len(y[start:end])/sr:.1f}s)")
            return segments
        
        print(f"  ✓ Pitch detection dokončen!")
        self.status.emit("Zpracovávám pitch data...")
        
        f0_clean = f0[~np.isnan(f0)]
        
        if len(f0_clean) == 0:
            print("  ⚠ Nelze detekovat pitch, použiji rovnoměrné rozdělení")
            segment_length = len(y) // num_segments
            segments = []
            rpm_range = config['typical']
            for i in range(num_segments):
                start = i * segment_length
                end = start + segment_length if i < num_segments - 1 else len(y)
                rpm = rpm_range[min(i, len(rpm_range)-1)] if i < len(rpm_range) else config['max']
                segments.append((y[start:end], rpm))
            return segments
        
        rpm_estimates = f0_clean * config['multiplier']
        
        percentiles = np.linspace(0, 100, num_segments + 1)
        rpm_thresholds = np.percentile(rpm_estimates, percentiles)
        
        print(f"  RPM rozsah detekován: {rpm_estimates.min():.0f} - {rpm_estimates.max():.0f}")
        
        self.status.emit("Vytvářím RPM segmenty...")
        
        segments = []
        segment_length_sec = 5
        segment_length_samples = int(segment_length_sec * sr)
        
        print(f"  Vytvářím {num_segments} segmentů...")
        
        for i in range(num_segments):
            rpm_low = rpm_thresholds[i]
            rpm_high = rpm_thresholds[i + 1]
            rpm_mid = (rpm_low + rpm_high) / 2
            
            time_to_samples = len(y) / len(f0)
            matching_indices = np.where(
                (f0 >= rpm_low/config['multiplier']) & (f0 < rpm_high/config['multiplier'])
            )[0]
            
            if len(matching_indices) > 0:
                mid_idx = matching_indices[len(matching_indices)//2]
                sample_idx = int(mid_idx * time_to_samples)
                
                start = max(0, sample_idx - segment_length_samples//2)
                end = min(len(y), start + segment_length_samples)
                segment_data = y[start:end]
            else:
                start = int(i * len(y) / num_segments)
                end = int((i + 1) * len(y) / num_segments)
                segment_data = y[start:end]
            
            segments.append((segment_data, int(rpm_mid)))
            print(f"  Segment {i+1}: ~{int(rpm_mid)} RPM ({len(segment_data)/sr:.1f}s)")
        
        return segments


class DropArea(QLabel):
    """Widget pro drag & drop videa"""
    fileDropped = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText("⬇️\n\nPřetáhni sem video\n\n(.mp4, .avi, .mov, .mkv)")
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #666;
                border-radius: 10px;
                padding: 40px;
                font-size: 16px;
                background-color: palette(base);
            }
            QLabel:hover {
                border-color: #0d7ac7;
                background-color: palette(alternate-base);
            }
        """)
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                event.accept()
                self.setStyleSheet("""
                    QLabel {
                        border: 3px solid #0d7ac7;
                        border-radius: 10px;
                        padding: 40px;
                        font-size: 16px;
                        background-color: palette(alternate-base);
                    }
                """)
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #666;
                border-radius: 10px;
                padding: 40px;
                font-size: 16px;
                background-color: palette(base);
            }
            QLabel:hover {
                border-color: #0d7ac7;
                background-color: palette(alternate-base);
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                event.accept()
                self.setText(f"✓ Video načteno:\n\n{os.path.basename(file_path)}")
                self.fileDropped.emit(file_path)
            else:
                event.ignore()
                self.setText("⚠️ Nepodporovaný formát!\n\nPoužij .mp4, .avi, .mov nebo .mkv")
        else:
            event.ignore()
        
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #666;
                border-radius: 10px;
                padding: 40px;
                font-size: 16px;
                background-color: palette(base);
            }
            QLabel:hover {
                border-color: #0d7ac7;
                background-color: palette(alternate-base);
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_path = None
        self.output_dir = str(Path.home() / "Desktop")
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Engine Sound Extractor for OMSI")
        self.setMinimumSize(800, 900)
        
        # Centrální widget se scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)
        
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # === DROP AREA ===
        self.drop_area = DropArea()
        self.drop_area.fileDropped.connect(self.on_file_dropped)
        main_layout.addWidget(self.drop_area)
        
        # Browse button
        browse_btn = QPushButton("📁 Nebo vybrat video ze souboru...")
        browse_btn.setMinimumHeight(40)
        browse_btn.clicked.connect(self.browse_video)
        browse_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px;
                background-color: palette(button);
                border: 1px solid palette(mid);
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: palette(light);
            }
        """)
        main_layout.addWidget(browse_btn)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # === NOISE REDUCTION ===
        nr_group = self._create_group_box("Odstranění šumu a hlasu")
        nr_layout = QVBoxLayout()
        nr_layout.setSpacing(15)
        
        # Classic noise reduction
        self.nr_classic_radio = QRadioButton("Klasický noise reduction (rychlý)")
        self.nr_classic_radio.setChecked(True)
        self.nr_classic_radio.toggled.connect(self._on_nr_method_changed)
        nr_layout.addWidget(self.nr_classic_radio)
        
        # Classic slider
        self.classic_nr_widget = QWidget()
        classic_layout = QVBoxLayout(self.classic_nr_widget)
        classic_layout.setContentsMargins(30, 5, 0, 10)
        
        slider_row = QHBoxLayout()
        slider_row.addWidget(QLabel("Úroveň:"))
        self.nr_value_label = QLabel("50%")
        self.nr_value_label.setStyleSheet("font-weight: bold; color: #0d7ac7;")
        slider_row.addWidget(self.nr_value_label)
        slider_row.addStretch()
        classic_layout.addLayout(slider_row)
        
        self.noise_slider = QSlider(Qt.Horizontal)
        self.noise_slider.setMinimum(0)
        self.noise_slider.setMaximum(100)
        self.noise_slider.setValue(50)
        self.noise_slider.setMinimumHeight(30)
        self.noise_slider.valueChanged.connect(lambda v: self.nr_value_label.setText(f"{v}%"))
        classic_layout.addWidget(self.noise_slider)
        
        nr_layout.addWidget(self.classic_nr_widget)
        
        # AI separation
        self.nr_ai_radio = QRadioButton("AI separace - Demucs (pomalejší, ale mnohem lepší)")
        self.nr_ai_radio.toggled.connect(self._on_nr_method_changed)
        nr_layout.addWidget(self.nr_ai_radio)
        
        # AI model selection
        self.ai_nr_widget = QWidget()
        ai_layout = QVBoxLayout(self.ai_nr_widget)
        ai_layout.setContentsMargins(30, 5, 0, 10)
        
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("AI Model:"))
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.addItem("htdemucs (doporučený)", "htdemucs")
        self.ai_model_combo.addItem("htdemucs_ft (rychlejší)", "htdemucs_ft")
        self.ai_model_combo.addItem("mdx_extra (nejlepší kvalita)", "mdx_extra")
        self.ai_model_combo.setMinimumHeight(35)
        model_row.addWidget(self.ai_model_combo, 1)
        ai_layout.addLayout(model_row)
        
        ai_info = QLabel("ℹ️ Odstraní lidský hlas, hudbu a izoluje čisté motorové zvuky\n⚠️ První použití stáhne AI model (~250 MB)")
        ai_info.setStyleSheet("""
            QLabel {
                color: #555;
                font-size: 11px;
                padding: 10px;
                background-color: #e8f4f8;
                border-radius: 5px;
                border-left: 3px solid #0d7ac7;
            }
        """)
        ai_info.setWordWrap(True)
        ai_layout.addWidget(ai_info)
        
        self.ai_nr_widget.setVisible(False)
        nr_layout.addWidget(self.ai_nr_widget)
        
        nr_group.setLayout(nr_layout)
        main_layout.addWidget(nr_group)
        
        # === FREQUENCY FILTER ===
        freq_group = self._create_group_box("Frekvenční filtr (motorové frekvence)")
        freq_layout = QVBoxLayout()
        freq_layout.setSpacing(12)
        
        freq_low_row = QHBoxLayout()
        freq_low_row.addWidget(QLabel("Dolní frekvence:"))
        self.freq_low_spin = QSpinBox()
        self.freq_low_spin.setRange(20, 500)
        self.freq_low_spin.setValue(80)
        self.freq_low_spin.setSuffix(" Hz")
        self.freq_low_spin.setMinimumHeight(35)
        self.freq_low_spin.setMinimumWidth(120)
        freq_low_row.addWidget(self.freq_low_spin)
        freq_low_row.addStretch()
        freq_layout.addLayout(freq_low_row)
        
        freq_high_row = QHBoxLayout()
        freq_high_row.addWidget(QLabel("Horní frekvence:"))
        self.freq_high_spin = QSpinBox()
        self.freq_high_spin.setRange(100, 2000)
        self.freq_high_spin.setValue(500)
        self.freq_high_spin.setSuffix(" Hz")
        self.freq_high_spin.setMinimumHeight(35)
        self.freq_high_spin.setMinimumWidth(120)
        freq_high_row.addWidget(self.freq_high_spin)
        freq_high_row.addStretch()
        freq_layout.addLayout(freq_high_row)
        
        freq_group.setLayout(freq_layout)
        main_layout.addWidget(freq_group)
        
        # === ENGINE CONFIG ===
        engine_group = self._create_group_box("Konfigurace motoru")
        engine_layout = QVBoxLayout()
        engine_layout.setSpacing(12)
        
        engine_row = QHBoxLayout()
        engine_row.addWidget(QLabel("Typ motoru:"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItem("FPT NEF 6 (6V, 6.7L) - SOR BN 9.5/10.5/12", "fpt_nef6_184")
        self.engine_combo.addItem("FPT NEF 6 (6V, 6.7L, 210kW) - SOR BN 12", "fpt_nef6_210")
        self.engine_combo.addItem("FPT NEF 4 (4V, 4.5L) - SOR BN 8.5", "fpt_nef4")
        self.engine_combo.addItem("FPT Cursor 8 (6V, 6.7L) - SOR NB 12", "fpt_cursor8")
        self.engine_combo.addItem("FPT Cursor 9 (6V, 8.7L) - SOR NB 18", "fpt_cursor9")
        self.engine_combo.addItem("IVECO Cursor 8 (6V, 7.8L) - Starší SOR", "iveco_cursor8")
        self.engine_combo.addItem("Mercedes OM906 (6V, 6.4L)", "mercedes_om906")
        self.engine_combo.addItem("Cummins ISBe (6V, 6.7L)", "cummins_isbe")
        self.engine_combo.addItem("Cummins ISL (6V, 8.9L)", "cummins_isl")
        self.engine_combo.addItem("Obecný 6V diesel", "generic_6cyl")
        self.engine_combo.addItem("Obecný 4V diesel", "generic_4cyl")
        self.engine_combo.setMinimumHeight(35)
        engine_row.addWidget(self.engine_combo, 1)
        engine_layout.addLayout(engine_row)
        
        engine_info = QLabel("ℹ️ Správná konfigurace motoru zlepší přesnost detekce RPM")
        engine_info.setStyleSheet("""
            QLabel {
                color: #555;
                font-size: 11px;
                padding: 10px;
                background-color: #fff8e1;
                border-radius: 5px;
                border-left: 3px solid #ffa726;
            }
        """)
        engine_info.setWordWrap(True)
        engine_layout.addWidget(engine_info)
        
        engine_group.setLayout(engine_layout)
        main_layout.addWidget(engine_group)
        
        # === EXPORT SETTINGS ===
        export_group = self._create_group_box("Export nastavení")
        export_layout = QVBoxLayout()
        export_layout.setSpacing(12)
        
        self.export_full_check = QCheckBox("Exportovat kompletní zvuk (engine_sound_full.wav)")
        self.export_full_check.setChecked(True)
        self.export_full_check.setStyleSheet("padding: 5px;")
        export_layout.addWidget(self.export_full_check)
        
        self.export_segments_check = QCheckBox("Rozdělit na segmenty podle RPM")
        self.export_segments_check.setChecked(True)
        self.export_segments_check.setStyleSheet("padding: 5px;")
        export_layout.addWidget(self.export_segments_check)
        
        segments_row = QHBoxLayout()
        segments_row.setContentsMargins(30, 5, 0, 5)
        segments_row.addWidget(QLabel("Počet segmentů:"))
        self.segments_spin = QSpinBox()
        self.segments_spin.setRange(2, 20)
        self.segments_spin.setValue(5)
        self.segments_spin.setMinimumHeight(35)
        self.segments_spin.setMinimumWidth(80)
        segments_row.addWidget(self.segments_spin)
        segments_row.addStretch()
        export_layout.addLayout(segments_row)
        
        export_group.setLayout(export_layout)
        main_layout.addWidget(export_group)
        
        # === OUTPUT FOLDER ===
        output_group = self._create_group_box("Výstupní složka")
        output_layout = QHBoxLayout()
        
        self.output_label = QLabel(self.output_dir)
        self.output_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 5px;
            }
        """)
        output_layout.addWidget(self.output_label, 1)
        
        output_btn = QPushButton("Změnit...")
        output_btn.setMinimumHeight(40)
        output_btn.setMinimumWidth(100)
        output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(output_btn)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # === PROGRESS ===
        main_layout.addSpacing(15)
        
        progress_label = QLabel("Průběh:")
        progress_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        main_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(35)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 13px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #0d7ac7, stop:1 #0a9ecc);
                border-radius: 6px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Připraven")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                font-size: 12px;
                color: palette(text);
                background-color: palette(alternate-base);
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # === PROCESS BUTTON ===
        main_layout.addSpacing(15)
        
        self.process_btn = QPushButton("🚀 Zpracovat video")
        self.process_btn.setMinimumHeight(65)
        self.process_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #0d7ac7, stop:1 #0a5f9e);
                color: white;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #0a5f9e, stop:1 #084c7d);
            }
            QPushButton:disabled {
                background-color: #999;
                color: #ddd;
            }
        """)
        self.process_btn.clicked.connect(self.process_video)
        self.process_btn.setEnabled(False)
        main_layout.addWidget(self.process_btn)
        
        main_layout.addStretch()
    
    def _create_group_box(self, title):
        """Helper pro vytvoření stylovaného GroupBoxu"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        return group
    
    def _on_nr_method_changed(self):
        """Handle noise reduction method změny"""
        self.classic_nr_widget.setVisible(self.nr_classic_radio.isChecked())
        self.ai_nr_widget.setVisible(self.nr_ai_radio.isChecked())
    
    def on_file_dropped(self, file_path):
        self.video_path = file_path
        self.process_btn.setEnabled(True)
        print(f"\n✓ Video načteno: {file_path}")
    
    def browse_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Vyberte video soubor",
            "",
            "Video soubory (*.mp4 *.avi *.mov *.mkv *.webm);;Všechny soubory (*.*)"
        )
        if file_path:
            self.video_path = file_path
            self.drop_area.setText(f"✓ Video načteno:\n\n{os.path.basename(file_path)}")
            self.process_btn.setEnabled(True)
            print(f"\n✓ Video načteno: {file_path}")
    
    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Vyberte výstupní složku",
            self.output_dir
        )
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(dir_path)
            print(f"\n✓ Výstupní složka změněna: {dir_path}")
    
    def process_video(self):
        if not self.video_path:
            return
        
        video_name = Path(self.video_path).stem
        output_subdir = os.path.join(self.output_dir, f"engine_sounds_{video_name}")
        os.makedirs(output_subdir, exist_ok=True)
        
        print(f"\n✓ Výstupní složka: {output_subdir}")
        
        settings = {
            'use_ai_separation': self.nr_ai_radio.isChecked(),
            'ai_model': self.ai_model_combo.currentData() if self.nr_ai_radio.isChecked() else None,
            'noise_reduction': self.noise_slider.value() if self.nr_classic_radio.isChecked() else 0,
            'freq_low': self.freq_low_spin.value(),
            'freq_high': self.freq_high_spin.value(),
            'export_full': self.export_full_check.isChecked(),
            'export_segments': self.export_segments_check.isChecked(),
            'num_segments': self.segments_spin.value(),
            'engine_type': self.engine_combo.currentData()
        }
        
        self.process_btn.setEnabled(False)
        self.drop_area.setEnabled(False)
        
        self.processor = AudioProcessor(self.video_path, output_subdir, settings)
        self.processor.progress.connect(self.progress_bar.setValue)
        self.processor.status.connect(self.status_label.setText)
        self.processor.finished.connect(self.on_processing_finished)
        self.processor.start()
    
    def on_processing_finished(self, success, message):
        self.status_label.setText(message)
        self.process_btn.setEnabled(True)
        self.drop_area.setEnabled(True)
        
        if success:
            self.progress_bar.setValue(100)
            print("\n🎉 Můžeš použít vygenerované WAV soubory v OMSI!")
        else:
            self.progress_bar.setValue(0)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    print("="*70)
    print("Engine Sound Extractor for OMSI v2.0")
    print("="*70)
    print("\nAplikace spuštěna!")
    print("Přetáhni video do okna a stiskni 'Zpracovat video'")
    print("\nVýstupy budou v konzoli i v GUI.")
    print("="*70 + "\n")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()