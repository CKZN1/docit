import os

OUTPUT_DIR = os.path.expanduser(os.environ.get("DOCIT_OUTPUT_DIR", "~/DocIt"))

WATCHER_SCRIPT = os.path.expanduser(
    os.environ.get("DOCIT_WATCHER_SCRIPT", os.path.join(OUTPUT_DIR, "watch.sh"))
)

PERSONA_FILE = os.path.join(OUTPUT_DIR, ".docit_persona")

SCREENSHOT_HOTKEY = "<shift>+<ctrl>+s"
AUDIO_HOTKEY = "<shift>+<ctrl>+a"

AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
