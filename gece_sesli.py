import sounddevice as sd
import numpy as np
import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import sys
import os
import requests
import json

# =========================
# HUGGING FACE CHATBOT API
# =========================

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
HF_API_TOKEN = "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"

def hf_chatbot_query(message: str) -> str:
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}
    payload = {"inputs": {"text": message}}
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "error" in data:
                return "Şu anda sohbet servisi kullanılamıyor."
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                return data[0]["generated_text"]
            elif isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"]
            else:
                return "Sohbetten yanıt alınamadı."
        else:
            return "Sohbet servisine bağlanılamadı."
    except Exception as e:
        return f"Sohbet sırasında hata oluştu: {str(e)}"

# =========================
# GECE SES MOTORU
# =========================

engine = pyttsx3.init()
rate = engine.getProperty("rate")
engine.setProperty("rate", rate - 40)  # Daha yavaş (daha doğal)
engine.setProperty("volume", 0.9)  # Hafif kısık, daha yumuşak ses

voices = engine.getProperty("voices")
# Sesler arasında erkek ve kadın sesleri denenecek
voice_found = False
for voice in voices:
    # Kadın sesi tercih et, yoksa ilk bulunanı kullan
    if "female" in voice.name.lower() or "zira" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        voice_found = True
        break
if not voice_found and voices:
    engine.setProperty("voice", voices[0].id)


def speak(text: str):
    print(f"GECE: {text}")
    engine.say(text)
    engine.runAndWait()


# =========================
# GECE KOMUTLARI
# =========================

def handle_command(command: str):
    cmd = (command or "").lower().strip()
    if cmd == "":
        return

    user_home = os.path.expanduser("~")

    # Çıkış
    if cmd in ["çık", "kapat", "exit", "q", "programı kapat"]:
        speak("Tamam, kendimi kapatıyorum. Görüşürüz.")
        sys.exit(0)

    # Saat
    if "saat kaç" in cmd or cmd == "saat":
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"Şu an saat {now}")
        return

    # Web
    if "google aç" in cmd:
        speak("Google'ı açıyorum.")
        webbrowser.open("https://www.google.com")
        return

    if "youtube aç" in cmd:
        speak("YouTube'u açıyorum.")
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
                try:
                    os.startfile(path)
                    speak("Masaüstünü açıyorum.")
                    return
                except Exception:
                    pass
        speak("Masaüstü klasörünü bulamadım.")
        return

    if "indirilenler aç" in cmd or "downloads aç" in cmd:
        downloads_paths = [
            os.path.join(user_home, "Downloads"),
            os.path.join(user_home, "İndirilenler"),
        ]
        for path in downloads_paths:
            if os.path.exists(path):
                try:
                    os.startfile(path)
                    speak("İndirilenler klasörünü açıyorum.")
                    return
                except Exception:
                    pass
        speak("İndirilenler klasörünü bulamadım.")
        return

    # Programlar
    if "chrome aç" in cmd or "google chrome aç" in cmd:
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for p in chrome_paths:
            if os.path.exists(p):
                os.startfile(p)
                speak("Chrome'u açıyorum.")
                return
        speak("Chrome'u bulamadım.")
        return

    # Bilgisayar kapatma
    if "bilgisayarı kapat" in cmd:
        speak("Bilgisayarı kapatmak istediğinden emin misin? 'evet kapat' dersen kapatırım.")
        return

    if "evet kapat" in cmd:
        speak("Bilgisayarı kapatıyorum.")
        os.system("shutdown /s /t 0")
        return

    # Yardım
    if "yardım" in cmd or "ne yapabiliyorsun" in cmd:
        speak("Saat söyleyebilirim, Google ve YouTube açabilirim, bazı klasörleri ve programları açabilirim, bilgisayarı kapatabilirim.")
        return

    # Selamlaşma
    if any(x in cmd for x in ["merhaba", "selam", "nasılsın"]):
        speak("Merhaba, ben Gece. Komutlarını bekliyorum.")
        return

    # Bilinmeyen komut
    response = hf_chatbot_query(command)
    speak(response)


# =========================
# SES KAYDI (sounddevice)
# =========================

recognizer = sr.Recognizer()


def record_and_recognize(duration=10, fs=16000):
    """
    Enter'a bastıktan sonra 'duration' saniye mikrofon kaydı alır,
    Google ile Türkçe konuşmayı çözer, string olarak döndürür.
    """
    speak(f"{duration} saniye boyunca konuşabilirsin.")
    print("[Kayıt başlıyor...]")

    try:
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
        sd.wait()
    except Exception as e:
        print("Mikrofon hatası:", e)
        speak("Mikrofonu kullanırken bir hata oluştu.")
        return ""

    audio_bytes = audio.tobytes()
    audio_data = sr.AudioData(audio_bytes, fs, 2)  # 16-bit -> sample_width=2

    try:
        text = recognizer.recognize_google(audio_data, language="tr-TR")
        print(f"SEN (tanınan): {text}")
        return text
    except sr.UnknownValueError:
        print("Konuşma anlaşılamadı.")
        speak("Ne dediğini anlayamadım.")
        return ""
    except sr.RequestError as e:
        print("Google API hatası:", e)
        speak("Şu an konuşmayı çözemiyorum, internet bağlantısını kontrol et.")
        return ""


# =========================
# ANA DÖNGÜ
# =========================

def main():
    speak("Gece sesli modda çalışıyor. Konuşmak için Enter'a bas, çıkmak için 'q' yazıp Enter'a bas.")
    while True:
        user = input("\nEnter'a bas ve konuş (çıkmak için q yaz): ")
        if user.lower().strip() == "q":
            speak("Tamam, sesli modu kapatıyorum. Görüşürüz.")
            break

        text = record_and_recognize()
        if text:
            handle_command(text)


if __name__ == "__main__":
    main()
