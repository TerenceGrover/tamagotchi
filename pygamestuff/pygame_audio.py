import pygame
import threading
import numpy as np

class AudioManager:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.lock = threading.Lock()
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)
    
    def _generate_tone(self, frequency, duration=0.2, volume=0.5):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = 0.5 * np.sin(2 * np.pi * frequency * t)
        audio = (volume * wave * (2**15 - 1)).astype(np.int16)  # 16-bit audio
        sound = pygame.sndarray.make_sound(audio)
        return sound

    def _play_notes(self, frequencies, duration=0.2):
        with self.lock:
            for freq in frequencies:
                sound = self._generate_tone(freq, duration)
                sound.play()
                pygame.time.delay(int(duration * 1000))  # delay in ms

    def play_sound(self, sound_type):
        sound_map = {
            'click': [600],
            'noteHit': [800],
            'noteMiss': [400],
            'jump': [400, 700],
            'workElement': [300, 500],
            'statLow': [330, 250],
            'success': [600, 800, 1000],
            'failure': [400, 300, 200],
            'gameWin': [523, 587, 659, 784],
            'gameLose': [659, 587, 523, 400],
            'suitcaseOpen': [300, 600, 300, 600],
            'happy': [523, 659, 784],
            'sad': [784, 659, 523]
        }

        if sound_type in sound_map:
            threading.Thread(target=self._play_notes, args=(sound_map[sound_type],)).start()
        else:
            print(f"Unknown sound type: {sound_type}")

    def cleanup(self):
        pygame.mixer.quit()
