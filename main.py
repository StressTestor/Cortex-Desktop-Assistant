import sys
import traceback

def main():
    # --- Paste your ENTIRE current main.py code here (indented) ---
    import os
    import yaml
    import re
    from groq_engine import chat_with_groq
    from web_search import search_brave
    import speech_recognition as sr

    # (Rest of your main.py code goes here, everything indented!)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        with open("fatal_error.log", "w") as f:
            traceback.print_exc(file=f)
        # (Optional) Show a message box with error (Windows only)
        try:
            import ctypes
            error = traceback.format_exc()
            ctypes.windll.user32.MessageBoxW(
                0, "A fatal error occurred:\n\n" + error, "Fatal Error", 0
            )
        except Exception:
            pass

import os
import yaml
import sys
import re
from groq_engine import chat_with_groq
from web_search import search_brave
import speech_recognition as sr

# -- DYNAMIC TTS MODULE SELECTION --
voice_config = {}
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
voice_config = config.get("voice", {})
if voice_config.get("engine", "edge") == "google":
    from google_tts_module import speak
else:
    from edge_tts_module import speak

def preprocess_for_tts(text, engine="edge"):
    # Stage directions and asterisk actions
    def stage_replace(match):
        phrase = match.group(1).strip().lower()
        # Longer pause for explicit pauses
        if "pause" in phrase or "..." in phrase:
            return '<break time="800ms"/>' if engine == "google" else "..."
        # All other directions/actions: brief pause, not spoken
        return '<break time="600ms"/>' if engine == "google" else ""
    # Replace *action or stage direction* with pause
    text = re.sub(r"\*(.*?)\*", stage_replace, text)

    # Markdown bullet points (convert * or - bullets to "- ")
    text = re.sub(r"^\s*[\*\-]\s+", "- ", text, flags=re.MULTILINE)
    # Emphasis with underscores
    text = re.sub(r"\_(.*?)\_", r"\1", text)
    # Line breaks preserved
    text = text.replace('\n', '\n')
    # Wrap with <speak> for Google SSML if not already present
    if engine == "google" and not text.strip().startswith("<speak>"):
        text = f"<speak>{text}</speak>"
    return text

def speak_config(text):
    engine = voice_config.get("engine", "edge")
    clean_text = preprocess_for_tts(text, engine)
    speak(
        clean_text,
        voice=voice_config.get("id", "en-US-Wavenet-F"),
        speaking_rate=voice_config.get("rate", 1.0)
    )

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[Voice Input] Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, phrase_time_limit=8)
    try:
        text = recognizer.recognize_google(audio)
        print(f"[You said]: {text}")
        return text
    except Exception:
        print("Sorry, I didn't catch that.")  # Prints only
        return ""

def wake_mode(config):
    recognizer = sr.Recognizer()
    WAKE_PHRASE = config.get("wake_word", "hey cortex").lower()
    SHUTDOWN_PHRASE = config.get("shutdown_word", "shutdown").lower()

    print(f"[Wake Mode] Listening for wake word: '{WAKE_PHRASE}'")
    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, phrase_time_limit=5)
            try:
                transcript = recognizer.recognize_google(audio).lower()
                print(f"[Heard]: {transcript}")
                if SHUTDOWN_PHRASE in transcript or "goodbye" in transcript:
                    print("[Wake Mode] Shutdown command received in passive phase.")
                    speak_config("Shutting down.")
                    break
                if WAKE_PHRASE in transcript:
                    print("Wake word detected. Entering active mode. Say 'shutdown' or 'goodbye' to exit.")
                    # Stay in active mode until shutdown/goodbye
                    while True:
                        with sr.Microphone() as source:
                            recognizer.adjust_for_ambient_noise(source, duration=0.3)
                            print("Awaiting command...")
                            command_audio = recognizer.listen(source, phrase_time_limit=10)
                        try:
                            user_input = recognizer.recognize_google(command_audio).lower()
                            print(f"[You said]: {user_input}")

                            # Exit active mode on shutdown/goodbye
                            if SHUTDOWN_PHRASE in user_input or "goodbye" in user_input:
                                print("[Active Mode] Shutdown or goodbye received. Returning to passive listening.")
                                speak_config("Shutting down.")
                                break

                            # Web search detection (Wake)
                            triggers = ["search for ", "look up ", "find "]
                            lowered = user_input.lower()
                            if any(lowered.startswith(t) for t in triggers):
                                for t in triggers:
                                    if lowered.startswith(t):
                                        query = user_input[len(t):].strip()
                                        break
                                result = search_brave(query)
                                print(f"Web: {result}")
                                speak_config(result)
                                continue

                            reply = chat_with_groq(user_input)
                            print(f"Groq: {reply}")
                            speak_config(reply)
                        except sr.UnknownValueError:
                            print("[Command Phase] Could not understand input.")
                            print("Sorry, I didn't catch that.")  # Print only
                        except sr.RequestError as e:
                            print(f"[Command Phase Error]: {e}")
                            print("There was a problem reaching the recognition service.")
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"[Passive Phase Error]: {e}")
        except KeyboardInterrupt:
            print("\n[Wake Mode] Interrupted.")
            speak_config("Goodbye.")
            break

def cli_mode():
    print("🧠 Groq Assistant - Core Edition (TTS: {})".format(voice_config.get("engine", "edge").capitalize()))
    print("Type 'exit' to quit. Type 'listen' to speak.")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            speak_config("Goodbye!")
            break
        elif user_input.lower() == "listen":
            user_input = listen()
            if not user_input:
                continue
        elif not user_input:
            continue

        # Web search detection (CLI)
        triggers = ["search for ", "look up ", "find "]
        lowered = user_input.lower()
        if any(lowered.startswith(t) for t in triggers):
            for t in triggers:
                if lowered.startswith(t):
                    query = user_input[len(t):].strip()
                    break
            result = search_brave(query)
            print(f"Web: {result}")
            speak_config(result)
            continue

        reply = chat_with_groq(user_input)
        print(f"Groq: {reply}")
        speak_config(reply)

if __name__ == "__main__":
    # config is already loaded above for TTS selection
    mode = config.get("mode", "cli").lower()
    # Print intro only (no TTS)
    if config.get("voice", {}).get("enabled", True):
        print(config["voice"].get("intro_line", "Cortex online and ready."))
    if mode == "wake":
        wake_mode(config)
    else:
        cli_mode()
