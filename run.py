import logging
import threading

from pynput import keyboard

from docit.app import DocItApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

app = DocItApp()


def on_screenshot():
    app._do_screenshot()


def on_audio():
    app._do_audio()


hotkeys = keyboard.GlobalHotKeys({
    "<shift>+<ctrl>+s": on_screenshot,
    "<shift>+<ctrl>+a": on_audio,
})


def main():
    hotkeys.start()
    app.run()


if __name__ == "__main__":
    main()
