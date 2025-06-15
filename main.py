"""
Cortex Desktop Assistant - Main Application

This is the main entry point for the Cortex Desktop Assistant,
a voice-enabled AI assistant with multiple TTS engine support.
"""

import os
import re
import sys
import logging
import traceback
import warnings
from typing import Optional, Dict, Any, Callable, Type, Union

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module='whisper.*')
warnings.filterwarnings("ignore", category=FutureWarning, module='whisper.*')
warnings.filterwarnings("ignore", category=UserWarning, module='torch.*')

# Local imports
try:
    from groq_engine import chat_with_groq
    from web_search import search_brave
    import speech_recognition as sr
    from logger import get_logger
    from config_utils import get_config, AppConfig
    
    # Import TTS modules with error handling
    try:
        from google_tts_module import speak as google_speak, GoogleTTSException
    except ImportError as e:
        google_speak = None
        google_error = str(e)
    
    try:
        from edge_tts_module import speak as edge_speak, EdgeTTSException
    except ImportError as e:
        edge_speak = None
        edge_error = str(e)
    
    try:
        from chatterbox_tts_module import speak as chatterbox_speak
    except ImportError as e:
        chatterbox_speak = None
        chatterbox_error = str(e)
        
except ImportError as e:
    # If we can't import our modules, log to stderr and exit
    print(f"Fatal error importing required modules: {e}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

# Initialize logger
logger = get_logger("cortex")

# Global configuration
config: AppConfig = get_config()

# TTS function mapping
TTS_ENGINES: Dict[str, Callable] = {
    "google": google_speak,
    "edge": edge_speak,
    "chatterbox": chatterbox_speak
}

# TTS error messages
TTS_ERRORS: Dict[str, str] = {
    "google": google_error if 'google_error' in locals() else "Google TTS not available",
    "edge": edge_error if 'edge_error' in locals() else "Edge TTS not available",
    "chatterbox": chatterbox_error if 'chatterbox_error' in locals() else "Chatterbox TTS not available"
}

# Select TTS engine based on config
try:
    engine = config.voice.engine.lower()
    speak = TTS_ENGINES.get(engine)
    
    if speak is None:
        logger.warning(
            "Configured TTS engine '%s' not found. Falling back to Edge TTS.", 
            engine
        )
        engine = "edge"
        speak = edge_speak or google_speak or chatterbox_speak
        
    if speak is None:
        raise RuntimeError("No TTS engine available. Please check your installation.")
        
    logger.info("Using TTS engine: %s", engine.upper())
    
except Exception as e:
    logger.critical("Failed to initialize TTS engine: %s", str(e), exc_info=True)
    # Try to use any available TTS as fallback
    speak = next((s for s in [edge_speak, google_speak, chatterbox_speak] if s is not None), None)
    if speak is None:
        logger.critical("No TTS engine available. Exiting.")
        sys.exit(1)
    from edge_tts_module import speak

def preprocess_for_tts(text: str, engine: Optional[str] = None) -> str:
    """
    Preprocess text for TTS by removing markdown and other formatting.
    
    Args:
        text: The input text to preprocess
        engine: The TTS engine being used (for engine-specific processing)
        
    Returns:
        Preprocessed text ready for TTS
    """
    if not text or not isinstance(text, str):
        return ""
    
    logger.debug("Preprocessing text for TTS (length: %d)", len(text))
    
    try:
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
        
        # Remove markdown links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # Remove inline code
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up whitespace and newlines
        text = ' '.join(text.split())
        
        # Special handling for different TTS engines
        engine = engine or config.voice.engine.lower()
        if engine in ["google", "edge"]:
            # Remove markdown formatting
            text = text.replace('*', '').replace('_', '').replace('~', '')
        
        logger.debug("Preprocessed text (length: %d)", len(text))
        return text
        
    except Exception as e:
        logger.error("Error preprocessing text for TTS: %s", str(e), exc_info=True)
        # Return the original text if preprocessing fails
        return text if isinstance(text, str) else ""

def speak_config(text: str, voice: Optional[str] = None, rate: Optional[float] = None) -> None:
    """
    Speak text using the configured TTS engine with error handling and fallback.
    
    Args:
        text: The text to speak
        voice: Optional voice ID to use (overrides config)
        rate: Optional speaking rate (overrides config)
        
    Raises:
        RuntimeError: If all TTS engines fail
    """
    if not text or not text.strip():
        logger.debug("Empty text provided to speak_config")
        return
    
    logger.debug("Speaking text (length: %d)", len(text))
    
    # Get the current engine
    current_engine = config.voice.engine.lower()
    engines_to_try = [current_engine]
    
    # Add fallback engines in order of preference
    if current_engine != "edge" and edge_speak:
        engines_to_try.append("edge")
    if current_engine != "google" and google_speak:
        engines_to_try.append("google")
    if current_engine != "chatterbox" and chatterbox_speak:
        engines_to_try.append("chatterbox")
    
    # Try each engine until one works
    last_error = None
    for engine_name in engines_to_try:
        if engine_name not in TTS_ENGINES or TTS_ENGINES[engine_name] is None:
            logger.debug("Skipping unavailable TTS engine: %s", engine_name)
            continue
            
        logger.debug("Attempting to speak with %s TTS", engine_name.upper())
        try:
            # Preprocess text for the specific engine
            processed_text = preprocess_for_tts(text, engine_name)
            
            # Get the appropriate speak function
            speak_func = TTS_ENGINES[engine_name]
            
            # Call with parameters if they exist in the function signature
            import inspect
            sig = inspect.signature(speak_func)
            params = {}
            
            if 'voice' in sig.parameters:
                params['voice'] = voice or config.voice.id
            if 'speaking_rate' in sig.parameters:
                params['speaking_rate'] = rate or config.voice.rate
            
            speak_func(processed_text, **params)
            logger.debug("Successfully spoke with %s TTS", engine_name.upper())
            return
            
        except Exception as e:
            error_msg = f"{engine_name.upper()} TTS failed: {str(e)}"
            logger.warning(error_msg, exc_info=logger.level <= logging.DEBUG)
            last_error = e
    
    # If we get here, all engines failed
    error_msg = "All TTS engines failed"
    logger.error(error_msg)
    if last_error:
        error_msg += f": {str(last_error)}"
    raise RuntimeError(error_msg)

def listen(timeout: Optional[float] = None, phrase_time_limit: Optional[float] = 10.0) -> Optional[str]:
    """
    Listen for audio input and convert it to text using speech recognition.
    
    Args:
        timeout: Maximum seconds to wait for speech before timing out
        phrase_time_limit: Maximum seconds for a phrase before it's cut off
        
    Returns:
        Recognized text as a string, or None if recognition failed
    """
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.0  # seconds of non-speaking audio before a phrase is considered complete
    recognizer.energy_threshold = 4000  # minimum audio energy to consider for recording
    recognizer.dynamic_energy_threshold = True
    
    logger.debug("Starting speech recognition...")
    
    with sr.Microphone() as source:
        try:
            # Adjust for ambient noise
            logger.debug("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Listen for audio input
            logger.debug("Listening...")
            audio = recognizer.listen(
                source, 
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
            
            # Recognize speech using Google's speech recognition
            logger.debug("Recognizing speech...")
            query = recognizer.recognize_google(audio, language="en-US")
            
            if query:
                logger.info("Recognized: %s", query)
                return query.lower()
                
        except sr.WaitTimeoutError:
            logger.debug("Listening timed out")
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
        except sr.RequestError as e:
            logger.error("Could not request results from Google Speech Recognition service: %s", e)
        except Exception as e:
            logger.error("Error in speech recognition: %s", str(e), exc_info=True)
    
    return None

def wake_mode() -> None:
    """
    Run the assistant in wake word mode, where it listens for a wake word
    before processing voice commands.
    """
    logger.info("Starting wake word mode")
    
    recognizer = sr.Recognizer()
    WAKE_PHRASE = config.wake_word.lower()
    SHUTDOWN_PHRASE = config.shutdown_word.lower()

    logger.info("Wake word: '%s'", WAKE_PHRASE)
    print(f"\n🔊 Wake word mode activated. Say '{WAKE_PHRASE}' to activate...")
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
    print("🧠 Groq Assistant - Core Edition (TTS: {})".format(config.voice.engine.upper()))
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

def main() -> None:
    """
    Main entry point for the Cortex Desktop Assistant.
    """
    try:
        logger.info("Starting Cortex Desktop Assistant")
        
        # Determine the mode to run in
        mode = config.mode.lower()
        
        # Print welcome message
        print(
            f"\n{'='*50}\n"
            "  🧠 Cortex Desktop Assistant\n"
            f"  Mode: {mode.upper()}\n"
            f"  TTS: {config.voice.engine.upper()}\n"
            f"  Version: {getattr(config, 'version', '1.0.0')}\n"
            f"{'='*50}\n"
        )
        
        # Run the appropriate mode
        if mode == "wake":
            wake_mode()
        else:  # Default to CLI mode
            cli_mode()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\nExiting...")
    except Exception as e:
        logger.critical("Fatal error: %s", str(e), exc_info=True)
        print(f"\n❌ A fatal error occurred: {str(e)}")
        print("Check the logs for more details.")
    finally:
        logger.info("Cortex Desktop Assistant stopped")

if __name__ == "__main__":
    # Configure global exception handler
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Global exception handler to log uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Call the default handler for KeyboardInterrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger.critical(
            "Uncaught exception", 
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # Try to show an error message
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror(
                "Fatal Error",
                f"An unexpected error occurred:\n\n{str(exc_value)}\n\n"
                "Check the logs for more details. The application will now exit."
            )
            root.destroy()
        except Exception:
            pass
    
    # Set the global exception handler
    sys.excepthook = handle_exception
    
    # Run the application
    main()
