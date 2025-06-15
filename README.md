# 🧠 Cortex Desktop Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful, modular, and extensible voice assistant for Windows, macOS, and Linux. Features real-time voice recognition, multiple TTS engine support, web search, and LLM integration (via Groq API).

## ✨ Features

- **Multiple TTS Engines**: Choose between Google TTS, Microsoft Edge TTS, or Chatterbox TTS
- **Voice & CLI Interaction**: Seamless voice and text-based interaction
- **Wake Word Detection**: Always-on listening with configurable wake word
- **Web Search**: Integrated Brave web search for real-time information
- **Modular Architecture**: Easy to extend with new features and integrations
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Configurable**: Customize voice, behavior, and appearance via `config.yaml`
- **Logging**: Comprehensive logging for debugging and monitoring

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- FFmpeg (required for audio processing)
- A Groq API key (sign up at [Groq Cloud](https://groq.com/))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/cortex-desktop-assistant.git
   cd cortex-desktop-assistant
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration:**
   ```bash
   # Copy the example config file
   copy config.yaml.example config.yaml
   
   # Copy the example environment file
   copy .env.example .env
   ```

5. **Edit the configuration files:**
   - Update `.env` with your API keys
   - Modify `config.yaml` to customize the assistant's behavior

## 🎯 Usage

### Running the Assistant

```bash
# Start in CLI mode (default)
python main.py

# Start in wake word mode
python main.py --mode wake

# Test TTS engines
python test_tts.py --engine all
```

### Voice Commands

- **Wake Word**: Say "Hey Cortex" to activate (configurable)
- **Search**: "Search for [query]" or "Look up [query]"
- **Exit**: Say "Goodbye" or "Shutdown" to exit

## ⚙️ Configuration

Edit `config.yaml` to customize:

- Voice settings (engine, voice ID, speaking rate)
- Wake word and shutdown phrase
- Logging verbosity
- Web search preferences

Example configuration:

```yaml
# Voice configuration
voice:
  engine: edge  # Options: edge, google, chatterbox
  id: en-US-AriaNeural  # Voice ID (varies by engine)
  rate: 1.0  # Speaking rate (0.5 to 2.0)
  intro_line: "Cortex online and ready."
  enabled: true

# Wake word configuration
wake_word: "hey cortex"
shutdown_word: "shutdown"

# Application mode (cli or wake)
mode: cli
```

## 🛠️ Building a Standalone Executable

Build a single-file executable using PyInstaller:

```bash
# Install PyInstaller if needed
pip install pyinstaller

# Build the executable
pyinstaller --noconfirm --onefile \
  --add-data "config.yaml;." \
  --add-data ".env;." \
  --add-data "google_creds.json;." \
  --name "CortexAssistant" \
  main.py
```

The executable will be in the `dist` directory.

## 🧪 Testing

Run the test suite to verify all components:

```bash
# Run all tests
pytest

# Test specific TTS engine
python test_tts.py --engine edge
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 Documentation

For detailed documentation, please see the [docs](docs/) directory.

---

💡 **Tip**: For the best experience, use a high-quality microphone and ensure you're in a quiet environment when using voice commands.

See `ROADMAP.md` for upcoming features!
