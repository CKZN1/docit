# DocIt

A macOS menu bar app for capturing screenshots and audio (including transcriptions) during meetings, saving everything as markdown notes you can open in Obsidian.

## Features

- Menu bar app with global hotkeys
- Screenshot capture (Cmd+Shift+S)
- Audio recording with toggle (Cmd+Shift+A)
- Auto-transcription via OpenAI Whisper (optional)
- Outputs markdown with embedded assets, ready for Obsidian

## Requirements

- macOS
- Python 3.10+
- PortAudio (`brew install portaudio`)

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/docit.git
   cd docit
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Grant Accessibility permission to your terminal app:
   - **System Settings > Privacy & Security > Accessibility**
   - Add and enable your terminal (Terminal.app, iTerm, VS Code, etc.)

4. Grant Microphone permission when prompted on first audio recording.

## Usage

```bash
source venv/bin/activate
python run.py
```

A **DocIt** icon appears in your menu bar. Use the menu or hotkeys:

| Action | Hotkey |
|---|---|
| Screenshot | Cmd+Shift+S |
| Start/Stop Audio | Cmd+Shift+A |

You can also click **New Session** in the menu to name your session, or **End Session** to finish.

## Output

Sessions are saved to `~/DocIt` by default:

```
~/DocIt/
  2025-04-19_standup/
    session.md
    assets/
      screenshot_143022.png
      audio_143500.wav
```

The `session.md` file contains timestamped entries with embedded screenshots and audio links.

### Change output directory

Set the `DOCIT_OUTPUT_DIR` environment variable:

```bash
export DOCIT_OUTPUT_DIR="$HOME/Documents/Obsidian Vault/DocIt"
```

Add this to your `~/.zshrc` to make it permanent.

## Obsidian Integration

Point the output directory into your Obsidian vault and sessions appear automatically in the sidebar. The markdown uses standard image and link syntax that Obsidian renders natively.

## Transcription (Optional)

If you set an OpenAI API key, audio recordings are automatically transcribed using Whisper and the transcript is added as a blockquote in the session markdown.

```bash
export OPENAI_API_KEY="sk-..."
```

If the key is not set or the API call fails, audio is saved normally without transcription.

## License

MIT
