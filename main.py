import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import re
import sys
import shutil
from urllib.parse import urlparse, parse_qs
import yt_dlp


def auto_update_yt_dlp():
    try:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], check=True)
    except Exception as e:
        print("yt-dlp upgrade failed:", e)


auto_update_yt_dlp()


def ensure_ffmpeg_in_path():
    """
    Ensure ffmpeg.exe is discoverable by yt-dlp by injecting it into PATH
    if it's in the same folder as the executable.
    """
    import os
    import sys

    ffmpeg_path = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)


try:
    from pytube import YouTube
    from pytube.exceptions import RegexMatchError, VideoUnavailable, AgeRestrictedError

    PYTUBE_AVAILABLE = True
except ImportError:
    PYTUBE_AVAILABLE = False

try:
    import yt_dlp

    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False


class ModernYouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        # Modern color scheme
        self.colors = {
            'primary': '#2563eb',  # Blue
            'primary_hover': '#1d4ed8',
            'success': '#10b981',  # Green
            'warning': '#f59e0b',  # Amber
            'error': '#ef4444',  # Red
            'surface': '#f8fafc',  # Light gray
            'surface_dark': '#e2e8f0',
            'text': '#1e293b',  # Dark gray
            'text_light': '#64748b',  # Medium gray
            'border': '#cbd5e1',  # Light border
            'white': '#ffffff'
        }

        self.root.configure(bg=self.colors['surface'])

        # Make window resizable
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Variables
        self.download_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar()
        self.format_var = tk.StringVar(value="mp4")
        self.backend_var = tk.StringVar(value="auto")

        # Storage for video info and quality streams
        self.video_info = None
        self.quality_streams = {}

        # Check available backends
        self.available_backends = []
        if YTDLP_AVAILABLE:
            self.available_backends.append("yt-dlp")
        if PYTUBE_AVAILABLE:
            self.available_backends.append("pytube")

        if not self.available_backends:
            messagebox.showerror("Error",
                                 "No download backend available!\n\nPlease install one of the following:\n- pip install yt-dlp\n- pip install pytube")
            root.destroy()
            return

        self.setup_modern_style()
        self.setup_ui()
        self.center_window()

    def setup_modern_style(self):
        """Configure modern styling for ttk widgets"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configure button styles
        self.style.configure('Modern.TButton',
                             padding=(20, 12),
                             font=('Segoe UI', 10, 'bold'),
                             borderwidth=0,
                             focuscolor='none')

        self.style.map('Modern.TButton',
                       background=[('active', self.colors['primary_hover']),
                                   ('!active', self.colors['primary'])],
                       foreground=[('active', self.colors['white']),
                                   ('!active', self.colors['white'])],
                       relief=[('pressed', 'flat'),
                               ('!pressed', 'flat')])

        # Large touch-friendly buttons
        self.style.configure('Large.TButton',
                             padding=(25, 15),
                             font=('Segoe UI', 12, 'bold'),
                             borderwidth=0,
                             focuscolor='none')

        self.style.map('Large.TButton',
                       background=[('active', self.colors['success']),
                                   ('!active', self.colors['success'])],
                       foreground=[('active', self.colors['white']),
                                   ('!active', self.colors['white'])],
                       relief=[('pressed', 'flat'),
                               ('!pressed', 'flat')])

        # Secondary button style
        self.style.configure('Secondary.TButton',
                             padding=(15, 10),
                             font=('Segoe UI', 9),
                             borderwidth=1,
                             focuscolor='none')

        self.style.map('Secondary.TButton',
                       background=[('active', self.colors['surface_dark']),
                                   ('!active', self.colors['white'])],
                       foreground=[('active', self.colors['text']),
                                   ('!active', self.colors['text'])],
                       bordercolor=[('active', self.colors['border']),
                                    ('!active', self.colors['border'])])

        # Entry field styling
        self.style.configure('Modern.TEntry',
                             padding=(12, 10),
                             borderwidth=1,
                             relief='solid',
                             bordercolor=self.colors['border'],
                             lightcolor=self.colors['border'],
                             darkcolor=self.colors['border'],
                             fieldbackground=self.colors['white'])

        # Combobox styling
        self.style.configure('Modern.TCombobox',
                             padding=(12, 8),
                             borderwidth=1,
                             relief='solid',
                             bordercolor=self.colors['border'],
                             fieldbackground=self.colors['white'])

        # Frame styling
        self.style.configure('Card.TFrame',
                             background=self.colors['white'],
                             relief='flat',
                             borderwidth=1)

        # Label styling
        self.style.configure('Title.TLabel',
                             background=self.colors['surface'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 24, 'bold'))

        self.style.configure('Heading.TLabel',
                             background=self.colors['white'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 12, 'bold'))

        self.style.configure('Info.TLabel',
                             background=self.colors['white'],
                             foreground=self.colors['text_light'],
                             font=('Segoe UI', 10))

        self.style.configure('Status.TLabel',
                             background=self.colors['surface'],
                             foreground=self.colors['success'],
                             font=('Segoe UI', 11, 'bold'))

    def setup_ui(self):
        # Create main scrollable frame
        main_canvas = tk.Canvas(self.root, bg=self.colors['surface'], highlightthickness=0)
        main_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        main_canvas.configure(yscrollcommand=scrollbar.set)

        # Create main frame inside canvas
        main_frame = ttk.Frame(main_canvas, style='TFrame', padding="30")
        main_canvas.create_window((0, 0), window=main_frame, anchor="nw")

        main_frame.columnconfigure(0, weight=1)

        # Title section
        title_frame = ttk.Frame(main_frame, style='TFrame')
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 30))
        title_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(title_frame, text="YouTube Downloader", style='Title.TLabel')
        title_label.grid(row=0, column=0)

        subtitle_label = ttk.Label(title_frame, text="Download videos and audio from YouTube",
                                   style='Info.TLabel')
        subtitle_label.grid(row=1, column=0, pady=(5, 0))

        # URL input card
        url_card = ttk.Frame(main_frame, style='Card.TFrame', padding="25")
        url_card.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        url_card.columnconfigure(0, weight=1)

        url_heading = ttk.Label(url_card, text="Video URL", style='Heading.TLabel')
        url_heading.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        url_input_frame = ttk.Frame(url_card, style='TFrame')
        url_input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        url_input_frame.columnconfigure(0, weight=1)

        self.url_entry = ttk.Entry(url_input_frame, textvariable=self.url_var,
                                   style='Modern.TEntry', font=('Segoe UI', 11))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))

        paste_btn = ttk.Button(url_input_frame, text="📋 Paste", command=self.paste_url,
                               style='Secondary.TButton', width=12)
        paste_btn.grid(row=0, column=1)

        get_info_btn = ttk.Button(url_card, text="🔍 Get Video Info", command=self.get_video_info,
                                  style='Modern.TButton', width=20)
        get_info_btn.grid(row=2, column=0, pady=(0, 0))

        # Video Information card
        self.info_card = ttk.Frame(main_frame, style='Card.TFrame', padding="25")
        self.info_card.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        self.info_card.columnconfigure(0, weight=1)

        info_heading = ttk.Label(self.info_card, text="Video Information", style='Heading.TLabel')
        info_heading.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        self.title_label = ttk.Label(self.info_card, text="📹 Title: Load a video to see details",
                                     style='Info.TLabel', wraplength=700)
        self.title_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 8))

        self.duration_label = ttk.Label(self.info_card, text="⏱️ Duration: --",
                                        style='Info.TLabel')
        self.duration_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 8))

        self.views_label = ttk.Label(self.info_card, text="👁️ Views: --",
                                     style='Info.TLabel')
        self.views_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 0))

        # Download Options card
        options_card = ttk.Frame(main_frame, style='Card.TFrame', padding="25")
        options_card.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        options_card.columnconfigure(1, weight=1)

        options_heading = ttk.Label(options_card, text="Download Options", style='Heading.TLabel')
        options_heading.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 20))

        # First row of options
        ttk.Label(options_card, text="Backend:", style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        backend_combo = ttk.Combobox(options_card, textvariable=self.backend_var,
                                     values=["auto"] + self.available_backends,
                                     state="readonly", style='Modern.TCombobox', width=15)
        backend_combo.grid(row=1, column=1, sticky=tk.W, padx=(0, 30))

        ttk.Label(options_card, text="Format:", style='Info.TLabel').grid(row=1, column=2, sticky=tk.W, padx=(0, 10))
        format_combo = ttk.Combobox(options_card, textvariable=self.format_var,
                                    values=["mp4", "mp3 (audio only)", "webm", "mkv"],
                                    state="readonly", style='Modern.TCombobox', width=18)
        format_combo.grid(row=1, column=3, sticky=tk.W)

        # Quality selection
        ttk.Label(options_card, text="Quality:", style='Info.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(15, 0))
        self.quality_combo = ttk.Combobox(options_card, textvariable=self.quality_var,
                                          state="readonly", style='Modern.TCombobox', width=60)
        self.quality_combo.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))

        # Download Path card
        path_card = ttk.Frame(main_frame, style='Card.TFrame', padding="25")
        path_card.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        path_card.columnconfigure(0, weight=1)

        path_heading = ttk.Label(path_card, text="Download Location", style='Heading.TLabel')
        path_heading.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        path_input_frame = ttk.Frame(path_card, style='TFrame')
        path_input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        path_input_frame.columnconfigure(0, weight=1)

        path_entry = ttk.Entry(path_input_frame, textvariable=self.download_path,
                               style='Modern.TEntry', font=('Segoe UI', 11))
        path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))

        browse_btn = ttk.Button(path_input_frame, text="📁 Browse", command=self.browse_path,
                                style='Secondary.TButton', width=12)
        browse_btn.grid(row=0, column=1)

        # Progress and Status card
        progress_card = ttk.Frame(main_frame, style='Card.TFrame', padding="25")
        progress_card.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_card.columnconfigure(0, weight=1)

        progress_heading = ttk.Label(progress_card, text="Status", style='Heading.TLabel')
        progress_heading.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        self.progress = ttk.Progressbar(progress_card, mode='indeterminate', style='TProgressbar')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.status_label = ttk.Label(progress_card, text="✅ Ready to download",
                                      style='Status.TLabel')
        self.status_label.grid(row=2, column=0, sticky=tk.W)

        # Download button
        self.download_btn = ttk.Button(main_frame, text="⬇️ Download Video",
                                       command=self.start_download, style='Large.TButton')
        self.download_btn.grid(row=6, column=0, pady=(10, 20))

        # Update canvas scroll region
        def configure_scroll_region(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))

        main_frame.bind("<Configure>", configure_scroll_region)

        # Mouse wheel scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        main_canvas.bind_all("<MouseWheel>", on_mousewheel)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def paste_url(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.url_var.set(clipboard_text)
            self.url_entry.focus_set()
        except tk.TclError:
            messagebox.showwarning("Warning", "Clipboard is empty or contains non-text data")

    def is_valid_youtube_url(self, url):
        """Enhanced URL validation for various YouTube URL formats"""
        youtube_patterns = [
            r'(https?://)?(www\.)?(youtube|youtu)\.(com|be)/.+',
            r'(https?://)?(www\.)?youtube\.com/watch\?v=.+',
            r'(https?://)?(www\.)?youtu\.be/.+',
            r'(https?://)?(www\.)?youtube\.com/embed/.+',
            r'(https?://)?(www\.)?youtube\.com/v/.+',
            r'(https?://)?(www\.)?m\.youtube\.com/watch\?v=.+'
        ]
        return any(re.match(pattern, url) for pattern in youtube_patterns)

    def get_video_info(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        if not self.is_valid_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL format")
            return

        self.progress.start()
        self.status_label.config(text="🔄 Loading video information...")
        self.style.configure('Status.TLabel', foreground=self.colors['primary'])
        threading.Thread(target=self._get_video_info_thread, args=(url,), daemon=True).start()

    def _get_video_info_thread(self, url):
        backend = self.backend_var.get()
        backends_to_try = self.available_backends if backend == "auto" else [backend]

        for backend_name in backends_to_try:
            try:
                if backend_name == "yt-dlp":
                    info = self._get_info_ytdlp(url)
                else:
                    info = self._get_info_pytube(url)

                self.root.after(0, self._update_video_info, info, backend_name)
                return
            except Exception as e:
                error_msg = str(e)
                print(f"{backend_name} failed: {error_msg}")

        # All backends failed
        self.root.after(0, lambda: self.show_error(
            "All backends failed to load video information.\n\n"
            "Possible causes:\n"
            "• Video is private or restricted\n"
            "• Age-restricted content\n"
            "• Invalid URL\n"
            "• Network connectivity issues\n"
            "• Backend libraries need updating"
        ))
        self.root.after(0, self.progress.stop)

    def _get_info_ytdlp(self, url):
        ensure_ffmpeg_in_path()
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'ignoreerrors': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 0),
            'view_count': info.get('view_count', 0),
            'formats': info.get('formats', []),
            'backend': 'yt-dlp',
            'url': url
        }

    def _get_info_pytube(self, url):
        yt = YouTube(url)
        return {
            'title': yt.title,
            'duration': yt.length,
            'view_count': yt.views,
            'streams': yt.streams,
            'backend': 'pytube',
            'url': url,
            'yt_object': yt
        }

    def _update_video_info(self, info, backend_used):
        try:
            # Update video information display
            self.title_label.config(text=f"📹 Title: {info['title']}")
            self.duration_label.config(text=f"⏱️ Duration: {self.format_duration(info['duration'])}")
            self.views_label.config(text=f"👁️ Views: {info['view_count']:,}")

            # Store info for download
            self.video_info = info

            # Update quality options based on backend
            qualities = []

            if backend_used == "yt-dlp":
                qualities = self._process_ytdlp_formats(info['formats'])
            elif backend_used == "pytube":
                qualities = self._process_pytube_streams(info['streams'])

            if qualities:
                self.quality_combo['values'] = [q[0] for q in qualities]
                self.quality_streams = {q[0]: q[1] for q in qualities}
                self.quality_combo.current(0)
                self.quality_var.set(qualities[0][0])

            self.status_label.config(text=f"✅ Video loaded successfully using {backend_used}!")
            self.style.configure('Status.TLabel', foreground=self.colors['success'])
            self.progress.stop()

        except Exception as e:
            self.show_error(f"Error processing video info: {str(e)}")

    def _process_ytdlp_formats(self, formats):
        """Process yt-dlp formats and return quality options"""
        video_formats = []
        audio_formats = []

        for fmt in formats:
            if not fmt:
                continue

            height = fmt.get('height', 0)
            width = fmt.get('width', 0)
            abr = fmt.get('abr', 0)
            has_video = fmt.get('vcodec', 'none') != 'none'
            has_audio = fmt.get('acodec', 'none') != 'none'
            ext = fmt.get('ext', 'unknown')
            fps = fmt.get('fps', 0)

            # Calculate file size
            size = fmt.get('filesize') or fmt.get('filesize_approx') or 0
            size_str = f"{size // 1024 // 1024}MB" if size > 0 else "?MB"

            if has_video and has_audio and height:
                # Combined video + audio
                fps_str = f" {fps}fps" if fps > 0 else ""
                quality_text = f"🎬 {height}p{fps_str} - {size_str} ({ext})"
                video_formats.append((quality_text, fmt))
            elif has_video and not has_audio and height:
                # Video only
                fps_str = f" {fps}fps" if fps > 0 else ""
                quality_text = f"🎥 {height}p{fps_str} (video only) - {size_str} ({ext})"
                video_formats.append((quality_text, fmt))
            elif has_audio and not has_video:
                # Audio only
                if abr:
                    quality_text = f"🎵 Audio {int(abr)}kbps - {size_str} ({ext})"
                else:
                    quality_text = f"🎵 Audio - {size_str} ({ext})"
                audio_formats.append((quality_text, fmt))

        # Sort by quality (highest first)
        video_formats.sort(key=lambda x: x[1].get('height', 0), reverse=True)
        audio_formats.sort(key=lambda x: x[1].get('abr', 0), reverse=True)

        return video_formats + audio_formats

    def _process_pytube_streams(self, streams):
        """Process pytube streams and return quality options"""
        qualities = []

        # Progressive streams (video + audio)
        progressive_streams = streams.filter(progressive=True).order_by('resolution').desc()
        for stream in progressive_streams:
            if stream.resolution:
                size_mb = stream.filesize // 1024 // 1024 if stream.filesize else 0
                quality_text = f"🎬 {stream.resolution} - {size_mb}MB ({stream.mime_type.split('/')[-1]})"
                qualities.append((quality_text, stream))

        # Audio only streams
        audio_streams = streams.filter(only_audio=True).order_by('abr').desc()
        for stream in audio_streams:
            if stream.abr:
                size_mb = stream.filesize // 1024 // 1024 if stream.filesize else 0
                quality_text = f"🎵 Audio {stream.abr} - {size_mb}MB ({stream.mime_type.split('/')[-1]})"
                qualities.append((quality_text, stream))

        return qualities

    def format_duration(self, seconds):
        """Format duration in a readable format"""
        if not seconds:
            return "Unknown"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    def browse_path(self):
        folder = filedialog.askdirectory(
            initialdir=self.download_path.get(),
            title="Select Download Folder"
        )
        if folder:
            self.download_path.set(folder)

    def start_download(self):
        # Validate inputs
        url = self.url_var.get().strip()
        quality = self.quality_var.get()
        path = self.download_path.get()

        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        if not quality:
            messagebox.showerror("Error", "Please select a quality option")
            return
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Please select a valid download path")
            return
        if not self.video_info:
            messagebox.showerror("Error", "Please load video information first")
            return

        # Start download
        self.progress.start()
        self.download_btn.config(state="disabled")
        self.status_label.config(text="⬇️ Downloading...")
        self.style.configure('Status.TLabel', foreground=self.colors['primary'])

        threading.Thread(target=self._download_thread, args=(url, quality, path), daemon=True).start()

    def _download_thread(self, url, quality, path):
        try:
            stream = self.quality_streams.get(quality)
            if not stream:
                raise Exception("Selected quality not available")

            if self.video_info['backend'] == 'yt-dlp':
                self._download_with_ytdlp(stream, path)
            else:
                self._download_with_pytube(stream, path)

        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Download failed: {str(e)}"))
        finally:
            self.root.after(0, self.reset_download_state)

    def _download_with_ytdlp(self, fmt, path):
        """Download using yt-dlp backend"""
        ensure_ffmpeg_in_path()

        title = self.video_info['title']
        safe_title = self.clean_filename(title)

        # Determine format and output settings
        if self.format_var.get() == "mp3 (audio only)":
            ext = 'mp3'
            format_selector = 'bestaudio'
        else:
            ext = fmt.get('ext', 'mp4')
            # Check if we need to merge video and audio
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') == 'none':
                # Video only format, merge with best audio
                format_selector = f"{fmt['format_id']}+bestaudio"
            else:
                format_selector = fmt['format_id']

        filename = f"{safe_title}.{ext}"
        output_path = os.path.join(path, filename)

        ydl_opts = {
            'outtmpl': output_path,
            'format': format_selector,
            'merge_output_format': ext if ext != 'mp3' else None,
        }

        # Add post-processing for mp3
        if self.format_var.get() == "mp3 (audio only)":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.video_info['url']])

        self.root.after(0, lambda: self.download_complete(filename))

    def _download_with_pytube(self, stream, path):
        """Download using pytube backend"""
        title = stream.title
        safe_title = self.clean_filename(title)

        if self.format_var.get() == "mp3 (audio only)":
            filename = f"{safe_title}.mp3"
        else:
            filename = f"{safe_title}.{stream.mime_type.split('/')[-1]}"

        stream.download(output_path=path, filename=filename)
        self.root.after(0, lambda: self.download_complete(filename))

    def clean_filename(self, name):
        """Clean filename by removing invalid characters"""
        # Remove invalid characters for file names
        cleaned = re.sub(r'[<>:"/\\|?*]', '', name)
        # Remove extra spaces and dots
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        # Limit length
        if len(cleaned) > 200:
            cleaned = cleaned[:200]
        return cleaned

    def download_complete(self, filename):
        """Handle download completion"""
        self.status_label.config(text=f"✅ Download completed: {filename}")
        self.style.configure('Status.TLabel', foreground=self.colors['success'])
        messagebox.showinfo("Download Complete", f"Successfully downloaded:\n{filename}")

    def reset_download_state(self):
        """Reset UI state after download"""
        self.progress.stop()
        self.download_btn.config(state="normal")

    def show_error(self, message):
        """Display error message"""
        self.status_label.config(text="❌ Error occurred")
        self.style.configure('Status.TLabel', foreground=self.colors['error'])
        self.progress.stop()
        messagebox.showerror("Error", message)


if __name__ == "__main__":
    # Check for required dependencies
    if not PYTUBE_AVAILABLE and not YTDLP_AVAILABLE:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showerror(
            "Missing Dependencies",
            "No download backend available!\n\n"
            "Please install one of the following:\n"
            "• pip install yt-dlp (recommended)\n"
            "• pip install pytube\n\n"
            "yt-dlp is more reliable and actively maintained."
        )
        sys.exit(1)

    # Create and run the application
    root = tk.Tk()
    app = ModernYouTubeDownloader(root)
    root.mainloop()