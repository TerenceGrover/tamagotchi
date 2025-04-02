import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from core.graphics import Graphics
from core.controls import Controls
from core.states import States
from core.stats import Stats
from core.minigames.platformer import update_platforms, check_goal_reached, handle_input, draw_platformer, calculate_jump_curve
from core.minigames.education import handle_education_input, render_education_screen
from core.minigames.social import handle_social_input, initialize_socializing
from core.minigames.housing import initialize_housing, handle_housing_input, assign_real_estate_agent
from core.minigames.hobby import initialize_hobby, update_hobby
from core.minigames.job import initialize_job, update_job, apply_job_rewards
import subprocess
import RPi.GPIO as GPIO

def init_controls_safely():
    subprocess.run(["/home/terence/tamagotchi/venv/bin/python3", "init_gpio_once.py"])
    print("GPIO pre-initialized safely")


# Constants
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32
FPS = 25
BRIGHTNESS = 50

def main():
    # GPIO setup before matrix is even imported
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("GPIO initialized early")

    # Set up the LED matrix options
    options = RGBMatrixOptions()
    options.rows = MATRIX_HEIGHT          # Physical rows on the LED panel
    options.brightness = BRIGHTNESS
    options.cols = MATRIX_WIDTH           # Physical columns on the LED panel
    options.chain_length = 1              # Adjust if you have multiple panels daisy-chained
    options.parallel = 1                  # Adjust for parallel chains if needed
    # You can tweak additional options such as brightness, pwm_bits, etc., here

    time.sleep(0.5)
    matrix = RGBMatrix(options=options)

    # Initialize game modules – note Graphics now receives the matrix instance instead of a Pygame screen.
    print("Creating controls")
    controls = Controls()
    print("Controls initialized fine")
    # controls = DummyControls()
    states = States()
    stats = Stats()
    graphics = Graphics(matrix, MATRIX_WIDTH, MATRIX_HEIGHT, 1)  # Adjusted constructor; PIXEL_SIZE is now implicit

    graphics.set_sprites(graphics.load_sprites(states.get_sprite_folder()))

    running = True
    while running:
        # Handle input using your updated Controls module (likely now reading GPIO inputs)
        controls.handle_input()

        # Update game state and stats
        old_stage = states.stage_of_life
        states.update_life_stage()
        if old_stage != states.stage_of_life:
            graphics.update_sprites(states)  # Reload sprites on stage change

        stats.decay_stats()  # Decay stats over time

        # Render based on the current screen/state
        if states.current_screen == "home_screen":
            graphics.draw_home_screen(states.selected_point_index, states)
            if controls.right_button:
                states.cycle_point()
            elif controls.center_button:
                selected_screen = states.get_current_screen_from_point()
                if states.is_screen_available(selected_screen):
                    states.transition_to_screen(selected_screen)
                else:
                    print(f"Cannot access {selected_screen} at this stage!")
            elif controls.left_button:
                states.transition_to_screen("stats_screen")

        elif states.current_screen == "stats_screen":
            graphics.clear_screen()
            stats.render_stats_screen(graphics)
            if controls.left_button:
                states.transition_to_screen("home_screen")

        elif states.current_screen == "education_screen":
            handle_education_input(stats, states, controls)
            render_education_screen(graphics, states)

        elif states.current_screen == "socialize_screen":
            if not states.social_state:
                states.social_state = initialize_socializing(graphics)
            handle_social_input(states, states.social_state, controls, stats)
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
                handle_input(states.platformer_state, controls, states, jump_curve)
                check_goal_reached(states.platformer_state, stats)

            draw_platformer(graphics, states.platformer_state, states.get_sprite_folder())
            if states.platformer_state["minigame_ended"]:
                states.reset_platformer()
                states.transition_to_screen("home_screen")

        elif states.current_screen == "hobby_screen":
            if not states.hobby_state:
                states.start_hobby()
            if not states.hobby_state["game_over"]:
                update_hobby(states.hobby_state, controls, stats)
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
                update_job(states.job_state, controls)
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

            handle_housing_input(states.housing_state, stats, controls, FPS, states)
            if (states.housing_state["countdown_active"] or 
                states.housing_state["random_timeout_active"] or 
                states.housing_state["reaction_active"] or 
                states.housing_state["reaction_result"] is not None):
                graphics.draw_housing_reaction_game(states.housing_state, FPS)
                if states.housing_state["real_estate_agent"] is None:
                    assign_real_estate_agent(states.housing_state)
            else:
                graphics.draw_housing_screen(states.housing_state)

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

        # Instead of pygame.display.flip(), we swap the canvas on the LED matrix.
        # Here we assume your Graphics module manages a 'canvas' attribute for drawing.
        graphics.render_to_matrix()
        time.sleep(1.0 / FPS)

if __name__ == "__main__":
    main()
