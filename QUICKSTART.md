# Cortex Desktop Assistant – Quickstart

Get up and running with your own AI-powered, voice-enabled desktop assistant in just a few steps!

---

## 1. Unzip the Release

Extract all files from the provided zip archive into your desired project directory.

---

## 2. Prepare Your Configuration

**a. Create Your `.env` File**

- Copy `.env.example` to `.env`
- Open `.env` and fill in your actual API keys:

  ```
  GOOGLE_APPLICATION_CREDENTIALS=google_creds.json
  BRAVE_API_KEY=your_brave_api_key_here
  GROQ_API_KEY=your_groq_api_key_here
  GROQ_MODEL=llama3-8b-8192
  ```

**b. Create Your `config.yaml`**

- Copy `config.yaml.example` to `config.yaml`
- (Optional) Edit `config.yaml` to customize voice, mode (CLI or wake), and persona details.

---

## 3. Set Up Your Python Environment

It’s recommended to use a virtual environment:

```sh
python -m venv gda-venv
gda-venv\Scripts\activate
```

---

## 4. Install Dependencies

```sh
pip install -r requirements.txt
```

---

## 5. Run the Assistant

- Double-click `run_cortex_assistant_final.bat` (Windows)
- Or, from your activated venv:

  ```sh
  python main.py
  ```

---

## 6. Troubleshooting

- If you see any errors, check that your `.env` and `config.yaml` are correctly filled.
- Errors will be logged to `fatal_error.log` for debugging.

---

Enjoy your Cortex Desktop Assistant!

---
