import sys
import time
import random
from core.graphics import Graphics
from core.states import States
from core.stats import Stats
from core.minigames.platformer import update_platforms, check_goal_reached, handle_input, calculate_jump_curve, draw_platformer
from core.minigames.education import handle_education_input, render_education_screen
from core.minigames.social import handle_social_input, initialize_socializing
from core.minigames.housing import initialize_housing, handle_housing_input, assign_real_estate_agent
from core.minigames.hobby import initialize_hobby, update_hobby
from core.minigames.job import initialize_job, update_job, apply_job_rewards
from core.states import RANDOM_EVENTS
from utils.text_utils import text_to_matrix, split_text_to_lines
import subprocess

# def init_controls_safely():
#     subprocess.run(["/home/terence/tamagotchi/venv/bin/python3", "init_gpio_once.py"])
#     print("GPIO pre-initialized safely")

def get_matrix():
    from rgbmatrix import RGBMatrix, RGBMatrixOptions

    options = RGBMatrixOptions()
    options.hardware_mapping = 'regular'
    options.rows = MATRIX_HEIGHT        # Physical rows on the LED panel
    options.brightness = BRIGHTNESS
    options.cols = MATRIX_WIDTH         # Physical columns on the LED panel
    options.chain_length = 1
    options.led_rgb_sequence = 'RBG'    # Adjust if you have multiple panels daisy-chained
    options.parallel = 1                # Adjust for parallel chains if needed
    # options.pixel_mapper_config = "Rotate:180"
    options.hardware_mapping = "adafruit-hat"

    return RGBMatrix(options=options)

# Constants
PIXEL_SIZE = 20
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32
FPS = 25
BRIGHTNESS = 15
INIT = False

def main():
    # usage: python3 script.py debug=true
    debug = any("debug=true" in arg.lower() for arg in sys.argv)

    if debug:
        # debug mode, will play on pygame window, no hardware imports
        import pygame
        from pygamestuff.pygame_controls import Controls
        from pygamestuff.pygame_audio import AudioManager

        matrix = None
        audio = AudioManager()
        pygame.init()
        screen_width = MATRIX_WIDTH * PIXEL_SIZE
        screen_height = MATRIX_HEIGHT * PIXEL_SIZE
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Tamagotchi")
        graphics = Graphics(screen, MATRIX_WIDTH, MATRIX_HEIGHT, PIXEL_SIZE)
        clock = pygame.time.Clock()

    else:
        # not debug mode, game running on hardware, import hardware-specific libraries and initialize GPIO
        import RPi.GPIO as GPIO
        from core.audioManager import AudioManager
        from core.controls import Controls

        global INIT
        if INIT == False:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            print('init')
            INIT = True
        print("Graphics initialized fine")


    # Let's go
    print(f"Running in {'debug' if debug else 'raspberry'} mode")
    print("Creating controls")
    controls = Controls()
    running = True

    while running:
        if debug:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

        # Handle input using your updated Controls module (likely now reading GPIO inputs)
        controls.handle_input()
if __name__ == "__main__":
    main()