import ctypes
from pathlib import Path
import sys
import pyttsx3
import pygame
import wave
import numpy as np
import tempfile
import os
import time

# TODO: Find a way to get the Geraint voice running cross platform. Currently, it only works on Windows, and only if you have the voice installed.
# Possibly, using something like Amazon Polly?

S2G_PATH = r"C:\Program Files (x86)\Speech2Go Voice Package\x64"
DLLS = ["tts_engine.dll", "voice_en_wls_geraint.dll", "VE_sapi_x64.dll", "ve_tools.dll"] # These are the DLLs that are needed to run the Geraint voice

class TTS:
    def __init__(self):
        pygame.mixer.init()
        self.current_text = ""
        self._amplitude = 0.0
        self.speaking = False
        self.can_use_geraint_voice = False
        if sys.platform.startswith("win") and Path(S2G_PATH).is_dir():
            try:
                for dll in DLLS:
                    ctypes.WinDLL(os.path.join(S2G_PATH, dll))
        
                # Initialize engine and check for Geraint voice
                engine = pyttsx3.init()
                self.can_use_geraint_voice = any("Geraint" in v.name for v in engine.getProperty('voices'))
        
            except Exception as e:
                print(f"Error loading Geraint voice: {e}")
                return False
        if not self.can_use_geraint_voice:
            print("Could not use Geraint voice.")

    def speak(self, text: str):
        self.current_text = text
        self.speaking = True

        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)

        # Attempt to use the Geraint voice. If it isn't available, it will default to something like Microsoft David Desktop
        if self.can_use_geraint_voice:
            for voice in engine.getProperty('voices'):
                if "Geraint" in voice.name:
                    engine.setProperty('voice', voice.id)
                    break

        # Save TTS to temporary WAV file
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_file.close()
        engine.save_to_file(text, tmp_file.name)
        engine.runAndWait()  # synchronous

        # Play audio
        wf = wave.open(tmp_file.name, 'rb')
        pygame.mixer.quit()
        pygame.mixer.init(frequency=wf.getframerate())
        pygame.mixer.music.load(tmp_file.name)
        pygame.mixer.music.play()

        # Listen to amplitude
        chunk_size = 1024
        data = wf.readframes(chunk_size)
        while pygame.mixer.music.get_busy() and data:
            samples = np.frombuffer(data, dtype=np.int16)
            amp = np.max(np.abs(samples)) / 32768.0
            self._amplitude = amp
            data = wf.readframes(chunk_size)
            time.sleep(chunk_size / wf.getframerate())

        # Cleanup
        self._amplitude = 0.0

        while pygame.mixer.music.get_busy():
            time.sleep(0.01)

        pygame.mixer.music.unload()
        wf.close()
        os.unlink(tmp_file.name)
        self.speaking = False

    def get_amplitude(self) -> float:
        return self._amplitude
