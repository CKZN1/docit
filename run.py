import logging
import os
import threading
import time

os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ.get("PATH", "")

from pynput import keyboard

from docit.app import DocItApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger("docit")

app = DocItApp()


def _safe(fn):
    def wrapped():
        try:
            fn()
        except Exception:
            log.exception("Hotkey callback failed")
    return wrapped


def _run_hotkeys():
    while True:
        listener = keyboard.GlobalHotKeys({
            "<shift>+<ctrl>+s": _safe(app._do_screenshot),
            "<shift>+<ctrl>+a": _safe(app._do_audio),
        })
        try:
            listener.start()
            listener.join()
        except Exception:
            log.exception("Hotkey listener crashed")
        log.warning("Hotkey listener stopped — restarting")
        time.sleep(0.5)


def main():
    threading.Thread(target=_run_hotkeys, daemon=True).start()
    app.run()


if __name__ == "__main__":
    main()
