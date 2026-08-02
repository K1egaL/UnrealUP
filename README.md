# UnrealUP

<p align="center">
  <img src="assets/logo.png" alt="UnrealUP Logo" width="128">
</p>

<p align="center">
  <b>Fast, lightweight and modern YouTube downloader for Windows.</b>
</p>

<p align="center">
  Download videos and audio from YouTube with a clean interface built using Python and CustomTkinter.
</p>

---

## Features

* Modern Windows 11 inspired interface
* Download video and audio
* Multiple quality options
* Clipboard URL detection
* Download progress
* Download speed
* ETA
* File size information
* Automatic settings saving
* Logging system
* FFmpeg support
* Threaded downloading (UI never freezes)

---

## Screenshots

Screenshots will be added after the first stable release.

---

## Requirements

* Python 3.11 or newer
* FFmpeg
* Windows 10 / Windows 11

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/UnrealUP.git
cd UnrealUP
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## FFmpeg

Place the following files into the `ffmpeg` folder:

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

## Project Structure

```text
UnrealUP/
│
├── assets/
├── downloads/
├── ffmpeg/
├── logs/
│
├── config.py
├── downloader.py
├── logger.py
├── main.py
├── settings.py
├── styles.py
├── ui.py
├── utils.py
├── widgets.py
│
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── README.md
├── LICENSE
└── SECURITY.md
```

---

## Development

Install development tools:

```bash
pip install -r requirements-dev.txt
```

Run Ruff:

```bash
ruff check .
```

Run MyPy:

```bash
mypy .
```

Compile the project:

```bash
python -m compileall .
```

---

## Roadmap

### v0.2

* Better Fluent Design
* Video thumbnail preview
* Playlist support
* Download queue
* Drag & Drop
* Automatic FFmpeg detection
* Automatic yt-dlp update check
* Better error reporting

### v0.3

* Multiple downloads
* History
* Download scheduler
* Theme customization

---

## Security

Please report vulnerabilities privately.

See **SECURITY.md**.

---

## License

This project is licensed under the MIT License.

See **LICENSE** for details.
