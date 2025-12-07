import pyttsx3
import webbrowser
import datetime
import sys
import os
import subprocess

engine = pyttsx3.init()

rate = engine.getProperty("rate")
engine.setProperty("rate", rate - 20)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)


def speak(text: str):
    print(f"GECE: {text}")
    engine.say(text)
    engine.runAndWait()


def open_folder(path):
    try:
        os.startfile(path)
        speak("Açıyorum.")
    except Exception as e:
        print(e)
        speak("Bu klasörü açarken bir hata oluştu.")


def open_program(possible_paths, fallback_msg=None):
    for p in possible_paths:
        if os.path.exists(p):
            try:
                os.startfile(p)
                speak("Açıyorum.")
                return
            except Exception as e:
                print(e)
    if fallback_msg:
        speak(fallback_msg)
    else:
        speak("Bu programı bulamadım.")


def handle_command(command: str):
    cmd = command.lower().strip()

    if cmd == "":
        return

    # Çıkış
    if cmd in ["çık", "kapat", "exit", "q", "programı kapat"]:
        speak("Tamam, kendimi kapatıyorum. Görüşürüz.")
        sys.exit(0)

    # Saat
    if "saat kaç" in cmd or cmd == "saat":
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"Şu an saat {now}")
        return

    # Google / YouTube
    if "google aç" in cmd:
        speak("Google'ı açıyorum.")
        webbrowser.open("https://www.google.com")
        return

    if "youtube aç" in cmd:
        speak("YouTube'u açıyorum.")
        webbrowser.open("https://www.youtube.com")
        return

    # Masaüstü, İndirilenler, Belgeler klasörlerini aç
    user_home = os.path.expanduser("~")

    if "masaüstü aç" in cmd or "desktop aç" in cmd:
        desktop_paths = [
            os.path.join(user_home, "Desktop"),
            os.path.join(user_home, "Masaüstü"),
            os.path.join(user_home, "OneDrive", "Masaüstü"),
        ]
        for path in desktop_paths:
            if os.path.exists(path):
                open_folder(path)
                return
        speak("Masaüstü klasörünü bulamadım.")
        return

    if "indirilenler aç" in cmd or "downloads aç" in cmd:
        downloads_paths = [
            os.path.join(user_home, "Downloads"),
            os.path.join(user_home, "İndirilenler"),
        ]
        for path in downloads_paths:
            if os.path.exists(path):
                open_folder(path)
                return
        speak("İndirilenler klasörünü bulamadım.")
        return

    if "belgeler aç" in cmd or "documents aç" in cmd:
        docs_paths = [
            os.path.join(user_home, "Documents"),
            os.path.join(user_home, "Belgeler"),
            os.path.join(user_home, "OneDrive", "Belgeler"),
        ]
        for path in docs_paths:
            if os.path.exists(path):
                open_folder(path)
                return
        speak("Belgeler klasörünü bulamadım.")
        return

    # Bazı programları açma (Chrome, Discord, Spotify)
    if "chrome aç" in cmd or "google chrome aç" in cmd:
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        open_program(chrome_paths, "Chrome'u bulamadım ama istersen Google'ı tarayıcıda açabilirim.")
        return

    if "discord aç" in cmd:
        discord_paths = [
            os.path.join(user_home, "AppData", "Local", "Discord", "Update.exe"),
        ]
        open_program(discord_paths, "Discord'u bulamadım.")
        return

    if "spotify aç" in cmd:
        spotify_paths = [
            r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe".replace("%USERNAME%", os.path.basename(user_home)),
            r"C:\Program Files\WindowsApps",
        ]
        open_program(spotify_paths, "Spotify'ı bulamadım.")
        return

    # Basit bilgisayar komutları (dikkatli kullan)
    if "bilgisayarı kapat" in cmd:
        speak("Bilgisayarı kapatmak istediğinden emin misin? Komutu tekrar 'evet kapat' diye yazarsan kapatırım.")
        return

    if "evet kapat" in cmd:
        speak("Bilgisayarı kapatıyorum.")
        os.system("shutdown /s /t 0")
        return

    # Yardım
    if "yardım" in cmd or "ne yapabiliyorsun" in cmd or "hangi komut" in cmd or "komutları algılıyorsun" in cmd:
        speak(
            "Şu komutları algılayabiliyorum: "
            "Selamlaşma; mesela merhaba, selam, nasılsın. "
            "Saat kaç veya saat. "
            "Google aç, YouTube aç. "
            "Masaüstü aç, indirilenler aç. "
            "Chrome aç. "
            "Bilgisayarı kapat ve evet kapat. "
            "Beni kapatmak için ise çık, kapat, programı kapat, exit veya q diyebilirsin."
        )
        return

    # Bilinmeyen komut
    speak("Bu komutu tanımıyorum, daha net söyleyebilir misin?")


def main():
    speak("Gece çalışıyor. Komutlarını yazabilirsin. Çıkmak için 'çık' yaz.")
    while True:
        try:
            user_input = input("\nSEN (komut yaz): ")
        except (EOFError, KeyboardInterrupt):
            speak("Tamam, kapatıyorum. Görüşürüz.")
            break

        handle_command(user_input)


if __name__ == "__main__":
    main()
