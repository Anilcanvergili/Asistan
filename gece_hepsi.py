import os
import sys
import datetime
import webbrowser
import pyttsx3
import requests
import json

# =========================
# Opsiyonel importlar
# =========================
try:
    import speech_recognition as sr  # Ses tanıma
    HAS_SR = True
except ImportError:
    HAS_SR = False

try:
    import pyaudio  # Sadece var mı yok mu kontrol
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False

HAS_VOICE = HAS_SR and HAS_PYAUDIO

try:
    import tkinter as tk
    from tkinter import scrolledtext
    HAS_TK = True
except ImportError:
    HAS_TK = False


# =========================
# FACE CHATBOT API (GEÇİCİ OLARAK DEVRE DIŞI)
# =========================

# HF_API_URL = ""
# HF_API_TOKEN = ""

# def hf_chatbot_query(message: str) -> str:
#     headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}
#     payload = {"inputs": {"text": message}}
#     try:
#         response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
#         if response.status_code == 200:
#             data = response.json()
#             if isinstance(data, dict) and "error" in data:
#                 return "Şu anda sohbet servisi kullanılamıyor."
#             if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
#                 return data[0]["generated_text"]
#             elif isinstance(data, dict) and "generated_text" in data:
#                 return data["generated_text"]
#             else:
#                 return "Sohbetten yanıt alınamadı."
#         else:
#             return "Sohbet servisine bağlanılamadı."
#     except Exception as e:
#         return f"Sohbet sırasında hata oluştu: {str(e)}"


# =========================
# GECE ÇEKİRDEK SINIFI
# =========================

