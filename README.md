# rssWatcher

`rssWatcher` is an automated system for monitoring, cleaning, organizing, and publishing worship practice audio recordings (MP3) via a podcast-compatible RSS feed. It is designed to operate continuously in the background, detect new practice files, tag them with ID3 metadata, clean invalid files, and regenerate a browsable HTML index and podcast feed.

---

## 📦 Features

- Automatically watches for new MP3 uploads in practice folders using `inotifywait`
- Cleans files based on duration and applies ID3 tags using `mutagen`
- Dynamically generates `rss_feed.xml` in podcast-compatible format
- Builds `index.html` for human browsing
- Automatically creates folder structure for upcoming Friday practices

---

## 🚀 Installation

### 🔧 Requirements

- Python 3 with `mutagen` installed:
  ```bash
  pip install mutagen
  ```

- Linux utilities: `bash`, `inotify-tools`

### 📁 Directory Structure

This system expects:

```
/var/www/band.fccsv.com/
├── audio/
│   └── practice-YYYY-MM-DD/
├── rss_feed.xml
└── index.html
```

Ensure this directory is writable by the user running the monitor.

### 📥 Setup

1. **Copy the Scripts**

Place the following scripts in `/usr/local/bin/` or a similar location:

- `monitor_audio.sh`
- `PodcastFeedGen.py`
- `cleanMP3.py`
- `folderCreate.sh`

2. **Make Executable**

```bash
chmod +x /usr/local/bin/*.sh /usr/local/bin/*.py
```

3. **Run Folder Bootstrap**

```bash
bash /usr/local/bin/folderCreate.sh
```

4. **Start the Monitor**

```bash
nohup /usr/local/bin/monitor_audio.sh &
```

Or use a service manager like `systemd`.

---

## 🔍 Usage

Once running, the system will:

- Watch for `.mp3` file saves
- Wait 5 minutes after last write before processing
- Tag valid MP3s, delete invalid ones
- Regenerate `rss_feed.xml` and `index.html`

Feed will be accessible at:

```
https://band.fccsv.com/rss_feed.xml
```

---

## 📄 License

This project is licensed under the terms of the included `LICENSE` file.
