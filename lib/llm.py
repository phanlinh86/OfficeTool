"""
    This module is used to implement the LLM algorithm for this project
"""

from openai import OpenAI
import pyttsx3          # For text to speech
import whisper          # For transcribe
from time import time

OLLAMA_BASE_URL = "http://127.0.0.1:11434/v1"  # Default Ollama address

PROMPT_ASSISTANT = ("The following is a conversation with an AI assistant."
                    "\nThe assistant is helpful, creative, clever, and very friendly."
                    "\n"
                    "\nUser: Hello, who are you?"
                    "\nAI: I am an AI assistant. How can I help you today?"
                    "\nUser: What can you do for me?"
                    "\nAI: I can help you with a variety of tasks. What do you need help with?"
                    "\nUser:")

LANG_DICT = {   "en": "english",
                "vi": "vietnamese",
                "es": "spanish",
                "fr": "french",
                "ko": "korean",
                "zh": "chinese",
                "ja": "japanese",
                "de": "german",
            }  # Language codes
SPEAK_MIN_LENGTH = 10  # Minimum length of text to be spoken
BASE_MODEL = "llama3.2:latest"


class LLM(object):
    def __init__(self, prompt=PROMPT_ASSISTANT):
        # Initialize the chat client
        self._client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
        self._messages = [
            {"role": "system", "content": prompt},
        ]
        self.verbose = False
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()  # Initialize text-to-speech engine
        self.engine.setProperty('rate', 150)  # Set speech rate
        self.engine.setProperty('volume', 1)  # Set volume (0.0 to 1.0)


    def chat(self,message, speak=False, speak_stream=True):
        self._messages.append({"role": "user", "content": message})
        response = self._client.chat.completions.create(model=BASE_MODEL, stream=True, messages=self._messages)
        ai_reply = ""
        ai_speak = ""
        for chunk in response:
            print(chunk.choices[0].delta.content or "", end="", flush=True)
            ai_speak += chunk.choices[0].delta.content or ""
            ai_reply += chunk.choices[0].delta.content or ""
            if speak_stream:
                if speak and ((ai_speak != "") and ai_speak[-1] in ".,!?"):
                    try:
                        # Get available voices
                        self.speak(ai_speak or "")
                    except Exception as e:
                        print(f"Text-to-speech error: {e}")
                    ai_speak = ""
        print()
        if speak and speak_stream is False:
            try:
                # Get available voices
                self.engine.say(ai_reply or "")
                self.engine.runAndWait()
            except Exception as e:
                print(f"Text-to-speech error: {e}")

        self._messages.append({"role": "bot", "content": ai_reply})
        return ai_reply

    def translate(self, text, target_language="vi"):
        """Translates text using Ollama."""
        message = f"Translate the following to {LANG_DICT[target_language]}:\n\n{text}"
        return self.chat(message)

    def transcribe(self, audio_file=None, language="en"):  # Add language parameter
        """Transcribes audio using Whisper with language support."""
        if self.verbose:
            print("Transcribing audio... ", end="")
            start_time = time()

        try:
            whisper_model = whisper.load_model("base")
            result = whisper_model.transcribe(audio_file, fp16=False, language=language)  # Pass language to Whisper

            if self.verbose:
                transcription_time = time() - start_time
                print(f"Transcription Completed in {transcription_time:.2f} seconds!")

            return result

        except Exception as e:
            print(f"Transcription Error: {e}")
            return None

    def speak(self, text, language=None):
        """Speak the given text."""
        try:
            if language:
                self.change_voice(language)
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            return None

    def change_voice(self, language="English"):
        for voice in self.engine.getProperty('voices'):
            if language.lower() in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                return True
        raise RuntimeError("Language '{}' not found".format(language))