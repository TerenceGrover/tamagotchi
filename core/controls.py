import time
import RPi.GPIO as GPIO

class Controls:
    def __init__(self):
        self.left_button = False
        self.right_button = False
        self.center_button = False
        self.last_press = time.time()
        self.debounce_interval = 0.2  # 200ms debounce

        # Set up GPIO using BCM numbering
        GPIO.setmode(GPIO.BCM)
        # Replace these pin numbers with the ones you’re using
        self.left_pin = 17    # Example: GPIO 17 for the left button
        self.right_pin = 27   # Example: GPIO 27 for the right button
        self.center_pin = 22  # Example: GPIO 22 for the center button

        # Configure pins as inputs with pull-up resistors enabled
        GPIO.setup(self.left_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.right_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.center_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def handle_input(self):
        current_time = time.time()

        # Check left button: pressed if the pin reads LOW
        if GPIO.input(self.left_pin) == GPIO.LOW and (current_time - self.last_press > self.debounce_interval):
            self.left_button = True
            self.last_press = current_time
        else:
            self.left_button = False

        # Check right button
        if GPIO.input(self.right_pin) == GPIO.LOW and (current_time - self.last_press > self.debounce_interval):
            self.right_button = True
            self.last_press = current_time
        else:
            self.right_button = False

        # Check center button
        if GPIO.input(self.center_pin) == GPIO.LOW and (current_time - self.last_press > self.debounce_interval):
            self.center_button = True
            self.last_press = current_time
        else:
            self.center_button = False
