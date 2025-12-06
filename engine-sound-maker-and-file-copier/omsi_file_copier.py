import sys
import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QTextEdit, 
                             QLabel, QFileDialog, QProgressBar, QMessageBox)
from PySide6.QtCore import QThread, Signal


class FileCopierThread(QThread):
    """Thread pro kopírování souborů na pozadí"""
    progress = Signal(int, int)  # current, total
    log = Signal(str)
    finished = Signal(bool, str)  # success, message
    
    def __init__(self, omsi_path, target_path, file_list):
        super().__init__()
        self.omsi_path = Path(omsi_path)
        self.target_path = Path(target_path)
        self.file_list = file_list
        self.should_stop = False
        
    def stop(self):
        self.should_stop = True
        
    def run(self):
        try:
            copied_folders = set()  # Sleduj zkopírované složky
            not_found_folders = set()
            total_files = len(self.file_list)
            
            # Vytvoř cílovou složku pokud neexistuje
            self.target_path.mkdir(parents=True, exist_ok=True)
            
            # Extrahuj root složky z cest
            self.log.emit("=== Analyzuji root složky modelů ===\n")
            root_folders = set()
            
            for relative_path in self.file_list:
                # Rozdělí cestu na části
                parts = Path(relative_path).parts
                
                # Pro Sceneryobjects\251_VelkeOpatovice-Kninice\Hasici_VO.sco
                # chceme: Sceneryobjects\251_VelkeOpatovice-Kninice
                if len(parts) >= 2:
                    root_folder = Path(parts[0]) / parts[1]
                    root_folders.add(str(root_folder))
            
            root_folders = sorted(root_folders)
            self.log.emit(f"Nalezeno {len(root_folders)} unikátních root složek\n")
            
            # Kopíruj každou root složku
            for idx, root_folder in enumerate(root_folders):
                if self.should_stop:
                    self.finished.emit(False, "Kopírování zrušeno uživatelem")
                    return
                
                source_folder = self.omsi_path / root_folder
                target_folder = self.target_path / root_folder
                
                if source_folder.exists() and source_folder.is_dir():
                    try:
                        self.log.emit(f"📁 Kopíruji složku: {root_folder}")
                        
                        # Zkopíruj celou složku včetně všech podsložek
                        shutil.copytree(source_folder, target_folder, dirs_exist_ok=True)
                        
                        # Spočítej kolik souborů bylo zkopírováno
                        file_count = sum(1 for _ in target_folder.rglob('*') if _.is_file())
                        
                        copied_folders.add(root_folder)
                        self.log.emit(f"  ✓ Zkopírováno {file_count} souborů z {root_folder}\n")
                        
                    except Exception as e:
                        self.log.emit(f"  ✗ Chyba při kopírování {root_folder}: {str(e)}\n")
                else:
                    not_found_folders.add(root_folder)
                    self.log.emit(f"  ⚠ Složka nenalezena: {root_folder}\n")
                
                # Aktualizuj progress
                self.progress.emit(idx + 1, len(root_folders))
            
            # Spočítej celkový počet zkopírovaných souborů
            total_copied_files = 0
            for folder in copied_folders:
                folder_path = self.target_path / folder
                total_copied_files += sum(1 for _ in folder_path.rglob('*') if _.is_file())
            
            # Výsledná zpráva
            message = f"Hotovo!\n\n"
            message += f"Zkopírováno složek: {len(copied_folders)}\n"
            message += f"Celkem souborů: {total_copied_files}\n"
            message += f"Nenalezeno složek: {len(not_found_folders)}"
            
            self.finished.emit(True, message)
            
        except Exception as e:
            self.finished.emit(False, f"Kritická chyba: {str(e)}")


