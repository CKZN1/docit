import threading

from pynput import keyboard

from docit.app import DocItApp

app = DocItApp()


def on_screenshot():
    app._do_screenshot()


def on_audio():
    app._do_audio()


hotkeys = keyboard.GlobalHotKeys({
    "<cmd>+<shift>+s": on_screenshot,
    "<cmd>+<shift>+a": on_audio,
})


def main():
    hotkeys.start()
    app.run()


if __name__ == "__main__":
    main()
