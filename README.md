\# 📺 Modern YouTube Downloader (GUI)

\*\*A responsive, multi-threaded desktop application for archiving media with `yt-dlp`.\*\*



<p align="left">

&nbsp; <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge\&logo=python" />

&nbsp; <img src="https://img.shields.io/badge/GUI-Tkinter-green?style=for-the-badge\&logo=python" />

&nbsp; <img src="https://img.shields.io/badge/Engine-yt--dlp-red?style=for-the-badge\&logo=youtube" />

</p>



---



\### 🚀 Overview

This is a robust GUI wrapper for the powerful `yt-dlp` command-line tool. Unlike simple downloaders that freeze the interface during large downloads, this application uses a \*\*Threaded Architecture\*\* to keep the UI responsive while processing heavy media files in the background.



It is designed for archivists and power users who need reliability over simplicity.



---



\### ✨ Key Features

| Feature | Description |

| :--- | :--- |

| \*\*⚡ Non-Blocking UI\*\* | Uses Python's `threading` module to run downloads asynchronously, preventing "App Not Responding" errors. |

| \*\*🎨 Modern Design\*\* | Features a custom-styled Tkinter interface with a clean, dark-themed aesthetic. |

| \*\*🛠️ Smart Engine\*\* | Automatically detects if `yt-dlp` or `ffmpeg` is missing and handles dependencies gracefully. |

| \*\*🎧 Format Control\*\* | One-click conversion between high-quality Video (MP4) and Audio (MP3). |

| \*\*📊 Real-time Progress\*\* | LIVE progress bar and status updates directly from the `yt-dlp` hook system. |



---



\### 🛠️ Technical Stack

\* \*\*Language:\*\* Python 3.10+

\* \*\*GUI Framework:\*\* Tkinter (Custom `ttk` styling)

\* \*\*Core Logic:\*\* `yt-dlp` library (API Hooks)

\* \*\*Concurrency:\*\* `threading` \& `queue` for thread-safe UI updates.



---



\### 📦 Installation

1\. \*\*Clone the repo:\*\*

&nbsp;  ```bash

&nbsp;  git clone \[https://github.com/HitroBro/Modern-YTDLP-GUI.git](https://github.com/HitroBro/Modern-YTDLP-GUI.git)

