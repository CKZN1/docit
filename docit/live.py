import logging
import os
import subprocess

from docit.config import PERSONA_FILE

log = logging.getLogger("docit")

PROMPT_TEMPLATE = """You are a live interview assistant. Be fast and concise — every second counts.

The user just said: "{transcript}"

If it contains a question, give the correct answer in 1-3 sentences max. Format:
> **Q:** <the question>

**A:** <short, direct answer>

If there's no question but useful content, summarize in one sentence.
If nothing useful, just say 'No actionable content detected.'

No lengthy explanations. No tables. Just the right answer, fast.
"""


def answer_transcript(transcript):
    prompt = PROMPT_TEMPLATE.format(transcript=transcript)
    cmd = ["claude", "-p", "--max-turns", "3"]
    if os.path.exists(PERSONA_FILE) and os.path.getsize(PERSONA_FILE) > 0:
        with open(PERSONA_FILE) as f:
            persona = f.read()
        cmd += ["--append-system-prompt", persona]
    try:
        result = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True, timeout=60,
        )
    except Exception:
        log.exception("Live answer subprocess failed")
        return None
    if result.returncode != 0:
        log.warning("claude returned %d: %s", result.returncode, result.stderr.strip()[:500])
        return None
    return result.stdout.strip()
