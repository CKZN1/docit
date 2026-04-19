import os
from datetime import datetime

from docit.config import OUTPUT_DIR


class Session:
    def __init__(self, name=None):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        folder_name = f"{date_str}_{name}" if name else date_str
        self.folder = os.path.join(OUTPUT_DIR, folder_name)
        self.assets_dir = os.path.join(self.folder, "assets")
        self.md_path = os.path.join(self.folder, "session.md")

        os.makedirs(self.assets_dir, exist_ok=True)

        display_name = name if name else "Untitled"
        header = f"# Meeting: {display_name} - {date_str}\n\n"
        with open(self.md_path, "w") as f:
            f.write(header)

    def add_screenshot(self, image_path):
        filename = os.path.basename(image_path)
        timestamp = datetime.now().strftime("%H:%M")
        entry = f"## {timestamp} - Screenshot\n![](assets/{filename})\n\n"
        self._append(entry)

    def add_audio(self, audio_path, duration, transcript=None):
        filename = os.path.basename(audio_path)
        timestamp = datetime.now().strftime("%H:%M")
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        dur_str = f"{minutes}:{seconds:02d}"
        entry = f"## {timestamp} - Audio Clip ({dur_str})\n[audio](assets/{filename})\n\n"
        if transcript:
            entry += f"> {transcript}\n\n"
        self._append(entry)

    def _append(self, text):
        with open(self.md_path, "a") as f:
            f.write(text)
