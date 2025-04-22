import RPi.GPIO as GPIO
import time
import random

BUZZER_PIN = 19

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

pwm = GPIO.PWM(BUZZER_PIN, 440)

try:
    pwm.start(50)

    # Cursed microtonal alien scale
    cursed_scale = [333, 358, 382, 400, 427, 451, 470, 497, 523, 539, 562, 598, 620, 666]

    for freq in cursed_scale:
        pwm.ChangeFrequency(freq)
        time.sleep(0.2)

    # Spicy glissando into madness
    for i in range(100):
        freq = random.randint(200, 1200)
        pwm.ChangeFrequency(freq)
        time.sleep(0.03)

    pwm.ChangeFrequency(666)
    time.sleep(1)

    pwm.stop()

finally:
    GPIO.cleanup()
