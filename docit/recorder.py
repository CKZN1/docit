import os
import threading
import time
from datetime import datetime

import numpy as np
import sounddevice as sd
import soundfile as sf

from docit.config import AUDIO_CHANNELS, AUDIO_SAMPLE_RATE


class AudioRecorder:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self._frames = []
        self._stream = None
        self._recording = False
        self._start_time = None
        self._lock = threading.Lock()

    @property
    def is_recording(self):
        return self._recording

    def _callback(self, indata, frames, time_info, status):
        with self._lock:
            if self._recording:
                self._frames.append(indata.copy())

    def start(self):
        self._frames = []
        self._recording = True
        self._start_time = time.time()
        self._stream = sd.InputStream(
            samplerate=AUDIO_SAMPLE_RATE,
            channels=AUDIO_CHANNELS,
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
            if not self._frames:
                return None, 0
            audio_data = np.concatenate(self._frames, axis=0)

        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"audio_{timestamp}.wav"
        filepath = os.path.join(self.save_dir, filename)

        sf.write(filepath, audio_data, AUDIO_SAMPLE_RATE)

        self._frames = []
        self._start_time = None
        return filepath, duration
