import RPi.GPIO as GPIO
import time

PIN = 3  # use any pin that was previously ghosting

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        print("Pressed" if GPIO.input(PIN) == GPIO.LOW else "Released")
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