class OmsiFileCopier(QMainWindow):
    def __init__(self):
        super().__init__()
        self.copier_thread = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('OMSI Kopírovač Souborů')
        self.setGeometry(100, 100, 900, 700)
        
        # Hlavní widget a layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # OMSI cesta
        omsi_layout = QHBoxLayout()
        omsi_layout.addWidget(QLabel('OMSI složka:'))
        self.omsi_path_edit = QLineEdit()
        self.omsi_path_edit.setPlaceholderText('C:/Program Files (x86)/Steam/steamapps/common/OMSI 2')
        omsi_layout.addWidget(self.omsi_path_edit)
        omsi_browse_btn = QPushButton('Procházet...')
        omsi_browse_btn.clicked.connect(self.browse_omsi_path)
        omsi_layout.addWidget(omsi_browse_btn)
        main_layout.addLayout(omsi_layout)
        
        # Cílová cesta
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel('Cílová složka:'))
        self.target_path_edit = QLineEdit()
        self.target_path_edit.setPlaceholderText('C:/OMSI_Export')
        target_layout.addWidget(self.target_path_edit)
        target_browse_btn = QPushButton('Procházet...')
        target_browse_btn.clicked.connect(self.browse_target_path)
        target_layout.addWidget(target_browse_btn)
        main_layout.addLayout(target_layout)
        
        # Seznam souborů
        main_layout.addWidget(QLabel('Seznam souborů (relativní cesty):'))
        self.file_list_edit = QTextEdit()
        self.file_list_edit.setPlaceholderText(
            'Vlož seznam souborů, každý na nový řádek:\n'
            'Sceneryobjects\\149_Warszawa\\Bloki\\Blok_Kocjana_1\\BL1.sco\n'
            'Sceneryobjects\\149_Warszawa\\Bloki\\Blok_Kocjana_2\\BL2.sco\n'
            '...'
        )
        main_layout.addWidget(self.file_list_edit)
        
        # Tlačítka akce
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton('Načíst ze souboru')
        self.load_btn.clicked.connect(self.load_file_list)
        button_layout.addWidget(self.load_btn)
        
        self.copy_btn = QPushButton('Začít kopírování')
        self.copy_btn.clicked.connect(self.start_copying)
        button_layout.addWidget(self.copy_btn)
        
        self.stop_btn = QPushButton('Zastavit')
        self.stop_btn.clicked.connect(self.stop_copying)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton('Vymazat log')
        self.clear_btn.clicked.connect(lambda: self.log_edit.clear())
        button_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Log
        main_layout.addWidget(QLabel('Log:'))
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        main_layout.addWidget(self.log_edit)
        
    def browse_omsi_path(self):
        path = QFileDialog.getExistingDirectory(self, 'Vyber OMSI složku')
        if path:
            self.omsi_path_edit.setText(path)
            
    def browse_target_path(self):
        path = QFileDialog.getExistingDirectory(self, 'Vyber cílovou složku')
        if path:
            self.target_path_edit.setText(path)
            
    def load_file_list(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            'Načíst seznam souborů', 
            '', 
            'Text soubory (*.txt);;Všechny soubory (*.*)'
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.file_list_edit.setPlainText(content)
                self.log_edit.append(f"✓ Načteno ze souboru: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, 'Chyba', f'Nelze načíst soubor: {str(e)}')
                
    def start_copying(self):
        # Validace
        omsi_path = self.omsi_path_edit.text().strip()
        target_path = self.target_path_edit.text().strip()
        file_list_text = self.file_list_edit.toPlainText().strip()
        
        if not omsi_path:
            QMessageBox.warning(self, 'Chyba', 'Zadej OMSI složku!')
            return
        
        if not target_path:
            QMessageBox.warning(self, 'Chyba', 'Zadej cílovou složku!')
            return
            
        if not file_list_text:
            QMessageBox.warning(self, 'Chyba', 'Zadej seznam souborů!')
            return
        
        if not Path(omsi_path).exists():
            QMessageBox.warning(self, 'Chyba', 'OMSI složka neexistuje!')
            return
        
        # Zpracuj seznam souborů
        file_list = [line.strip() for line in file_list_text.split('\n') if line.strip()]
        
        if not file_list:
            QMessageBox.warning(self, 'Chyba', 'Seznam souborů je prázdný!')
            return
        
        # Připrav UI
        self.copy_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_edit.clear()
        self.progress_bar.setValue(0)
        
        self.log_edit.append(f"=== Začínám kopírování CELÝCH SLOŽEK ===")
        self.log_edit.append(f"OMSI: {omsi_path}")
        self.log_edit.append(f"Cíl: {target_path}")
        self.log_edit.append(f"Souborů v seznamu: {len(file_list)}")
        self.log_edit.append(f"\nBudou zkopírovány CELÉ root složky včetně všech podsložek!\n")
        
        # Spusť thread
        self.copier_thread = FileCopierThread(omsi_path, target_path, file_list)
        self.copier_thread.progress.connect(self.update_progress)
        self.copier_thread.log.connect(self.add_log)
        self.copier_thread.finished.connect(self.copying_finished)
        self.copier_thread.start()
        
    def stop_copying(self):
        if self.copier_thread and self.copier_thread.isRunning():
            self.copier_thread.stop()
            self.log_edit.append("\n⚠ Zastavování...")
            
    def update_progress(self, current, total):
        percentage = int((current / total) * 100)
        self.progress_bar.setValue(percentage)
        
    def add_log(self, message):
        self.log_edit.append(message)
        # Auto-scroll
        self.log_edit.verticalScrollBar().setValue(
            self.log_edit.verticalScrollBar().maximum()
        )
        
    def copying_finished(self, success, message):
        self.copy_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        self.log_edit.append(f"\n{'='*50}")
        self.log_edit.append(message)
        
        if success:
            QMessageBox.information(self, 'Hotovo', message)
        else:
            QMessageBox.warning(self, 'Chyba', message)


def main():
    app = QApplication(sys.argv)
    window = OmsiFileCopier()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()