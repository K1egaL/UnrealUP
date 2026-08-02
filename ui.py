from __future__ import annotations

import queue
import socket
import threading
from pathlib import Path
from tkinter import TclError, filedialog, messagebox

import customtkinter as ctk

from config import (
    APP_NAME,
    DOWNLOADS_DIR,
    FFMPEG_PATH,
    UI_REFRESH_MS,
    WINDOW_HEIGHT,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_WIDTH,
)
from downloader import DownloadError, Downloader
from logger import setup_logger
from settings import AppSettings, load_settings, save_settings
from utils import extract_youtube_url, format_bytes, format_time, is_youtube_url


class UnrealUP(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.logger = setup_logger()
        self.settings: AppSettings = load_settings()

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.downloader = Downloader(
            ffmpeg_path=str(FFMPEG_PATH) if FFMPEG_PATH.exists() else None,
            logger=self.logger,
        )

        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.worker: threading.Thread | None = None
        self._poll_after_id: str | None = None
        self._closing = False

        self.url_var = ctk.StringVar(value="")
        self.folder_var = ctk.StringVar(value=self.settings.last_folder or str(DOWNLOADS_DIR))
        self.mode_var = ctk.StringVar(value=self.settings.mode or "Video")
        self.quality_var = ctk.StringVar(value=self.settings.quality or "Best")

        self.title_var = ctk.StringVar(value="Название: —")
        self.status_var = ctk.StringVar(value="Готов к загрузке")
        self.progress_var = ctk.StringVar(value="0%")
        self.speed_var = ctk.StringVar(value="—")
        self.eta_var = ctk.StringVar(value="—")
        self.size_var = ctk.StringVar(value="—")

        self._build_ui()
        self._schedule_poll()

    def _build_ui(self) -> None:
        outer = ctk.CTkFrame(self, corner_radius=22)
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        header = ctk.CTkFrame(outer, corner_radius=18)
        header.pack(fill="x", padx=18, pady=(18, 12))

        ctk.CTkLabel(
            header,
            text="UnrealUP",
            font=ctk.CTkFont(size=30, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(14, 2))

        ctk.CTkLabel(
            header,
            text="Лёгкий загрузчик видео и аудио с YouTube",
            text_color="#A9B1BD",
        ).pack(anchor="w", padx=16, pady=(0, 14))

        body = ctk.CTkFrame(outer, corner_radius=18)
        body.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        url_card = ctk.CTkFrame(body, corner_radius=18)
        url_card.pack(fill="x", padx=18, pady=(18, 12))

        ctk.CTkLabel(url_card, text="Ссылка на видео").pack(anchor="w", padx=16, pady=(14, 6))

        url_row = ctk.CTkFrame(url_card, fg_color="transparent")
        url_row.pack(fill="x", padx=16, pady=(0, 14))

        self.url_entry = ctk.CTkEntry(
            url_row,
            textvariable=self.url_var,
            height=40,
            placeholder_text="https://www.youtube.com/watch?v=...",
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            url_row,
            text="📋 Вставить",
            width=110,
            height=40,
            command=self.paste_from_clipboard,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            url_row,
            text="Очистить",
            width=96,
            height=40,
            fg_color="#3A3F4B",
            hover_color="#4A5160",
            command=self.clear_all,
        ).pack(side="left")

        options_card = ctk.CTkFrame(body, corner_radius=18)
        options_card.pack(fill="x", padx=18, pady=(0, 12))

        options_row = ctk.CTkFrame(options_card, fg_color="transparent")
        options_row.pack(fill="x", padx=16, pady=16)

        left = ctk.CTkFrame(options_row, corner_radius=16)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ctk.CTkLabel(left, text="Режим").pack(anchor="w", padx=12, pady=(12, 6))
        ctk.CTkOptionMenu(
            left,
            values=["Video", "Audio"],
            variable=self.mode_var,
        ).pack(fill="x", padx=12, pady=(0, 12))

        middle = ctk.CTkFrame(options_row, corner_radius=16)
        middle.pack(side="left", fill="both", expand=True, padx=8)

        ctk.CTkLabel(middle, text="Качество").pack(anchor="w", padx=12, pady=(12, 6))
        ctk.CTkOptionMenu(
            middle,
            values=["Best", "1080p", "720p", "480p", "360p"],
            variable=self.quality_var,
        ).pack(fill="x", padx=12, pady=(0, 12))

        right = ctk.CTkFrame(options_row, corner_radius=16)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        ctk.CTkLabel(right, text="Папка").pack(anchor="w", padx=12, pady=(12, 6))

        folder_row = ctk.CTkFrame(right, fg_color="transparent")
        folder_row.pack(fill="x", padx=12, pady=(0, 12))

        self.folder_entry = ctk.CTkEntry(folder_row, textvariable=self.folder_var, height=36)
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            folder_row,
            text="📁",
            width=46,
            height=36,
            command=self.choose_folder,
        ).pack(side="left")

        info_card = ctk.CTkFrame(body, corner_radius=18)
        info_card.pack(fill="x", padx=18, pady=(0, 12))

        self.title_label = ctk.CTkLabel(info_card, textvariable=self.title_var, anchor="w")
        self.title_label.pack(fill="x", padx=16, pady=(14, 2))

        self.status_label = ctk.CTkLabel(
            info_card,
            textvariable=self.status_var,
            anchor="w",
            text_color="#A9B1BD",
        )
        self.status_label.pack(fill="x", padx=16, pady=(0, 14))

        progress_card = ctk.CTkFrame(body, corner_radius=18)
        progress_card.pack(fill="x", padx=18, pady=(0, 12))

        ctk.CTkLabel(progress_card, text="Прогресс").pack(anchor="w", padx=16, pady=(14, 6))

        self.progress = ctk.CTkProgressBar(progress_card, height=16)
        self.progress.pack(fill="x", padx=16)
        self.progress.set(0)

        stats = ctk.CTkFrame(progress_card, fg_color="transparent")
        stats.pack(fill="x", padx=16, pady=(10, 14))

        self.progress_label = ctk.CTkLabel(stats, textvariable=self.progress_var)
        self.progress_label.pack(side="left")

        self.speed_label = ctk.CTkLabel(stats, textvariable=self.speed_var, text_color="#A9B1BD")
        self.speed_label.pack(side="left", padx=18)

        self.eta_label = ctk.CTkLabel(stats, textvariable=self.eta_var, text_color="#A9B1BD")
        self.eta_label.pack(side="left", padx=18)

        self.size_label = ctk.CTkLabel(stats, textvariable=self.size_var, text_color="#A9B1BD")
        self.size_label.pack(side="right")

        action_card = ctk.CTkFrame(body, corner_radius=18)
        action_card.pack(fill="x", padx=18, pady=(0, 18))

        actions = ctk.CTkFrame(action_card, fg_color="transparent")
        actions.pack(fill="x", padx=16, pady=16)

        self.download_btn = ctk.CTkButton(
            actions,
            text="⬇ Скачать",
            height=44,
            command=self.start_download,
        )
        self.download_btn.pack(side="left")

        self.clipboard_check_btn = ctk.CTkButton(
            actions,
            text="Проверить ссылку",
            height=44,
            fg_color="#3A3F4B",
            hover_color="#4A5160",
            command=self.validate_current_url,
        )
        self.clipboard_check_btn.pack(side="left", padx=10)

    def choose_folder(self) -> None:
        folder = filedialog.askdirectory(initialdir=self.folder_var.get() or str(DOWNLOADS_DIR))
        if folder:
            self.folder_var.set(folder)

    def paste_from_clipboard(self) -> None:
        try:
            text = self.clipboard_get()
        except TclError:
            messagebox.showwarning(APP_NAME, "Буфер обмена пуст или недоступен.")
            return

        url = extract_youtube_url(text)
        if not url or not is_youtube_url(url):
            messagebox.showwarning(APP_NAME, "Буфер обмена не содержит ссылку YouTube.")
            return

        self.url_var.set(url)
        self.status_var.set("Ссылка вставлена из буфера обмена.")

    def validate_current_url(self) -> None:
        url = extract_youtube_url(self.url_var.get())
        if not url or not is_youtube_url(url):
            messagebox.showwarning(APP_NAME, "Ссылка не похожа на YouTube.")
            return

        self.url_var.set(url)
        self.status_var.set("Ссылка валидна.")

    def clear_all(self) -> None:
        self.url_var.set("")
        self.title_var.set("Название: —")
        self.status_var.set("Готов к загрузке")
        self.progress_var.set("0%")
        self.speed_var.set("—")
        self.eta_var.set("—")
        self.size_var.set("—")
        self.progress.set(0)

    def _save_ui_state(self) -> None:
        self.settings.last_folder = self.folder_var.get().strip() or str(DOWNLOADS_DIR)
        self.settings.mode = self.mode_var.get().strip() or "Video"
        self.settings.quality = self.quality_var.get().strip() or "Best"
        save_settings(self.settings)

    def _has_internet(self) -> bool:
        try:
            socket.gethostbyname("youtube.com")
            return True
        except OSError:
            return False

    def _has_ffmpeg(self) -> bool:
        return FFMPEG_PATH.exists()

    def start_download(self) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(APP_NAME, "Загрузка уже идёт.")
            return

        url = extract_youtube_url(self.url_var.get())
        folder = self.folder_var.get().strip()
        mode = self.mode_var.get().strip()
        quality = self.quality_var.get().strip()

        if not url or not is_youtube_url(url):
            messagebox.showwarning(APP_NAME, "Вставь нормальную ссылку YouTube.")
            return

        if not folder:
            messagebox.showwarning(APP_NAME, "Укажи папку сохранения.")
            return

        if not self._has_internet():
            messagebox.showerror(APP_NAME, "Интернет-соединение недоступно.")
            return

        if not self._has_ffmpeg():
            messagebox.showerror(
                APP_NAME,
                "FFmpeg не найден.\nПоложи ffmpeg.exe и ffprobe.exe в папку ffmpeg.",
            )
            return

        try:
            Path(folder).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Не удалось создать папку сохранения:\n{exc}")
            return

        self._save_ui_state()

        self.download_btn.configure(state="disabled")
        self.status_var.set("Подготовка...")
        self.progress_var.set("0%")
        self.speed_var.set("—")
        self.eta_var.set("—")
        self.size_var.set("—")
        self.progress.set(0)

        self.worker = threading.Thread(
            target=self._download_worker,
            args=(url, folder, mode, quality),
            daemon=True,
        )
        self.worker.start()

    def _download_worker(self, url: str, folder: str, mode: str, quality: str) -> None:
        def hook(d: dict) -> None:
            status = d.get("status")

            if status == "downloading":
                downloaded = d.get("downloaded_bytes") or 0
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                percent = (downloaded / total * 100) if total else 0.0

                speed = d.get("speed")
                eta = d.get("eta")

                speed_text = f"{format_bytes(speed)}/s" if speed else "—"
                eta_text = format_time(eta)

                self.events.put(("progress", float(percent)))
                self.events.put(("status", f"Скачивание... {percent:.1f}%"))
                self.events.put(("speed", speed_text))
                self.events.put(("eta", eta_text))
                self.events.put(("size", f"{format_bytes(downloaded)} / {format_bytes(total)}"))

            elif status == "finished":
                self.events.put(("status", "Скачивание завершено. Обработка файла..."))
                self.events.put(("progress", 100.0))

        try:
            self.events.put(("status", "Получаю информацию о видео..."))
            info = self.downloader.get_info(url)
            title = info.get("title") or "Без названия"
            self.events.put(("title", f"Название: {title}"))
            self.events.put(("status", "Начинаю загрузку..."))

            self.downloader.download(
                url=url,
                folder=folder,
                mode=mode,
                quality=quality,
                progress_hook=hook,
            )

            self.events.put(("done", "Готово. Файл сохранён."))
        except DownloadError as exc:
            self.logger.error("Download error: %s", exc)
            self.events.put(("error", str(exc)))
        except Exception as exc:
            self.logger.exception("Unexpected error during download")
            self.events.put(("error", f"Непредвиденная ошибка: {exc}"))

    def _schedule_poll(self) -> None:
        self._poll_after_id = self.after(UI_REFRESH_MS, self._poll_events)

    def _poll_events(self) -> None:
        if self._closing:
            return

        try:
            while True:
                event, payload = self.events.get_nowait()

                if event == "progress":
                    value = max(0.0, min(100.0, float(payload)))
                    self.progress.set(value / 100.0)
                    self.progress_var.set(f"{value:.1f}%")

                elif event == "status":
                    self.status_var.set(str(payload))

                elif event == "title":
                    self.title_var.set(str(payload))

                elif event == "speed":
                    self.speed_var.set(f"Скорость: {payload}")

                elif event == "eta":
                    self.eta_var.set(f"ETA: {payload}")

                elif event == "size":
                    self.size_var.set(str(payload))

                elif event == "done":
                    self.status_var.set(str(payload))
                    self.download_btn.configure(state="normal")
                    messagebox.showinfo(APP_NAME, str(payload))

                elif event == "error":
                    self.download_btn.configure(state="normal")
                    self.status_var.set("Ошибка загрузки")
                    messagebox.showerror(APP_NAME, f"Не удалось скачать видео:\n{payload}")

        except queue.Empty:
            pass

        self._schedule_poll()

    def _on_close(self) -> None:
        self._closing = True
        self._save_ui_state()

        if self._poll_after_id is not None:
            try:
                self.after_cancel(self._poll_after_id)
            except TclError:
                pass
            self._poll_after_id = None

        self.destroy()
