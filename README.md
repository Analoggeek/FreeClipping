# ☁️ DigiRG Cloud - AI Video Clip Engine

**Paste any link. Get captioned, viral 9:16 vertical clips in about two minutes. Free, local, private, and open-source.**

DigiRG Cloud transforms long YouTube, Twitch, and Kick videos (or local MP4s) into high-impact vertical clips with AI-generated titles, hooks, and word-timed subtitles for Instagram Reels, YouTube Shorts, and TikTok. Everything runs entirely on your local machine: no accounts, no subscriptions, and zero video data uploaded to external servers.

[![Star on GitHub](https://img.shields.io/github/stars/DIGIRGCLOUD/DIGIRGCLIPPINGFREE?style=for-the-badge&logo=github&label=Star%20on%20GitHub)](https://github.com/DIGIRGCLOUD/DIGIRGCLIPPINGFREE)
[![Donate ₹10](https://img.shields.io/badge/Donate-₹10%20(PayU)-10b981?style=for-the-badge&logo=googlepay&logoColor=white)](https://u.payu.in/PAYUMN/yrw25eGEUES4)
[![Follow @ft_raj_check](https://img.shields.io/badge/Instagram-%40ft__raj__check-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/ft_raj_check/)
[![License: MIT](https://img.shields.io/badge/License-MIT-00f0ff?style=for-the-badge)](LICENSE)
[![Python 3.10--3.13](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

---

### 🌟 Developed by DigiRG Cloud
Created and maintained by **[DigiRG Cloud](https://www.instagram.com/ft_raj_check/)**.  
Follow on Instagram: **[@ft_raj_check](https://www.instagram.com/ft_raj_check/)** for updates, tools, and tutorials.  
If DigiRG Cloud saves you time, please give this repository a ⭐ **Star**!

---

### ❤️ Support This Free Tool (Donate At Least ₹10)
DigiRG Cloud is **100% free and open-source**. There are no paywalls, subscriptions, or watermarks.

Agar is tool ne aapka keemti waqt bachaya ho, ya video clipping aasan ki ho, to please **at least ₹10 (a cup of tea ☕)** donate karke is free tool ko zinda rakhne me support kare:

👉 **[⚡ Click Here to Donate ₹10 via PayU / UPI (GPay, PhonePe, Paytm, Cards)](https://u.payu.in/PAYUMN/yrw25eGEUES4)**  
*Aapka chhota sa support hamare liye bohot bada hausla aur taqat hai! 🙏*

---

## ⚡ How It Works

DigiRG Cloud uses an intelligent hybrid audio-visual heuristic pipeline to pinpoint peak moments in seconds:

1. **Audio First Analysis:** Downloads audio stream instantly (e.g. ~80 MB for an 85-minute stream in seconds).
2. **Instant Transcript:** Leverages word-timed YouTube captions or falls back to local Whisper speech recognition.
3. **Signal Spike Scoring:** Scans the audio track for sudden loudness shifts, raised voice frequency energy (2–4 kHz shouting/screaming), and high-impact dialogue cues.
4. **Sentence-Snapping & Hooks:** Snaps start and end timestamps precisely to natural sentence boundaries within your target Min/Max length.
5. **Precision Rendering:** Downloads only the selected video segments and renders high-definition vertical clips with burned-in animated subtitles and customized speaker framing.

---

## 🚀 Key Features

- **One-Click Generation:** Single click on **⚡ Make clips** downloads, detects highlights, frames, and renders complete clips.
- **11 Studio Layouts:** Facecam above/below gameplay, blurred background fill, full screen crop, gameplay focus, circular facecams, and corner overlays.
- **Dynamic Word-Timed Captions:** 5 popular social styles:
  - *GTA Neon* (Electric sky blue / cyan glow)
  - *Impact* (Active-word lime highlight)
  - *Hormozi* (Bold white + cyan pop with thick outline)
  - *MrBeast* (High-contrast yellow + orange)
  - *Clean* (Minimal, readable modern subtitles)
- **52 Languages & Hinglish:** Native support for English, Hindi, Hinglish (Hindi written in English letters), Spanish, German, French, and 46+ other languages.
- **Live Stream Clipping:** Automatically detects chat spikes on active Twitch and YouTube live streams to cut clips in real-time.
- **Creator Radar:** Add streamer handles; DigiRG Cloud monitors their channels and automatically records and clips viral moments when they go live.
- **Phone Remote Companion:** Connect your phone over local Wi-Fi to monitor live clips, trigger instant trims, and preview videos directly from your mobile browser.
- **100% Private & Local:** The server binds strictly to `127.0.0.1`. No telemetry, no API fees, no subscriptions.

---

## 💻 Quick Start & Installation

### Requirements
- **Python:** 3.10, 3.11, 3.12, or 3.13
- **FFmpeg:** Installed and available on your system `PATH`
- **Optional:** [Ollama](https://ollama.com) (`ollama pull llama3.2:3b`) for local AI title and hook generation.

---

### macOS & Linux

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DIGIRGCLOUD/DIGIRGCLIPPINGFREE.git
   cd DIGIRGCLIPPINGFREE
   ```

2. **Launch DigiRG Cloud:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   *The launcher automatically initializes a Python virtual environment (`.venv`), installs all dependencies, and opens `http://127.0.0.1:8770` in your default browser.*

---

### Windows

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/DIGIRGCLOUD/DIGIRGCLIPPINGFREE.git
   cd DIGIRGCLIPPINGFREE
   ```

2. **Launch DigiRG Cloud:**
   ```powershell
   .\run.ps1
   ```

---

## 📱 Mobile Access (Phone Remote)

To control clipping from your mobile phone on the same Wi-Fi network:
```bash
NEONCLIPPING_LAN=1 ./run.sh
```
Open the displayed local IP address (e.g. `http://192.168.1.XX:8770/m`) on your phone and enter the secure 6-digit PIN shown on your PC screen.

---

## 🤝 Community & Support

- **Instagram:** [@ft_raj_check](https://www.instagram.com/ft_raj_check/)
- **Bug Reports & Feature Requests:** Open an issue on GitHub!

---

## 🔍 Topics & Search Keywords
`digirg-cloud` · `digirgclippingfree` · `ai-video-clipper` · `opus-clip-alternative` · `shorts-generator` · `reels-maker` · `tiktok-generator` · `auto-subtitles` · `hinglish-captions` · `twitch-clipper` · `open-source` · `faster-whisper` · `yt-dlp` · `fastapi` · `opencv` · `local-ai` · `video-highlight-generator`

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
