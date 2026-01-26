import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import threading

from app.downloader import fetch_video_info, download_video
from app.logger import logger


class ModernYouTubeDownloader(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("HitroBro YouTube Pro")
        self.geometry("1100x680")

        self.download_path = tk.StringVar(value="Downloads")
        self.url_var = tk.StringVar()
        self.video_info = None
        self.quality_streams = {}

        self.setup_ui()

    def setup_ui(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.url_entry = ctk.CTkEntry(self, textvariable=self.url_var, width=600)
        self.url_entry.pack(pady=20)

        self.fetch_btn = ctk.CTkButton(self, text="Fetch Info", command=self.get_video_info)
        self.fetch_btn.pack()

        self.quality_combo = ctk.CTkOptionMenu(self, values=["Fetch video first"])
        self.quality_combo.pack(pady=10)

        self.path_entry = ctk.CTkEntry(self, textvariable=self.download_path, width=400)
        self.path_entry.pack(pady=5)

        ctk.CTkButton(self, text="Browse", command=self.browse_path).pack()

        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(fill="x", padx=50, pady=10)

        self.status_label = ctk.CTkLabel(self, text="Ready")
        self.status_label.pack()

        self.download_btn = ctk.CTkButton(self, text="Start Download", command=self.start_download)
        self.download_btn.pack(pady=20)

    def browse_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)

    def get_video_info(self):
        url = self.url_var.get().strip()
        if not url:
            return
        threading.Thread(target=self._fetch_thread, args=(url,), daemon=True).start()

    def _fetch_thread(self, url):
        try:
            info, formats = fetch_video_info(url)
            self.after(0, lambda: self.update_ui(info, formats))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))

    def update_ui(self, info, formats):
        self.video_info = info
        self.quality_streams = {f[0]: f[1] for f in formats}
        self.quality_combo.configure(values=[f[0] for f in formats])
        self.quality_combo.set(formats[0][0])
        self.status_label.configure(text="Metadata loaded")

    def start_download(self):
        if not self.video_info:
            return
        threading.Thread(target=self._download_thread, daemon=True).start()

    def _download_thread(self):
        try:
            fmt_id = self.quality_streams[self.quality_combo.get()]
            download_video(
                self.url_var.get(),
                fmt_id,
                self.download_path.get(),
                self.progress_hook
            )
            self.after(0, lambda: self.status_label.configure(text="Download complete"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Download Error", str(e)))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').replace('%', '')
            try:
                self.after(0, lambda: self.progress.set(float(percent) / 100))
            except:
                pass
