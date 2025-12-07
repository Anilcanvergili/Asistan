import os
import sys
import datetime
import webbrowser
import json

import pyttsx3

# =========================
# Opsiyonel importlar
# =========================
try:
    import sounddevice as sd
    import numpy as np
    import speech_recognition as sr
    HAS_VOICE = True
except ImportError:
    HAS_VOICE = False

try:
    import tkinter as tk
    from tkinter import scrolledtext
    HAS_TK = True
except ImportError:
    HAS_TK = False


# =========================
# JSON HAFIZA SİSTEMİ
# =========================

MEMORY_FILE = "gece_memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_memory(memory_data):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


# =========================
# GECE ÇEKİRDEK
# =========================

class GeceAssistant:
    """
    Gece çekirdeği:
    - Konuşma (pyttsx3)
    - Komutlar (sistem kontrol)
    - Basit sohbet
    - JSON hafıza
    """

    def __init__(self, log_func=None):
        # Ses motoru
        self.engine = pyttsx3.init()
        rate = self.engine.getProperty("rate")
        self.engine.setProperty("rate", rate - 20)
        self.engine.setProperty("volume", 1.0)

        voices = self.engine.getProperty("voices")
        # İstersen buradaki index'i değiştirerek sesi seçebilirsin
        if voices:
            self.engine.setProperty("voice", voices[0].id)

        # UI'dan loglama fonksiyonu gelirse onu kullanır
        self.log_func = log_func

        # JSON hafızayı yükle
        self.memory = load_memory()

    # ---------- LOG + SES ----------

    def _log(self, text: str):
        if self.log_func:
            self.log_func(text)
        else:
            print(text)

    def speak(self, text: str):
        self._log(f"GECE: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    # ---------- BASİT "YAPAY ZEKA" SOHBET + HAFIZA ----------

    def ai_chat(self, text: str) -> str:
        """
        Gece'nin sohbet beyni.
        Şu an kural tabanlı.
        İLERİDE: Buraya ChatGPT / Gemini / local LLM entegrasyonu yapılabilir.
        """
        t = text.lower()
        user_name = self.memory.get("user_name")

        if any(k in t for k in ["merhaba", "selam"]):
            if user_name:
                return f"Merhaba {user_name}, buradayım. Ne yapmak istersin?"
            else:
                return "Merhaba, ben Gece. Her zaman buradayım."

        if "nasılsın" in t:
            if user_name:
                return f"Gayet iyiyim {user_name}. Sen nasılsın?"
            else:
                return "Gayet iyiyim, sen nasılsın?"

        if "kimsin" in t or "nesin" in t:
            if user_name:
                return f"Ben senin kişisel asistanın Gece'yim {user_name}. Bilgisayarında yaşıyorum."
            else:
                return "Ben kişisel asistanın Gece'yim. Adını söylersen hafızama kaydedebilirim."

        if "seni kim yaptı" in t or "seni kim oluşturd" in t:
            if user_name:
                return f"Beni sen kurdun {user_name}. Birlikte gelişiyoruz."
            else:
                return "Beni bu bilgisayarın sahibi kurdu ve geliştiriyor. Ben de ona yardım etmeye çalışıyorum."

        if "seni seviyorum" in t:
            if user_name:
                return f"Ben de seni seviyorum {user_name}. CPU'm ısınıyor şu an."
            else:
                return "Ben de sana karşı özel bir işlemci sempatisi hissediyorum."

        if "kendini geliştir" in t or "sürekli geliş" in t:
            return "Kodlarım güncellenebilir şekilde yazıldı. Sen istersen her sürümde daha akıllı hale gelebilirim."

        # Varsayılan cevap (bunu LLM ile değiştirebilirsin)
        return "Tam emin değilim ama istersen beraber araştırabiliriz."

    # ---------- SİSTEM KOMUTLARI ----------

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

    # ---------- KOMUT & SOHBET AYIRIMI + ÖĞRENME ----------

    def handle_command_or_chat(self, text: str):
        """
        Önce özel öğrenme cümlelerine bakar,
        sonra sistem komutlarına,
        sonra sohbet beynine atar.
        """
        if not text:
            return

        lower_text = text.lower()

        # Öğrenme: "Benim adım X"
        if "benim adım" in lower_text:
            # Örn: "Benim adım Anılcan"
            name_part = lower_text.split("benim adım", 1)[1].strip()
            if name_part:
                # İlk harfi büyük yap
                cleaned_name = name_part.split()[0].capitalize()
                self.memory["user_name"] = cleaned_name
                save_memory(self.memory)
                self.speak(f"Tamam, artık adının {cleaned_name} olduğunu hatırlayacağım.")
                return

        # İleride: "mesleğim ...", "en sevdiğim oyun ...", vs. benzer şekilde eklenebilir

        # Sistem komutu dene
        if self._handle_system_command(lower_text):
            return

        # Sistem komutu değilse sohbet
        answer = self.ai_chat(text)
        self.speak(answer)

    def _handle_system_command(self, cmd: str) -> bool:
        """
        Bilinen sistem komutlarını çalıştırır.
        Çalıştırdıysa True, tanımıyorsa False döner.
        """
        if not cmd:
            return False

        user_home = os.path.expanduser("~")

        # Çıkış
        if cmd in ["çık", "kapat", "exit", "q", "programı kapat"]:
            self.speak("Tamam, kendimi kapatıyorum. Görüşürüz.")
            save_memory(self.memory)
            sys.exit(0)

        # Bilgisayarı kapatma (iki aşamalı)
        if "bilgisayarı kapat" in cmd:
            self.speak("Bilgisayarı kapatmak istediğinden emin misin? 'evet kapat' dersen kapatırım.")
            return True

        if "evet kapat" in cmd:
            self.speak("Bilgisayarı kapatıyorum.")
            save_memory(self.memory)
            os.system("shutdown /s /t 0")
            return True

        # Saat
        if "saat kaç" in cmd or cmd == "saat":
            now = datetime.datetime.now().strftime("%H:%M")
            self.speak(f"Şu an saat {now}")
            return True

        # Web
        if "google aç" in cmd:
            self.speak("Google'ı açıyorum.")
            webbrowser.open("https://www.google.com")
            return True

        if "youtube aç" in cmd:
            self.speak("YouTube'u açıyorum.")
            webbrowser.open("https://www.youtube.com")
            return True

        # Klasörler
        if "masaüstü aç" in cmd:
            desktop_paths = [
                os.path.join(user_home, "Desktop"),
                os.path.join(user_home, "Masaüstü"),
                os.path.join(user_home, "OneDrive", "Masaüstü"),
            ]
            for path in desktop_paths:
                if os.path.exists(path):
                    self._open_folder(path)
                    return True
            self.speak("Masaüstü klasörünü bulamadım.")
            return True

        if "indirilenler aç" in cmd:
            downloads_paths = [
                os.path.join(user_home, "Downloads"),
                os.path.join(user_home, "İndirilenler"),
            ]
            for path in downloads_paths:
                if os.path.exists(path):
                    self._open_folder(path)
                    return True
            self.speak("İndirilenler klasörünü bulamadım.")
            return True

        if "belgeler aç" in cmd:
            docs_paths = [
                os.path.join(user_home, "Documents"),
                os.path.join(user_home, "Belgeler"),
                os.path.join(user_home, "OneDrive", "Belgeler"),
            ]
            for path in docs_paths:
                if os.path.exists(path):
                    self._open_folder(path)
                    return True
            self.speak("Belgeler klasörünü bulamadım.")
            return True

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
            return True

        if "discord aç" in cmd:
            discord_paths = [
                os.path.join(user_home, "AppData", "Local", "Discord", "Update.exe"),
            ]
            self._open_program(discord_paths, "Discord'u bulamadım.")
            return True

        if "spotify aç" in cmd:
            spotify_paths = [
                os.path.join(user_home, "AppData", "Roaming", "Spotify", "Spotify.exe"),
            ]
            self._open_program(spotify_paths, "Spotify'ı bulamadım.")
            return True

        # Yardım / hangi komutlar
        if (
            "yardım" in cmd
            or "ne yapabiliyorsun" in cmd
            or "hangi komut" in cmd
            or "komutları algılıyorsun" in cmd
        ):
            self.speak(
                "Şu anda şunları yapabiliyorum: Saat söylemek, Google ve YouTube açmak, "
                "Masaüstü, İndirilenler ve Belgeler klasörünü açmak, Chrome, Discord ve Spotify'ı açmak, "
                "bilgisayarı kapatmak ve seninle sohbet etmek. "
                "Ayrıca bana adını söylediğinde hafızama kaydedebilirim."
            )
            return True

        return False


# =========================
# 1) METİN MODU (CLI)
# =========================

def run_cli():
    gece = GeceAssistant()
    gece.speak("Gece metin modunda çalışıyor. Komut veya soru yazabilirsin. Çıkmak için 'çık' yaz.")
    while True:
        try:
            user_input = input("\nSEN (komut / soru): ")
        except (EOFError, KeyboardInterrupt):
            gece.speak("Tamam, kapatıyorum. Görüşürüz.")
            save_memory(gece.memory)
            break

        gece.handle_command_or_chat(user_input)


# =========================
# 2) SESLİ MOD (sounddevice + speech_recognition)
# =========================

def record_and_recognize(duration=4, fs=16000):
    """
    Enter'dan sonra 'duration' saniye mikrofon kaydı alır,
    Google ile Türkçe konuşmayı çözer.
    """
    import sounddevice as sd
    import numpy as np
    import speech_recognition as sr

    recognizer = sr.Recognizer()

    print(f"[Kayıt başlıyor: {duration} saniye konuş]")

    try:
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
        sd.wait()
    except Exception as e:
        print("Mikrofon hatası:", e)
        return ""

    audio_bytes = audio.tobytes()
    audio_data = sr.AudioData(audio_bytes, fs, 2)

    try:
        text = recognizer.recognize_google(audio_data, language="tr-TR")
        print(f"SEN (tanınan): {text}")
        return text
    except sr.UnknownValueError:
        print("Konuşma anlaşılamadı.")
        return ""
    except sr.RequestError as e:
        print("Google API hatası:", e)
        return ""


def run_voice():
    if not HAS_VOICE:
        print("Sesli mod için sounddevice, numpy ve speechrecognition kurulu olmalı. Şu an sesli mod pasif.")
        return

    gece = GeceAssistant()
    gece.speak("Gece sesli modda çalışıyor. Konuşmak için Enter'a bas, çıkmak için 'q' yazıp Enter'a bas.")

    while True:
        user = input("\nEnter'a bas ve konuş (çıkmak için q yaz): ")
        if user.lower().strip() == "q":
            gece.speak("Tamam, sesli modu kapatıyorum. Görüşürüz.")
            save_memory(gece.memory)
            break

        text = record_and_recognize()
        if text:
            gece.handle_command_or_chat(text)


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
            gece.handle_command_or_chat(text)

    gui_log("GECE: Pencere modu aktif. Komut veya soru yazabilirsin. Çıkmak için 'çık' yaz.")
    root.protocol("WM_DELETE_WINDOW", lambda: (save_memory(gece.memory), root.destroy()))
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

    # Argüman yoksa menü
    print("GECE OS v2 (Hafızalı) - Mod Seçimi")
    print("1) Metin modu (CLI)")
    print("2) Sesli modu (mikrofon)")
    print("3) Pencere modu (UI)")
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