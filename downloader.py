from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

import yt_dlp

from utils import normalize_url


class DownloadError(RuntimeError):
    pass


class Downloader:
    def __init__(self, ffmpeg_path: str | None = None, logger=None):
        self.ffmpeg_path = ffmpeg_path
        self.logger = logger

    def get_info(self, url: str) -> dict:
        url = normalize_url(url)

        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "socket_timeout": 20,
            "http_headers": {"User-Agent": "Mozilla/5.0"},
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as exc:
            raise DownloadError(f"Не удалось получить информацию о видео: {exc}") from exc

    def _build_format(self, mode: str, quality: str) -> str:
        if mode == "Audio":
            return "bestaudio/best"

        quality_map = {
            "Best": None,
            "1080p": 1080,
            "720p": 720,
            "480p": 480,
            "360p": 360,
        }
        height = quality_map.get(quality)

        if height is None:
            return "bv*+ba/b"

        return f"bv*[height<={height}]+ba/b[height<={height}]"

    def download(
        self,
        url: str,
        folder: str,
        mode: str,
        quality: str,
        progress_hook: Optional[Callable[[dict], None]] = None,
    ) -> None:
        url = normalize_url(url)
        folder_path = Path(folder)

        try:
            folder_path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            raise DownloadError(f"Не удалось создать папку загрузки: {exc}") from exc

        ydl_opts = {
            "format": self._build_format(mode, quality),
            "outtmpl": str(folder_path / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 20,
            "http_headers": {"User-Agent": "Mozilla/5.0"},
            "merge_output_format": "mp4",
            "progress_hooks": [progress_hook] if progress_hook else [],
        }

        if self.ffmpeg_path:
            ydl_opts["ffmpeg_location"] = str(self.ffmpeg_path)

        if mode == "Audio":
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as exc:
            raise DownloadError(f"Скачивание не удалось: {exc}") from exc
