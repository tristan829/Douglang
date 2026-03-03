import pyttsx3
import pygame
import wave
import numpy as np
import tempfile
import os
from threading import Lock
import time

# TODO: Find a way to get the Geraint voice running cross platform. Currently, it only works on Windows, and only if you have the voice installed.
# Possibly, using something like Amazon Polly?

class TTS:
    def __init__(self):
        pygame.mixer.init()
        self.current_text = ""
        self._amplitude = 0.0
        self.speaking = False

    def speak(self, text: str):
        self.current_text = text
        self.speaking = True

        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)

        # Attempt to use the Geraint voice. If it isn't available, it will default to something like Microsoft David Desktop
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
