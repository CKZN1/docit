import os
import subprocess
from datetime import datetime


def take_screenshot(save_dir):
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"screenshot_{timestamp}.jpg"
    filepath = os.path.join(save_dir, filename)

    result = subprocess.run(["screencapture", "-t", "jpg", filepath])

    if result.returncode == 0 and os.path.exists(filepath):
        return filepath
    return None
