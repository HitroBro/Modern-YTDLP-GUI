from typing import Dict, List, Tuple
import yt_dlp
from app.utils import format_size
from app.logger import logger


def fetch_video_info(url: str) -> tuple[dict, List[Tuple[str, str]]]:
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = []
    for f in info.get('formats', []):
        if f.get('height') and f.get('ext') != 'mhtml' and f.get('vcodec') != 'none':
            size_str = format_size(f.get('filesize_approx') or f.get('filesize'))
            label = f"{f['height']}p ({f['ext']}) - {size_str}"
            formats.append((label, f['format_id'], f.get('height', 0)))

    formats.sort(key=lambda x: x[2], reverse=True)
    final_list = [(f[0], f[1]) for f in formats]

    logger.info("Video metadata fetched successfully")
    return info, final_list


def download_video(url: str, format_id: str, path: str, hook):
    opts = {
        'format': f"{format_id}+bestaudio/best",
        'outtmpl': f"{path}/%(title)s.%(ext)s",
        'progress_hooks': [hook],
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    logger.info("Download completed")
