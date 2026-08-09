"""
HitroBro YouTube Pro - Stable Edition

Author: HitroBro

Description:
    A modern GUI-based YouTube downloader application that integrates
    yt-dlp extraction logic with a CustomTkinter user interface.
    Supports format selection, quality filtering, threaded downloads,
    and real-time progress tracking.
"""

from typing import Dict, List, Tuple, Optional
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import threading
import os
import yt_dlp
from PIL import Image


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ModernYouTubeDownloader(ctk.CTk):
    """Main application class for YouTube Downloader GUI."""

    def __init__(self) -> None:
        super().__init__()

        self.title("HitroBro YouTube Pro")
        self.geometry("1100x680")
        self.iconbitmap("assets/icons/app_icon.ico")

        self.download_path: tk.StringVar = tk.StringVar(
            value=os.path.expanduser("~/Downloads")
        )
        self.url_var: tk.StringVar = tk.StringVar()
        self.format_var: tk.StringVar = tk.StringVar(value="mp4")

        self.video_info: Optional[dict] = None
        self.quality_streams: Dict[str, str] = {}

        self.setup_ui()

    def setup_ui(self) -> None:
        """Initialize and render all UI components."""

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        logo_path = os.path.join("assets", "images", "logo.png")

        self.logo_image = ctk.CTkImage(
            light_image=Image.open(logo_path),
            dark_image=Image.open(logo_path),
            size=(120, 120)
        )

        self.logo = ctk.CTkLabel(
            self.sidebar,
            image=self.logo_image,
            text=""
        )
        self.logo.grid(row=0, column=0, padx=20, pady=(20, 20))

        self._create_side_label("OUTPUT FORMAT", 1)
        self.format_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["mp4", "mp3", "mkv", "webm"],
            variable=self.format_var
        )
        self.format_menu.grid(row=2, column=0, padx=20, pady=10)

        self._create_side_label("THEME", 3)
        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["System", "Dark", "Light"],
            command=ctk.set_appearance_mode
        )
        self.theme_menu.grid(row=4, column=0, padx=20, pady=10)

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=40, pady=20)
        self.main.grid_columnconfigure(0, weight=1)

        self.input_card = ctk.CTkFrame(self.main, height=70)
        self.input_card.grid(row=1, column=0, sticky="ew", pady=10)

        self.url_entry = ctk.CTkEntry(
            self.input_card,
            textvariable=self.url_var,
            placeholder_text="Paste YouTube URL here...",
            height=45,
            border_width=0,
            fg_color="transparent"
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=20)

        self.fetch_btn = ctk.CTkButton(
            self.input_card,
            text="FETCH INFO",
            width=140,
            height=45,
            font=ctk.CTkFont(weight="bold"),
            command=self.get_video_info
        )
        self.fetch_btn.pack(side="right", padx=10, pady=10)

        self.info_card = ctk.CTkFrame(self.main)
        self.info_card.grid(row=2, column=0, sticky="ew", pady=20)

        self.title_label = ctk.CTkLabel(
            self.info_card,
            text="Ready to fetch video details...",
            font=ctk.CTkFont(size=18, weight="bold"),
            wraplength=700
        )
        self.title_label.pack(pady=(25, 10), padx=25, anchor="w")

        self.stats_label = ctk.CTkLabel(
            self.info_card,
            text="Views: -- | Duration: --",
            text_color="gray"
        )
        self.stats_label.pack(pady=(0, 25), padx=25, anchor="w")

        self.ctrl_card = ctk.CTkFrame(self.main, fg_color="transparent")
        self.ctrl_card.grid(row=3, column=0, sticky="ew")
        self.ctrl_card.grid_columnconfigure(0, weight=1)
        self.ctrl_card.grid_columnconfigure(1, weight=1)

        self.q_frame = ctk.CTkFrame(self.ctrl_card)
        self.q_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(
            self.q_frame,
            text="Select Quality",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(15, 5), padx=20, anchor="w")

        self.quality_combo = ctk.CTkOptionMenu(
            self.q_frame,
            values=["Fetch video first"],
            width=300
        )
        self.quality_combo.pack(pady=(5, 20), padx=20)

        self.p_frame = ctk.CTkFrame(self.ctrl_card)
        self.p_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        ctk.CTkLabel(
            self.p_frame,
            text="Save Location",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(15, 5), padx=20, anchor="w")

        p_box = ctk.CTkFrame(self.p_frame, fg_color="transparent")
        p_box.pack(fill="x", padx=20, pady=(5, 20))

        self.path_entry = ctk.CTkEntry(
            p_box,
            textvariable=self.download_path,
            height=30
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            p_box,
            text="📁",
            width=40,
            command=self.browse_path
        ).pack(side="right")

        self.progress = ctk.CTkProgressBar(self.main)
        self.progress.grid(row=4, column=0, sticky="ew", pady=(40, 5))
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            self.main,
            text="System Status: Ready",
            text_color="gray"
        )
        self.status_label.grid(row=5, column=0)

        self.download_btn = ctk.CTkButton(
            self.main,
            text="🚀 START DOWNLOAD",
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.start_download
        )
        self.download_btn.grid(row=6, column=0, pady=20)

    def _create_side_label(self, text: str, row: int) -> None:
        lbl = ctk.CTkLabel(
            self.sidebar,
            text=text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        )
        lbl.grid(row=row, column=0, padx=20, pady=(15, 0), sticky="w")

    def browse_path(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)

    def get_video_info(self) -> None:
        url = self.url_var.get().strip()
        if not url:
            return

        self.status_label.configure(
            text="System: Synchronizing with YouTube...",
            text_color="#3b8ed0"
        )
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        threading.Thread(
            target=self._fetch_thread,
            args=(url,),
            daemon=True
        ).start()

    def _fetch_thread(self, url: str) -> None:
        try:
            opts = {'quiet': True, 'no_warnings': True}

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

            formats: List[Tuple[str, str, int]] = []

            for f in info.get('formats', []):
                if f.get('height') and f.get('vcodec') != 'none':
                    fs = f.get('filesize_approx') or f.get('filesize')
                    size_str = f"{fs // 1048576}MB" if fs else "Unknown size"
                    label = f"{f['height']}p ({f['ext']}) - {size_str}"
                    formats.append((label, f['format_id'], f.get('height', 0)))

            formats.sort(key=lambda x: x[2], reverse=True)
            final_list = [(f[0], f[1]) for f in formats]

            self.after(0, lambda: self._update_ui(info, final_list))

        except Exception as exc:
            self.after(0, lambda m=str(exc): self._handle_error(m))

    def _update_ui(self, info: dict, formats: List[Tuple[str, str]]) -> None:
        self.video_info = info
        self.title_label.configure(text=info['title'])
        self.stats_label.configure(
            text=f"👁️ {info.get('view_count', 0):,} Views | ⏱️ {info.get('duration')}s"
        )

        self.quality_streams = {f[0]: f[1] for f in formats}
        self.quality_combo.configure(values=[f[0] for f in formats])
        self.quality_combo.set(formats[0][0])

        self.progress.stop()
        self.progress.configure(mode="determinate")
        self.progress.set(0)

        self.status_label.configure(
            text="System: Meta-Data Synchronized",
            text_color="#10b981"
        )

    def _handle_error(self, message: str) -> None:
        self.progress.stop()
        messagebox.showerror("Operation Error", message)

    def start_download(self) -> None:
        if not self.video_info:
            return

        self.download_btn.configure(state="disabled")

        threading.Thread(
            target=self._download_thread,
            daemon=True
        ).start()

    def _download_thread(self) -> None:
        try:
            fmt_id = self.quality_streams[self.quality_combo.get()]

            opts = {
                'format': f"{fmt_id}+bestaudio/best",
                'outtmpl': os.path.join(
                    self.download_path.get(),
                    '%(title)s.%(ext)s'
                ),
                'progress_hooks': [self._progress_hook],
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url_var.get()])

            self.after(0, lambda: self.status_label.configure(
                text="System: Process Complete! ✅",
                text_color="#10b981"
            ))

        except Exception as exc:
            self.after(0, lambda m=str(exc): messagebox.showerror("Download Failure", m))

        finally:
            self.after(0, lambda: self.download_btn.configure(state="normal"))

    def _progress_hook(self, d: dict) -> None:
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').replace('%', '').strip()
            try:
                self.after(0, lambda: self.progress.set(float(percent) / 100))
            except ValueError:
                pass


if __name__ == "__main__":
    app = ModernYouTubeDownloader()
    app.mainloop()
