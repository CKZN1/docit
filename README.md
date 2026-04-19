# DocIt

A macOS menu bar app for capturing screenshots and audio (including transcriptions) during meetings, saving everything as markdown notes you can open in Obsidian.

## Features

- Menu bar app with global hotkeys
- Screenshot capture (Shift+Ctrl+S)
- Audio recording with toggle (Shift+Ctrl+A)
- Auto-transcription via OpenAI Whisper (optional)
- Outputs markdown with embedded assets, ready for Obsidian

## Requirements

- macOS
- Python 3.10+
- PortAudio (`brew install portaudio`)
- ffmpeg (`brew install ffmpeg`)

## Installation

1. Install system dependencies:
   ```bash
   brew install portaudio ffmpeg
   ```

2. Clone the repo:
   ```bash
   git clone https://github.com/CKZN1/docit.git
   cd docit
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Set the output directory (point it at your Obsidian vault or any folder):
   ```bash
   echo 'export DOCIT_OUTPUT_DIR="$HOME/Documents/Obsidian Vault/DocIt"' >> ~/.zshrc
   source ~/.zshrc
   ```

5. (Optional) Enable auto-transcription:
   ```bash
   echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
   source ~/.zshrc
   ```

6. Grant Accessibility permission to your terminal app:
   - **System Settings > Privacy & Security > Accessibility**
   - Add and enable your terminal (Terminal.app, iTerm, VS Code, etc.)

7. Grant Microphone permission when prompted on first audio recording.

## Usage

```bash
source venv/bin/activate
python run.py
```

A **DocIt** icon appears in your menu bar. Use the menu or hotkeys:

| Action | Hotkey |
|---|---|
| Screenshot | Shift+Ctrl+S |
| Start/Stop Audio | Shift+Ctrl+A |

You can also click **New Session** in the menu to name your session, or **End Session** to finish.

## Output

Sessions are saved to the `DOCIT_OUTPUT_DIR` directory (defaults to `~/DocIt` if not set):

```
DocIt/
  2025-04-19_standup/
    session.md
    assets/
      screenshot_143022.png
      audio_143500.mp3
```

The `session.md` file contains timestamped entries with embedded screenshots, audio links, and transcriptions.

## Transcription

If `OPENAI_API_KEY` is set, audio recordings are automatically transcribed using OpenAI Whisper and the transcript is added as a blockquote in the session markdown. If the key is not set or the API call fails, audio is saved normally without transcription.

## License

MIT
