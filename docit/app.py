import logging
import threading

import rumps

from docit.capture import take_screenshot
from docit.config import OUTPUT_DIR
from docit.recorder import AudioRecorder
from docit.session import Session
from docit.transcriber import transcribe

log = logging.getLogger("docit")


class DocItApp(rumps.App):
    def __init__(self):
        super().__init__("DocIt", title="DocIt")
        self.session = None
        self.recorder = None

        self.menu = [
            rumps.MenuItem("New Session", callback=self.new_session),
            rumps.MenuItem("End Session", callback=self.end_session),
            None,
            rumps.MenuItem("Screenshot  (Shift+Ctrl+S)", callback=self.on_screenshot),
            rumps.MenuItem("Audio  (Shift+Ctrl+A)", callback=self.on_audio),
            None,
            rumps.MenuItem(f"Output: {OUTPUT_DIR}"),
        ]

    def _ensure_session(self):
        if self.session is None:
            self.session = Session()
            self.recorder = AudioRecorder(self.session.assets_dir)
            log.info("Auto-started session: %s", self.session.folder)

    @rumps.clicked("New Session")
    def new_session(self, _):
        window = rumps.Window(
            message="Enter a session name (or leave blank):",
            title="New Session",
            default_text="",
            ok="Create",
            cancel="Cancel",
        )
        response = window.run()
        if response.clicked:
            name = response.text.strip() or None
            self.session = Session(name)
            self.recorder = AudioRecorder(self.session.assets_dir)
            self.title = "DocIt"
            log.info("New session: %s", self.session.folder)

    @rumps.clicked("End Session")
    def end_session(self, _):
        if self.session is None:
            return

        if self.recorder and self.recorder.is_recording:
            audio_path, duration = self.recorder.stop()
            if audio_path:
                transcript = transcribe(audio_path)
                self.session.add_audio(audio_path, duration, transcript)

        folder = self.session.folder
        self.session = None
        self.recorder = None
        self.title = "DocIt"
        log.info("Session ended: %s", folder)

    @rumps.clicked("Screenshot  (Shift+Ctrl+S)")
    def on_screenshot(self, _):
        self._do_screenshot()

    def _do_screenshot(self):
        log.info("Screenshot hotkey pressed")
        self._ensure_session()
        threading.Thread(target=self._capture_screenshot, daemon=True).start()

    def _capture_screenshot(self):
        path = take_screenshot(self.session.assets_dir)
        if path:
            self.session.add_screenshot(path)
            log.info("Screenshot saved: %s", path)
        else:
            log.warning("Screenshot failed or was cancelled")

    @rumps.clicked("Audio  (Shift+Ctrl+A)")
    def on_audio(self, _):
        self._do_audio()

    def _do_audio(self):
        self._ensure_session()

        if self.recorder and self.recorder.is_recording:
            log.info("Stopping audio recording")
            audio_path, duration = self.recorder.stop()
            if audio_path:
                log.info("Audio saved: %s (%.1fs)", audio_path, duration)
                session = self.session
                threading.Thread(
                    target=self._transcribe_and_save,
                    args=(session, audio_path, duration),
                    daemon=True,
                ).start()
            else:
                log.warning("Audio recording produced no output")
            self.title = "DocIt"
        else:
            log.info("Starting audio recording")
            self.recorder.start()
            self.title = "DocIt [REC]"

    def _transcribe_and_save(self, session, audio_path, duration):
        log.info("Transcribing %s", audio_path)
        transcript = transcribe(audio_path)
        if transcript:
            log.info("Transcription complete (%d chars)", len(transcript))
        else:
            log.info("No transcription (no API key or failed)")
        session.add_audio(audio_path, duration, transcript)
