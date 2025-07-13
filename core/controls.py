import RPi.GPIO as GPIO
import time

class Controls:
    def __init__(self):
        GPIO.cleanup()  # clear any previous pin state
        print("Initializing GPIO for Controls...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.left_pin = 8
        self.center_pin = 7
        self.right_pin = 25

        GPIO.setup(self.left_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.right_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.center_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.left_button = False
        self.right_button = False
        self.center_button = False

        self.debounce_interval = 0.2  # seconds
        self.last_press_left = 0
        self.last_press_right = 0
        self.last_press_center = 0

        print("GPIO fully initialized from Controls.")

    def handle_input(self):
        now = time.time()

        left_state = GPIO.input(self.left_pin)
        right_state = GPIO.input(self.right_pin)
        center_state = GPIO.input(self.center_pin)

        # print(f"RAW STATES: LEFT={left_state}, RIGHT={right_state}, CENTER={center_state}")

        # LEFT
        if left_state == GPIO.LOW and (now - self.last_press_left > self.debounce_interval):
            self.left_button = True
            self.last_press_left = now
            print("Left button pressed")
        else:
            self.left_button = False

        # RIGHT
        if right_state == GPIO.LOW and (now - self.last_press_right > self.debounce_interval):
            self.right_button = True
            self.last_press_right = now
            print("Right button pressed")
        else:
            self.right_button = False

        # CENTER
        if center_state == GPIO.LOW and (now - self.last_press_center > self.debounce_interval):
            self.center_button = True
            self.last_press_center = now
            print("Center button pressed")
        else:
            self.center_button = False
