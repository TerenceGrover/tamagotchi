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
    options.pixel_mapper_config = "Rotate:180"
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
            GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            print('init')
            INIT = True
        matrix = get_matrix()
        audio = AudioManager()
        print("Audio initialized fine")
        graphics = Graphics(matrix, MATRIX_WIDTH, MATRIX_HEIGHT, 1)  # Adjusted constructor; PIXEL_SIZE is now implicit
        print("Graphics initialized fine")


    # Let's go
    print(f"Running in {'debug' if debug else 'raspberry'} mode")
    print("Creating controls")
    controls = Controls()
    time.sleep(0.5) # Allow time for GPIO setup
    states = States()
    stats = Stats()
    
    graphics.set_sprites(graphics.load_sprites(states.get_sprite_folder()))

    running = True
    while running:
        if debug:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

        # Handle input using your updated Controls module (likely now reading GPIO inputs)
        controls.handle_input()

        # Update game state and stats
        old_stage = states.stage_of_life
        states.update_life_stage()
        if old_stage != states.stage_of_life:
            graphics.update_sprites(states)  # Reload sprites on stage change

        stats.decay_stats()  # Decay stats over time

        if stats.check_win_condition() and states.stage_of_life != "dead":
            states.transition_to_screen("end_screen")
            states.transition_to_life_stage("dead")
            graphics.start_end_animation('win', None, states.get_sprite_folder())
            audio.play_sound("gameWin")
            continue

        death_cause = stats.check_lose_condition()
        if death_cause and states.stage_of_life != "dead":
            states.transition_to_screen("end_screen")
            graphics.start_end_animation('lose', death_cause, states.get_sprite_folder())
            audio.play_sound("gameLose")
            states.transition_to_life_stage("dead")
            graphics.update_sprites(states)
            continue

        # Render based on the current screen/state
        if states.current_screen == "home_screen":
            if states.random_event["active"]:
                graphics.clear_screen()

                # Split the prompt
                lines = split_text_to_lines(states.random_event["prompt"], max_chars_per_line=8)
                total_height = len(lines) * 7
                for i, line in enumerate(lines):
                    line_matrix = text_to_matrix(
                        line, "assets/fonts/tamzen.ttf", 11, MATRIX_WIDTH, MATRIX_HEIGHT
                    )
                    y_offset = MATRIX_HEIGHT // 12 + i * 6
                    graphics.draw_matrix(line_matrix, MATRIX_WIDTH // 5, y_offset)

                # Handle navigation
                if controls.left_button:
                    states.random_event["selection"] = "yes"
                    audio.play_sound("click")
                elif controls.right_button:
                    states.random_event["selection"] = "no"
                    audio.play_sound("click")
                elif controls.center_button:
                    # Apply the selected outcome
                    if states.random_event["selection"] == "yes":
                        states.random_event["outcome"]["yes"](stats)
                        audio.play_sound("success")
                    else:
                        states.random_event["outcome"]["no"](stats)
                        audio.play_sound("failure")
                    states.random_event.update({"active": False, "cooldown_timer": time.time()})
                    states.random_event["selection"] = "yes"

                # Draw Yes/No buttons
                button_font_size = 10
                yes_matrix = text_to_matrix("Yes", "assets/fonts/tamzen.ttf", button_font_size, 20, 10)
                no_matrix = text_to_matrix("No", "assets/fonts/tamzen.ttf", button_font_size, 20, 10)

                button_y = MATRIX_HEIGHT - 10

                graphics.draw_button(yes_matrix, MATRIX_WIDTH // 4 - 8, states.random_event["selection"] == "yes", button_y)
                graphics.draw_button(no_matrix, MATRIX_WIDTH // 2 + 8, states.random_event["selection"] == "no", button_y)

            else:
                if time.time() - states.random_event["cooldown_timer"] > random.randint(50, 200):
                    event = random.choice(RANDOM_EVENTS)
                    states.random_event.update({
                        "active": True,
                        "prompt": event["prompt"],
                        "outcome": event,
                        "selection": "yes"
                    })

                graphics.draw_home_screen(states.selected_point_index, states)
                if controls.right_button:
                    states.cycle_point()
                    audio.play_sound("click")
                elif controls.center_button:
                    selected_screen = states.get_current_screen_from_point()
                    if states.is_screen_available(selected_screen):
                        states.transition_to_screen(selected_screen)
                        audio.play_sound("click")
                    else:
                        print(f"Cannot access {selected_screen} at this stage!")
                elif controls.left_button:
                    states.transition_to_screen("stats_screen")
                    audio.play_sound("click")


        elif states.current_screen == "end_screen":
            graphics.clear_screen()
            graphics.draw_end_animation()

            # Wait a few seconds, then return to home
            if graphics.end_animation_done():
                states.transition_to_screen("home_screen")
                graphics.end_mode = None
                graphics.end_start_time = None
                graphics.death_cause = None
                graphics.death_sprite_folder = None

        elif states.current_screen == "stats_screen":
            graphics.clear_screen()
            stats.render_stats_screen(graphics)
            if controls.left_button:
                states.transition_to_screen("home_screen")

        elif states.current_screen == "education_screen":
            handle_education_input(stats, states, controls, audio)
            render_education_screen(graphics, states)

        elif states.current_screen == "socialize_screen":
            if not states.social_state:
                states.social_state = initialize_socializing(graphics)
            handle_social_input(states, states.social_state, controls, stats, audio)
            if states.social_state:
                graphics.draw_social_screen(
                    player_sprites=graphics.sprites,
                    other_tama_sprite=states.social_state["other_tama_sprite"],
                    social_state=states.social_state,
                )
                if states.social_state["interaction_done"] and states.social_state["current_round"] > states.social_state["max_rounds"]:
                    states.transition_to_screen("home_screen")
                    states.social_state = None

        elif states.current_screen == "food_screen":
            if not states.platformer_state:
                states.start_platformer(stats.stats["money"])

            if not states.platformer_state["minigame_ended"]:
                # Generate jump curve and update platforms/minigame logic
                jump_curve = calculate_jump_curve(duration=12, peak_height=2)
                update_platforms(states.platformer_state, jump_curve)
                handle_input(states.platformer_state, controls, states, jump_curve, audio)
                check_goal_reached(states.platformer_state, stats, audio)

            draw_platformer(graphics, states.platformer_state, states.get_sprite_folder())
            if states.platformer_state["minigame_ended"]:
                states.reset_platformer()
                states.transition_to_screen("home_screen")

        elif states.current_screen == "hobby_screen":
            if not states.hobby_state:
                states.start_hobby()
            if not states.hobby_state["game_over"]:
                update_hobby(states.hobby_state, controls, stats, audio, states)
            graphics.draw_hobby_screen(states.hobby_state)
            if states.hobby_state["game_over"]:
                if controls.left_button:  # Exit the game on failure
                    states.transition_to_screen("home_screen")
                    states.hobby_state = None

        elif states.current_screen == "job_screen":
            if not states.job_state:
                # Choose education level; default to "HS" if not set
                education_level = stats.stats.get("education", "HS")
                states.job_state = initialize_job(education_level)
            if not states.job_state["completed"]:
                update_job(states.job_state, controls, audio)
            graphics.draw_job_screen(states.job_state)
            if states.job_state["completed"]:
                apply_job_rewards(states.job_state, stats)
                states.transition_to_screen("home_screen")
                states.job_state = None

        elif states.current_screen == "housing_screen":
            if not states.housing_state:
                states.housing_state = initialize_housing()

            if (states.housing_state["countdown_active"] or states.housing_state["random_timeout_active"]) and controls.center_button:
                print("Game failed due to early button press!")
                states.housing_state["reaction_result"] = "fail"
                states.housing_state["countdown_active"] = False
                states.housing_state["random_timeout_active"] = False
                states.housing_state["reaction_active"] = False
                print("Game failed due to early button press!")

            handle_housing_input(states.housing_state, stats, controls, FPS, states, audio)
            if (states.housing_state["countdown_active"] or 
                states.housing_state["random_timeout_active"] or 
                states.housing_state["reaction_active"] or 
                states.housing_state["reaction_result"] is not None):
                graphics.draw_housing_reaction_game(states.housing_state, FPS)
                if states.housing_state["real_estate_agent"] is None:
                    assign_real_estate_agent(states.housing_state)
            else:
                graphics.draw_housing_screen(states.housing_state, stats)

            if states.housing_state["reaction_result"] is not None and not states.housing_state["reaction_active"]:
                if controls.left_button:
                    print(f"Reaction result: {states.housing_state['reaction_result']}")
                    states.transition_to_screen("home_screen")
                    states.housing_state = None

        elif states.current_screen in states.point_screens:
            graphics.clear_screen()
            graphics.render_individual_screen(states.current_screen)
            if controls.left_button:
                states.transition_to_screen("home_screen")
        
        if debug:
            pygame.display.flip()
            clock.tick(FPS)
        else:
        # Instead of pygame.display.flip(), we swap the canvas on the LED matrix.
        # Here we assume your Graphics module manages a 'canvas' attribute for drawing.
            graphics.render_to_matrix()
            time.sleep(1.0 / FPS)
    
    if debug: 
        pygame.quit()

if __name__ == "__main__":
    main()
