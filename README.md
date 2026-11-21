# ⚡ FreeClipping — Free AI Video Clip Engine

**Paste any link. Get captioned, viral 9:16 vertical clips in about two minutes. Free, local, private, and open-source.**

FreeClipping turns long YouTube, Twitch, and Kick videos (or local MP4s) into high-impact vertical clips with AI-generated titles, hooks, and word-timed subtitles for Instagram Reels, YouTube Shorts, and TikTok. Everything runs entirely on your local machine: no accounts, no subscriptions, and zero video data uploaded to external servers.

[![License: MIT](https://img.shields.io/badge/License-MIT-00f0ff?style=for-the-badge)](LICENSE)
[![Python 3.10--3.13](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Star on GitHub](https://img.shields.io/github/stars/Analoggeek/FreeClipping?style=for-the-badge&logo=github&label=Star%20on%20GitHub)](https://github.com/Analoggeek/FreeClipping)

---

### ⚡ What it is
FreeClipping is a **free, open-source, local-first** AI video clipping tool built by [Analoggeek](https://github.com/Analoggeek).

---

## ⚡ How It Works

FreeClipping uses an intelligent hybrid audio-visual heuristic pipeline to pinpoint peak moments in seconds:

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
- **Creator Radar:** Add streamer handles; FreeClipping monitors their channels and automatically records and clips viral moments when they go live.
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
   git clone https://github.com/Analoggeek/FreeClipping.git
   cd FreeClipping
   ```

2. **Launch FreeClipping:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   *The launcher automatically initializes a Python virtual environment (`.venv`), installs all dependencies, and opens `http://127.0.0.1:8770` in your default browser.*

---

### Self-contained .app bundles (macOS — double-click, no installer)

For macOS, the app ships as a **self-contained `.app` bundle** — it embeds the app source and the whole Python-3.12 wheelhouse. The very first launch sets up the local environment inside the bundle itself. No installer, no shell script.

* **macOS (Apple Silicon):** `FreeClipping-macOS-arm64.app.zip` — unzip, then double-click `FreeClipping.app`.
* **macOS (Intel):** `FreeClipping-macOS-x64.app.zip` — unzip, then double-click `FreeClipping.app`.

> Requires Python 3.12 on the target machine. On first launch the bundle bootstraps a local venv in itself; afterwards it launches instantly. See `tools/offline/make_app_bundle.py`.

### Offline installers (macOS Intel + Apple Silicon + Windows, no internet needed)

Self-contained zips — the app **and every dependency are baked in**. No downloads required.

* **macOS (Apple Silicon):** `FreeClipping-Offline-macOS-arm64.zip` (~217 MB) — unzip, then run the `.sh`. Installs to `~/FreeClipping` and creates `~/Applications/FreeClipping.app` (with the 3D bolt icon).
* **macOS (Intel):** `FreeClipping-Offline-macOS-x64.zip` (~233 MB) — same as above for Intel Macs.
* **Windows (64-bit):** `FreeClipping-Offline-Windows-x64.zip` — unzip, double-click the `.bat`. Installs to `%LOCALAPPDATA%\FreeClipping` and creates a desktop shortcut with the 3D icon.

> Requires **Python 3.12** already installed (`python3.12` / [python.org](https://www.python.org/downloads/)). The offline installer installs nothing system-wide — it only builds the app's virtual environment with the embedded wheelhouse.

Download the installers from [GitHub Releases](https://github.com/Analoggeek/FreeClipping/releases) or build them yourself:

```bash
python3 tools/offline/make_offline_installer.py        # builds dist/*.zip + the raw .sh/.bat/.ps1
```

---

### Windows

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/Analoggeek/FreeClipping.git
   cd FreeClipping
   ```

2. **Launch FreeClipping:**
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

- **Issues & Feature Requests:** Open an issue on [GitHub](https://github.com/Analoggeek/FreeClipping/issues)!
- **Report bugs:** Use the **Report a problem** option inside the app — it pre-fills the boxes and removes links, user names, e-mails and IPs.

---

## 🔍 Topics & Search Keywords
`freeclipping` · `free-video-clipper` · `ai-video-clipper` · `free-ai-video-clipper` · `video-highlight-generator` · `reels-maker` · `shorts-generator` · `tiktok-generator` · `youtube-shorts-maker` · `instagram-reels-maker` · `auto-subtitles` · `hinglish-captions` · `twitch-clipper` · `vertical-clips` · `local-ai` · `fastapi` · `faster-whisper` · `yt-dlp` · `open-source` · `free-open-source`

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

---

Made with ❤️ by [Analoggeek](https://github.com/Analoggeek)
