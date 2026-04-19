import logging
import os
import subprocess
import tempfile
import threading
import time
from datetime import datetime

import sounddevice as sd
import soundfile as sf

from docit.config import AUDIO_CHANNELS, AUDIO_SAMPLE_RATE

log = logging.getLogger("docit")

STREAM_BLOCK_SIZE = 1024


class AudioRecorder:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self._stream = None
        self._writer = None
        self._tmp_path = None
        self._recording = False
        self._start_time = None
        self._lock = threading.Lock()

    @property
    def is_recording(self):
        return self._recording

    def _callback(self, indata, frames, time_info, status):
        with self._lock:
            if self._recording and self._writer:
                self._writer.write(indata.copy())

    def start(self):
        self._tmp_path = tempfile.mktemp(suffix=".wav", dir=self.save_dir)
        log.info("Recording to temp file: %s", self._tmp_path)
        self._writer = sf.SoundFile(
            self._tmp_path, mode="w",
            samplerate=AUDIO_SAMPLE_RATE,
            channels=AUDIO_CHANNELS,
            format="WAV", subtype="PCM_16",
        )
        self._recording = True
        self._start_time = time.time()
        self._stream = sd.InputStream(
            samplerate=AUDIO_SAMPLE_RATE,
            channels=AUDIO_CHANNELS,
            blocksize=STREAM_BLOCK_SIZE,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self):
        self._recording = False
        duration = time.time() - self._start_time if self._start_time else 0

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if self._writer:
                self._writer.close()
                self._writer = None

        if not self._tmp_path or not os.path.exists(self._tmp_path):
            return None, 0

        timestamp = datetime.now().strftime("%H%M%S")
        mp3_filename = f"audio_{timestamp}.mp3"
        mp3_path = os.path.join(self.save_dir, mp3_filename)

        log.info("Converting to mp3: %s", mp3_path)
        self._convert_to_mp3(self._tmp_path, mp3_path)
        os.remove(self._tmp_path)
        self._tmp_path = None
        self._start_time = None

        return mp3_path, duration

    def _convert_to_mp3(self, wav_path, mp3_path):
        subprocess.run(
            ["ffmpeg", "-y", "-i", wav_path, "-ac", "1", "-ar",
             str(AUDIO_SAMPLE_RATE), "-b:a", "64k", mp3_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
