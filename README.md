# 🎵 Python YouTube Music Player

A modern desktop music player built with Python that lets you search, stream, and download audio from YouTube — all inside a clean GUI.

# ✨ Features
🔍 Search YouTube directly from the app
▶️ Stream audio instantly (no full download required)
⬇️ Download songs as MP3
🎧 Built-in audio player (powered by VLC)
🖼️ Thumbnail previews for search results
🎚️ Volume + seek controls
⚡ Multithreaded UI (no freezing)

# 🖼️ Preview
![App Screenshot](screenshots/app.png)

# 🧰 Tech Stack
Python 3
PyQt6 (GUI)
VLC (audio playback)
yt-dlp (YouTube extraction)
requests (thumbnail fetching)

# ⚙️ Requirements
🔹 Python Packages

Install via pip:

pip install PyQt6 python-vlc requests yt-dlp
🔹 System Dependencies (Required)

Make sure these are installed on your system:

1. VLC Media Player

Download: https://www.videolan.org/vlc/

Required for audio playback (python-vlc depends on it)

2. Node.js

Download: https://nodejs.org/

Required because yt-dlp uses:

--js-runtimes node
--remote-components ejs:github
3. yt-dlp (CLI tool)

Already installed via pip above, but ensure it's accessible:

yt-dlp --version

# 🚀 How to Run

python v2player.py
📁 Project Structure
.
├── v2player.py
├── Music/        # downloaded songs
├── temp/         # temporary audio files
└── README.md

# 🧠 How It Works
Uses yt-dlp to:
search YouTube
fetch audio streams
Streams audio into temporary .webm files
Plays audio using VLC backend
Uses PyQt6 for UI + threading to keep app responsive

# ⚠️ Known Issues
VLC must match your system architecture (32/64-bit)
If playback fails → check VLC installation
If search fails → ensure Node.js is installed
Temporary files may remain if app crashes

# 🛠️ Future Improvements
Playlist support
Queue system
Better UI styling
Offline library view
Progress bar seeking (bidirectional)

# 📜 Disclaimer

This project is for educational purposes only.
Make sure you comply with YouTube's terms of service when using this tool.

# ⭐ Contributing

Pull requests are welcome. Feel free to open issues for bugs or feature requests.

📄 License

MIT License (or choose your preferred license)
