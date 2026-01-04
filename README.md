# 📺 Modern YouTube Downloader (GUI)
**A responsive, multi-threaded desktop application for archiving media with `yt-dlp`.**

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/GUI-Tkinter-green?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Engine-yt--dlp-red?style=for-the-badge&logo=youtube" />
  <img src="https://img.shields.io/badge/License-MIT-orange?style=for-the-badge&logo=license" />
</p>

---

### 🚀 Overview
**Modern-YTDLP-GUI** is a robust desktop wrapper for the powerful `yt-dlp` command-line tool. 

Unlike simple downloaders that freeze the interface during large transfers, this application implements a **Threaded Architecture**. It offloads the heavy network and disk I/O to background threads, keeping the UI completely responsive (no "App Not Responding" errors). It allows for one-click downloading of videos up to 4K or extracting high-quality audio.

---

### ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **⚡ Non-Blocking UI** | Uses Python's `threading` and `queue` modules to run downloads asynchronously. |
| **🎨 Modern Design** | Features a custom-styled Tkinter interface with a professional dark theme and card-based layout. |
| **🛠️ Smart Engine** | Automatically detects dependencies and handles the `yt-dlp` hook system for real-time progress bars. |
| **🎧 Format Control** | Intelligent format selection to merge the best video stream (e.g., 1080p/4K) with the best audio stream. |
| **📂 Auto-Organization** | Sanitizes filenames automatically to prevent filesystem errors. |

---

### 🛠️ Technical Stack
* **Language:** Python 3.10+
* **GUI Framework:** Tkinter (Custom `ttk` styling)
* **Core Logic:** `yt-dlp` library (API Hooks)
* **Concurrency:** `threading` for background tasks

---

### 📦 Installation

#### 1. Clone the Repository
```bash
git clone [https://github.com/HitroBro/Modern-YTDLP-GUI.git](https://github.com/HitroBro/Modern-YTDLP-GUI.git)
cd Modern-YTDLP-GUI