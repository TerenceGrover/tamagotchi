import RPi.GPIO as GPIO
import time

SAFE_PINS = [2, 3, 14, 15, 25, 9, 10, 11, 8, 7]  # All safe GPIOs (see notes below)
PIN_NAMES = {
    2: "GPIO2 (SDA)",
    3: "GPIO3 (SCL)",
    14: "GPIO14 (TX)",
    15: "GPIO15 (RX)",
    25: "GPIO25",
    9: "GPIO9 (MISO)",
    10: "GPIO10 (MOSI)",
    11: "GPIO11 (SCLK)",
    8: "GPIO8 (CE0)",
    7: "GPIO7 (CE1)",
    19: "GPIO19 (old center Button)",
    24: "GPIO24 (old left Button)",
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup pins
for pin in SAFE_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    print("Press buttons (CTRL+C to stop):")
    while True:
        for pin in SAFE_PINS:
            state = GPIO.input(pin)
            if state == GPIO.LOW:
                print(f"{PIN_NAMES[pin]}: Pressed")
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nCleaned up GPIO")
