import RPi.GPIO as GPIO
import time

# Change this to the pin you want to test
TEST_PIN = 5  # BCM numbering

GPIO.setmode(GPIO.BCM)
GPIO.setup(TEST_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print(f"Listening on GPIO {TEST_PIN}... (Press CTRL+C to exit)")

try:
    while True:
        if GPIO.input(TEST_PIN) == GPIO.LOW:
            print("Button PRESSED")
        else:
            print("Button released")
        time.sleep(0.1)  # Slow it down so it's readable

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
