from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

SETTINGS_FILE = Path("settings.json")


@dataclass
class AppSettings:
    theme: str = "dark"
    last_folder: str = "downloads"
    mode: str = "Video"
    quality: str = "Best"


def load_settings() -> AppSettings:
    if not SETTINGS_FILE.exists():
        return AppSettings()

    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return AppSettings(
            theme=str(data.get("theme", "dark")),
            last_folder=str(data.get("last_folder", "downloads")),
            mode=str(data.get("mode", "Video")),
            quality=str(data.get("quality", "Best")),
        )
    except Exception:
        return AppSettings()


def save_settings(settings: AppSettings) -> None:
    SETTINGS_FILE.write_text(
        json.dumps(asdict(settings), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
