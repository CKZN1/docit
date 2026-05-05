import logging
import os

log = logging.getLogger(__name__)


def transcribe(audio_path):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        log.warning("OPENAI_API_KEY is not set in this process's environment")
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        with open(audio_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
            )
        return result.text
    except Exception:
        log.exception("Transcription request failed")
        return None
