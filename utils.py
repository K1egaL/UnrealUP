from __future__ import annotations

import re
from urllib.parse import urlparse


YOUTUBE_RE = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
    re.IGNORECASE,
)


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""

    if url.startswith("youtube.com/") or url.startswith("youtu.be/"):
        return "https://" + url

    if url.startswith("www.youtube.com/") or url.startswith("www.youtu.be/"):
        return "https://" + url

    if url.startswith("youtube.com") or url.startswith("youtu.be"):
        return "https://www." + url

    return url


def is_youtube_url(url: str) -> bool:
    return bool(YOUTUBE_RE.match(normalize_url(url)))


def extract_youtube_url(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    match = re.search(
        r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/[^\s]+",
        text,
        re.IGNORECASE,
    )
    if match:
        return normalize_url(match.group(0))

    return normalize_url(text)


def format_bytes(size: float | int | None) -> str:
    if size is None:
        return "—"

    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)

    for unit in units:
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024

    return f"{value:.1f} PB"


def format_time(seconds: int | float | None) -> str:
    if seconds is None:
        return "—"

    seconds = int(seconds)
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f"{hours:02}:{minutes:02}:{secs:02}"

    return f"{minutes:02}:{secs:02}"
