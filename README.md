# Cortex Desktop Assistant (powered by Groq)

A modular, sarcastic, voice-powered Python assistant for Windows. Features real-time voice recognition, persona-based interaction, web search, and pluggable LLM completion (via Groq API).

## Features
- Voice and CLI interaction (Google/Edge TTS)
- Persona-driven sarcasm & wit (configurable)
- Integrated Brave web search
- Wake word and passive/active modes
- Fully modular, easy to extend
- Packaged as EXE via PyInstaller, or run as Python scripts

## Getting Started

1. **Install Python 3.10+ and create a virtualenv:**
   ```sh
   python -m venv gda-venv
   gda-venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Copy `.env.example` to `.env` and fill in your API keys.**
3. **Copy `config.yaml.example` to `config.yaml` and tweak as desired.**
4. **Run with:**
   - `python main.py` (from your venv), or
   - `run_cortex_assistant_final.bat` (Windows)
   - Or build with PyInstaller for a single-file EXE.

## Building the EXE

Run:
```
pyinstaller --noconfirm --onefile --add-data "config.yaml;." --add-data ".env;." --add-data "google_creds.json;." main.py
```
Distribute the generated EXE with your config and keys.

## Usage

- CLI: Type questions/commands. Type `listen` for voice input. Type `exit` to quit.
- Wake Mode: Set `mode: "wake"` in `config.yaml` to enable always-on listening for the wake word (`hey cortex`).

## Security

**Never commit `.env` or `google_creds.json`!** All sensitive info is in `.gitignore` by default.

## License

MIT

---

See `ROADMAP.md` for upcoming features!
