import RPi.GPIO as GPIO
import time

class Controls:
    def __init__(self):
        # This is REQUIRED even if subprocess did the setup
        GPIO.setmode(GPIO.BCM)

        self.left_button = False
        self.right_button = False
        self.center_button = False
        self.left_pin = 5
        self.right_pin = 6
        self.center_pin = 26
        self.last_press = time.time()
        self.debounce_interval = 0.4

    def handle_input(self):
        current_time = time.time()

        self.left_button = GPIO.input(self.left_pin) == GPIO.LOW and (current_time - self.last_press > self.debounce_interval)
        self.right_button = GPIO.input(self.right_pin) == GPIO.LOW and (current_time - self.last_press > self.debounce_interval)
        self.center_button = GPIO.input(self.center_pin) == GPIO.LOW and (current_time - self.last_press > self.debounce_interval)

        if self.left_button or self.right_button or self.center_button:
            self.last_press = current_time
            
        if self.left_button:
            print("Left button pressed")
        if self.right_button:
            print("Right button pressed")
        if self.center_button:
            print("Center button pressed")
