# Asistan
Kendinize ait py ile yazılmış bir asistandır kişiseleştirmek size kalmışuamarım işinize yarar
# GECE Asistan

GECE, Türkçe bir sesli asistan uygulamasıdır. Kullanıcıların sesli veya metin tabanlı komutlarla etkileşim kurmasını sağlar.

## Özellikler

- **Metin Modu**: Komutları yazarak verin.
- **Sesli Mod**: Mikrofonla konuşarak komut verin (speech_recognition ve pyaudio gerektirir).
- **GUI Modu**: Küçük bir pencere arayüzü ile etkileşim (tkinter gerektirir).
- **Komutlar**:
  - Saat söyleme
  - Web sitelerini açma (Google, YouTube)
  - Klasörleri açma (Masaüstü, İndirilenler, Belgeler)
  - Programları açma (Chrome, Discord, Spotify)
  - Bilgisayarı kapatma
  - Yardım alma
  - Selamlaşma
  - Bilinmeyen komutlar için chatbot yanıtı (Hugging Face API ile)

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

2. Opsiyonel kütüphaneler (sesli mod için):
   ```
   pip install speechrecognition pyaudio
   ```

3. Opsiyonel kütüphane (GUI modu için):
   ```
   pip install tkinter
   ```

## Kullanım

### Metin Modu
```
python gece_asistan.py
```

### Sesli Mod
```
python gece_sesli.py
```

### Tüm Modlar (CLI, Sesli, GUI)
```
python gece_hepsi.py
# Veya mod belirtin: python gece_hepsi.py cli / voice / ui
```

## API Yapılandırması

Chatbot özelliği için Hugging Face API'sini kullanır. `gece_hepsi.py` veya `gece_sesli.py` dosyalarında `HF_API_URL` ve `HF_API_TOKEN` değişkenlerini ayarlayın.

Örnek:
```python
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
HF_API_TOKEN = "your_huggingface_token_here"
```

Token'ı Hugging Face hesabınızdan alın.

## Gereksinimler

- Python 3.6+
- pyttsx3
- requests
- webbrowser (standart)
- datetime (standart)
- os (standart)
- sys (standart)

Opsiyonel:
- speech_recognition
- pyaudio
- tkinter

## Lisans

Bu proje açık kaynak kodludur. Dilediğiniz gibi kullanabilirsiniz.

## Katkıda Bulunma

Pull request'ler ve issue'lar memnuniyetle karşılanır!
