import atexit
import logging
import os
import threading

import rumps

from docit.capture import take_screenshot
from docit.config import OUTPUT_DIR, PERSONA_FILE, WATCHER_SCRIPT
from docit.live import answer_transcript
from docit.personas import DEFAULT_PERSONA, PERSONAS
from docit.recorder import AudioRecorder
from docit.session import Session
from docit.transcriber import transcribe
from docit.watcher import LiveWatcher

log = logging.getLogger("docit")


class DocItApp(rumps.App):
    def __init__(self):
        super().__init__("DocIt", title="DocIt")
        self.session = None
        self.recorder = None
        self.watcher = LiveWatcher(WATCHER_SCRIPT, OUTPUT_DIR)
        atexit.register(self.watcher.stop)

        self.live_enabled_item = rumps.MenuItem("Enabled", callback=self.toggle_live_mode)
        self.persona_items = {
            name: rumps.MenuItem(name, callback=self.select_persona)
            for name in PERSONAS
        }
        self.active_persona = DEFAULT_PERSONA
        self.persona_items[DEFAULT_PERSONA].state = 1
        self._write_persona(DEFAULT_PERSONA)

        live_mode_menu = rumps.MenuItem("AI Assistance")
        live_mode_menu.add(self.live_enabled_item)
        live_mode_menu.add(None)
        for name in PERSONAS:
            live_mode_menu.add(self.persona_items[name])

        self.menu = [
            rumps.MenuItem("New Session", callback=self.new_session),
            rumps.MenuItem("End Session", callback=self.end_session),
            None,
            rumps.MenuItem("Screenshot  (Shift+Ctrl+S)", callback=self.on_screenshot),
            rumps.MenuItem("Audio  (Shift+Ctrl+A)", callback=self.on_audio),
            None,
            live_mode_menu,
            None,
            rumps.MenuItem(f"Output: {OUTPUT_DIR}"),
        ]

    def toggle_live_mode(self, _):
        if self.watcher.is_running:
            self.watcher.stop()
            self.live_enabled_item.state = 0
        else:
            self.watcher.start()
            if self.watcher.is_running:
                self.live_enabled_item.state = 1
            else:
                rumps.alert(
                    title="AI Assistance failed to start",
                    message=f"Could not launch watcher.\nScript: {WATCHER_SCRIPT}\nSee /tmp/docit_watcher.log",
                )

    def select_persona(self, sender):
        name = sender.title
        if name not in PERSONAS:
            return
        self.persona_items[self.active_persona].state = 0
        self.active_persona = name
        self.persona_items[name].state = 1
        self._write_persona(name)
        log.info("Persona set: %s", name)

    def _write_persona(self, name):
        os.makedirs(os.path.dirname(PERSONA_FILE), exist_ok=True)
        with open(PERSONA_FILE, "w") as f:
            f.write(PERSONAS[name])

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
            log.info("No transcription produced (see warnings above)")
        session.add_audio(audio_path, duration, transcript)

        if transcript and self.watcher.is_running:
            log.info("Asking Claude for live answer to audio")
            answer = answer_transcript(transcript)
            if answer and "No actionable content" not in answer:
                session.append_live_answer(answer)
                log.info("Live answer appended (%d chars)", len(answer))
            else:
                log.info("No live answer produced")
