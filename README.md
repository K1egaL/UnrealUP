![Python](https://img.shields.io/badge/Python-3.11+-blue)

![License](https://img.shields.io/github/license/K1egaL/UnrealUP)

![GitHub Release](https://img.shields.io/github/v/release/K1egaL/UnrealUP)

![Downloads](https://img.shields.io/github/downloads/K1egaL/UnrealUP/total)

![CodeQL](https://github.com/K1egaL/UnrealUP/actions/workflows/codeql.yml/badge.svg)

![Python CI](https://github.com/K1egaL/UnrealUP/actions/workflows/python.yml/badge.svg)

# UnrealUP

🇷🇺 **Русский** | [🇬🇧 English](#english)

---

# 🇷🇺 Русский

## UnrealUP

Современное, лёгкое и быстрое приложение для скачивания видео и аудио с YouTube.

Разработано на **Python + CustomTkinter** с интерфейсом в стиле Windows 11.

---

## Возможности

- 🎬 Скачивание видео
- 🎵 Скачивание аудио
- ⚡ Высокая скорость
- 📋 Вставка ссылки из буфера обмена
- 📈 Отображение прогресса
- 🚀 Потоковая загрузка без зависания интерфейса
- 💾 Автоматическое сохранение настроек
- 📝 Логирование ошибок
- 🖥 Современный интерфейс

---

## Установка

Клонируйте репозиторий:

```bash
git clone https://github.com/K1egaL/UnrealUP.git
cd UnrealUP
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

---

## FFmpeg

**UnrealUP не включает FFmpeg в репозиторий.**

Это сделано для уменьшения размера проекта и соблюдения принципов распространения сторонних компонентов.

Скачайте FFmpeg самостоятельно с официального сайта:

https://ffmpeg.org/download.html

После скачивания поместите файлы

```text
ffmpeg.exe
ffprobe.exe
```

в папку

```text
ffmpeg/
```

Структура должна выглядеть так:

```text
ffmpeg/
├── ffmpeg.exe
└── ffprobe.exe
```

---

## Запуск

```bash
python main.py
```

---

## Лицензия

Проект распространяется по лицензии MIT.

---

# English

## UnrealUP

A modern, lightweight and fast YouTube video & audio downloader.

Built with **Python + CustomTkinter** and inspired by the Windows 11 design language.

---

## Features

- 🎬 Download videos
- 🎵 Download audio
- ⚡ Fast downloads
- 📋 Clipboard URL detection
- 📈 Download progress
- 🚀 Responsive UI
- 💾 Automatic settings saving
- 📝 Logging
- 🖥 Modern interface

---

## Installation

Clone the repository:

```bash
git clone https://github.com/K1egaL/UnrealUP.git
cd UnrealUP
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## FFmpeg

**FFmpeg is NOT bundled with UnrealUP.**

To keep the repository lightweight and avoid redistributing third-party binaries, users must install FFmpeg manually.

Download FFmpeg from the official website:

https://ffmpeg.org/download.html

Then place

```text
ffmpeg.exe
ffprobe.exe
```

inside the

```text
ffmpeg/
```

directory:

```text
ffmpeg/
├── ffmpeg.exe
└── ffprobe.exe
```

---

## Run

```bash
python main.py
```

---

## License

Licensed under the MIT License.
