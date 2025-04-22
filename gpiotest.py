import RPi.GPIO as GPIO
import os

print("EUID:", os.geteuid())

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("GPIO is happy.")
