import os
import subprocess
from datetime import datetime


def take_screenshot(save_dir):
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(save_dir, filename)

    result = subprocess.run(["screencapture", filepath])

    if result.returncode == 0 and os.path.exists(filepath):
        return filepath
    return None