class GeceAssistant:
    def __init__(self, log_func=None):
        self.engine = pyttsx3.init()
        rate = self.engine.getProperty("rate")
        self.engine.setProperty("rate", rate - 20)
        self.engine.setProperty("volume", 1.0)
        voices = self.engine.getProperty("voices")
        if voices:
            self.engine.setProperty("voice", voices[0].id)

        # log_func GUI’de çıktı kutusuna yazmak için kullanılıyor
        self.log_func = log_func

    def _log(self, text: str):
        """Console veya GUI'ye yaz."""
        if self.log_func:
            self.log_func(text)
        else:
            print(text)

    def speak(self, text: str):
        """Yaz + seslendir."""
        self._log(f"GECE: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    # ----------------- Yardımcılar -----------------

    def _open_folder(self, path):
        try:
            os.startfile(path)
            self.speak("Açıyorum.")
        except Exception as e:
            self._log(str(e))
            self.speak("Bu klasörü açarken bir hata oluştu.")

    def _open_program(self, possible_paths, fallback_msg=None):
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    os.startfile(p)
                    self.speak("Açıyorum.")
                    return
                except Exception as e:
                    self._log(str(e))
        if fallback_msg:
            self.speak(fallback_msg)
        else:
            self.speak("Bu programı bulamadım.")

    # ----------------- Komut İşleme -----------------

    def handle_command(self, command: str):
        cmd = (command or "").lower().strip()
        if cmd == "":
            return

        user_home = os.path.expanduser("~")

        # Çıkış
        if cmd in ["çık", "kapat", "exit", "q", "programı kapat"]:
            self.speak("Tamam, kendimi kapatıyorum. Görüşürüz.")
            sys.exit(0)

        # Saat
        if "saat kaç" in cmd or cmd == "saat":
            now = datetime.datetime.now().strftime("%H:%M")
            self.speak(f"Şu an saat {now}")
            return

        # Web
        if "google aç" in cmd:
            self.speak("Google'ı açıyorum.")
            webbrowser.open("https://www.google.com")
            return

        if "youtube aç" in cmd:
            self.speak("YouTube'u açıyorum.")
            webbrowser.open("https://www.youtube.com")
            return

        # Klasörler
        if "masaüstü aç" in cmd or "desktop aç" in cmd:
            desktop_paths = [
                os.path.join(user_home, "Desktop"),
                os.path.join(user_home, "Masaüstü"),
                os.path.join(user_home, "OneDrive", "Masaüstü"),
            ]
            for path in desktop_paths:
                if os.path.exists(path):
                    self._open_folder(path)
                    return
            self.speak("Masaüstü klasörünü bulamadım.")
            return

        if "indirilenler aç" in cmd or "downloads aç" in cmd:
            downloads_paths = [
                os.path.join(user_home, "Downloads"),
                os.path.join(user_home, "İndirilenler"),
            ]
            for path in downloads_paths:
                if os.path.exists(path):
                    self._open_folder(path)
                    return
            self.speak("İndirilenler klasörünü bulamadım.")
            return

        if "belgeler aç" in cmd or "documents aç" in cmd:
            docs_paths = [
                os.path.join(user_home, "Documents"),
                os.path.join(user_home, "Belgeler"),
                os.path.join(user_home, "OneDrive", "Belgeler"),
            ]
            for path in docs_paths:
                if os.path.exists(path):
                    self._open_folder(path)
                    return
            self.speak("Belgeler klasörünü bulamadım.")
            return

        # Programlar
        if "chrome aç" in cmd or "google chrome aç" in cmd:
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            self._open_program(
                chrome_paths,
                "Chrome'u bulamadım ama istersen Google'ı tarayıcıda açabilirim."
            )
            return

        if "discord aç" in cmd:
            discord_paths = [
                os.path.join(user_home, "AppData", "Local", "Discord", "Update.exe"),
            ]
            self._open_program(discord_paths, "Discord'u bulamadım.")
            return

        if "spotify aç" in cmd:
            spotify_paths = [
                os.path.join(user_home, "AppData", "Roaming", "Spotify", "Spotify.exe"),
            ]
            self._open_program(spotify_paths, "Spotify'ı bulamadım.")
            return

        # Bilgisayar kapatma
        if "bilgisayarı kapat" in cmd:
            self.speak("Bilgisayarı kapatmak istediğinden emin misin? 'evet kapat' yazarsan kapatırım.")
            return

        if "evet kapat" in cmd:
            self.speak("Bilgisayarı kapatıyorum.")
            os.system("shutdown /s /t 0")
            return

        # Yardım
        if "yardım" in cmd or "ne yapabiliyorsun" in cmd:
            self.speak(
                "Saat söyleyebilirim, Google ve YouTube açabilirim, bazı klasörleri ve programları açabilirim, "
                "ve bilgisayarı kapatabilirim."
            )
            return

        # Selamlaşma
        if any(x in cmd for x in ["merhaba", "selam", "nasılsın"]):
            self.speak("Merhaba, ben Gece. Komutlarını bekliyorum.")
            return

        # Bilinmeyen komut
        response = hf_chatbot_query(command)
        self.speak(response)


# =========================
# 1) METİN MODU (CLI)
# =========================

def run_cli():
    gece = GeceAssistant()
    gece.speak("Gece metin modunda çalışıyor. Komutlarını yazabilirsin. Çıkmak için 'çık' yaz.")
    while True:
        try:
            user_input = input("\nSEN (komut yaz): ")
        except (EOFError, KeyboardInterrupt):
            gece.speak("Tamam, kapatıyorum. Görüşürüz.")
            break
        gece.handle_command(user_input)


# =========================
# 2) SESLİ MOD (MİKROFON)
# =========================

WAKE_WORDS = ["gece", "asistan"]
LANG = "tr-TR"


def run_voice():
    if not HAS_VOICE:
        print("Sesli mod için 'speechrecognition' ve 'pyaudio' kurulu olmalı. Şu an sesli mod pasif.")
        return

    gece = GeceAssistant()
    gece.speak("Gece sesli modda hazır. Beni çağırmak için 'Gece' diyebilirsin.")

    recognizer = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as source:
                print("\n[Gece dinliyor...]")
                recognizer.adjust_for_ambient_noise(source, duration=0.7)
                audio = recognizer.listen(source)
        except Exception as e:
            print("Mikrofon hatası:", e)
            break

        try:
            text = recognizer.recognize_google(audio, language=LANG)
            print(f"SEN: {text}")
            text = text.lower()
        except sr.UnknownValueError:
            print("Anlayamadım, tekrar söyle.")
            continue
        except sr.RequestError as e:
            print(f"Google Speech API hatası: {e}")
            continue

        if any(w in text for w in WAKE_WORDS):
            gece.speak("Dinliyorum, söyle.")
            for w in WAKE_WORDS:
                text = text.replace(w, "")
            text = text.strip()
            if not text:
                # Wake word'den sonra cümle yoksa tekrar dinle
                try:
                    with sr.Microphone() as source:
                        print("[Komut için dinleniyor...]")
                        recognizer.adjust_for_ambient_noise(source, duration=0.7)
                        audio = recognizer.listen(source)
                    text = recognizer.recognize_google(audio, language=LANG).lower()
                    print(f"SEN: {text}")
                except Exception:
                    continue

            if text:
                gece.handle_command(text)
        else:
            print("Wake kelimesi duymadım. 'Gece' diyerek beni çağırabilirsin.")


# =========================
# 3) PENCERE MODU (TKINTER)
# =========================

def run_ui():
    if not HAS_TK:
        print("Tkinter bulunamadı, pencere modu şu an kullanılamıyor.")
        return

    root = tk.Tk()
    root.title("Gece Asistan")
    root.geometry("420x380")
    root.resizable(False, False)
    root.configure(bg="#050816")

    frame = tk.Frame(root, bg="#050816")
    frame.pack(fill="both", expand=True, padx=8, pady=8)

    output_box = scrolledtext.ScrolledText(
        frame,
        wrap=tk.WORD,
        state="disabled",
        height=15,
        bg="#0f172a",
        fg="#e5e7eb"
    )
    output_box.pack(fill="both", expand=True, padx=4, pady=4)

    input_frame = tk.Frame(frame, bg="#050816")
    input_frame.pack(fill="x", padx=4, pady=(4, 0))

    input_box = tk.Entry(input_frame, bg="#020617", fg="#e5e7eb")
    input_box.pack(side="left", fill="x", expand=True, padx=(0, 4), pady=2)

    send_button = tk.Button(input_frame, text="Gönder", command=lambda: on_send())
    send_button.pack(side="right", pady=2)

    def gui_log(text: str):
        output_box.config(state="normal")
        output_box.insert(tk.END, text + "\n")
        output_box.see(tk.END)
        output_box.config(state="disabled")

    gece = GeceAssistant(log_func=gui_log)

    def on_send():
        text = input_box.get()
        input_box.delete(0, tk.END)
        if text.strip():
            gui_log(f"SEN: {text}")
            gece.handle_command(text)

    gui_log("GECE: Pencere modu aktif. Alttaki kutuya komut yazabilirsin. Çıkmak için 'çık' yaz.")
    root.mainloop()


# =========================
# MAIN
# =========================

def main():
    # Argümanla mod seçimi: cli / voice / ui
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "cli":
            run_cli()
            return
        elif mode == "voice":
            run_voice()
            return
        elif mode == "ui":
            run_ui()
            return

    # Argüman yoksa basit menü
    print("GECE Asistan - Mod Seçimi")
    print("1) Metin modu (yazarak komut ver)")
    print("2) Sesli modu (mikrofonla konuş) ")
    print("3) Pencere modu (küçük UI)")
    choice = input("Seçimin (1/2/3): ").strip()

    if choice == "1":
        run_cli()
    elif choice == "2":
        run_voice()
    elif choice == "3":
        run_ui()
    else:
        print("Geçersiz seçim, metin moduyla başlatıyorum.")
        run_cli()


if __name__ == "__main__":
    main()
