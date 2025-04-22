import RPi.GPIO as GPIO
import threading
import time

class AudioManager:
    def __init__(self, buzzer_pin=19):
        self.buzzer_pin = buzzer_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.buzzer_pin, 440)
        self.lock = threading.Lock()

    def _play_notes(self, frequencies, duration=0.2):
        with self.lock:
            self.pwm.start(50)
            for freq in frequencies:
                self.pwm.ChangeFrequency(freq)
                time.sleep(duration)
            self.pwm.stop()

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

    def cleanup(self):
        GPIO.cleanup()
