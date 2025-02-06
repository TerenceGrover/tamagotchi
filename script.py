import pygame
from core.graphics import Graphics
from core.controls import Controls
from core.states import States
from core.stats import Stats
from core.minigames.platformer import update_platforms, check_goal_reached, handle_input, draw_platformer, calculate_jump_curve
from core.minigames.education import handle_education_input, render_education_screen
from core.minigames.social import handle_social_input, initialize_socializing
from core.minigames.housing import initialize_housing, handle_housing_input

# Constants
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32
PIXEL_SIZE = 20
FPS = 30


def main():
    pygame.init()
    screen_width = MATRIX_WIDTH * PIXEL_SIZE
    screen_height = MATRIX_HEIGHT * PIXEL_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tamagotchi")

    controls = Controls()
    states = States()
    stats = Stats()
    graphics = Graphics(screen, MATRIX_WIDTH, MATRIX_HEIGHT, PIXEL_SIZE)

    graphics.set_sprites(graphics.load_sprites(states.get_sprite_folder()))

    clock = pygame.time.Clock()
    running = True

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Handle inputs
        controls.handle_input()

        # Update life stage and stats
        old_stage = states.stage_of_life
        states.update_life_stage()
        if old_stage != states.stage_of_life:
            graphics.update_sprites(states)  # Reload sprites on stage change

        stats.decay_stats()  # Decay stats over time

        # Screen-specific rendering
        if states.current_screen == "home_screen":
            graphics.draw_home_screen(states.selected_point_index)

            if controls.right_button:
                states.cycle_point()
            elif controls.center_button:
                states.transition_to_screen(states.get_current_screen_from_point())
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
                    states.social_state = None  # Reset the minigame state

        elif states.current_screen == "food_screen":
            if not states.platformer_state:
                states.start_platformer(stats.stats["money"])

            if not states.platformer_state["minigame_ended"]:
                # Create jump curve
                jump_curve = calculate_jump_curve(duration=12, peak_height=2)

                # Call update_platforms with the jump curve
                update_platforms(states.platformer_state, jump_curve)
                handle_input(states.platformer_state, controls, states, jump_curve)
                check_goal_reached(states.platformer_state, stats)

            draw_platformer(graphics, states.platformer_state, states.get_sprite_folder())

            if states.platformer_state["minigame_ended"]:
                states.reset_platformer()
                states.transition_to_screen("home_screen")

        elif states.current_screen == "housing_screen":
            if not states.housing_state:
                states.housing_state = initialize_housing()

            if (states.housing_state["countdown_active"] or states.housing_state["random_timeout_active"]) and controls.center_button:
                # Fail the game due to early button press
                states.housing_state["reaction_result"] = "fail"
                states.housing_state["countdown_active"] = False
                states.housing_state["random_timeout_active"] = False
                states.housing_state["reaction_active"] = False
                print("Game failed due to early button press!")

            # Handle input and update the housing state
            handle_housing_input(states.housing_state, controls, FPS, states)

            # Render the appropriate housing screen
            if (
                states.housing_state["countdown_active"]
                or states.housing_state["random_timeout_active"]
                or states.housing_state["reaction_active"]
                or states.housing_state["reaction_result"] is not None
            ):
                graphics.draw_housing_reaction_game(states.housing_state, FPS)
            else:
                graphics.draw_housing_screen(states.housing_state)

            # Allow the user to stay on the result screen until they press the left button
            if states.housing_state["reaction_result"] is not None and not states.housing_state["reaction_active"]:
                if controls.left_button:
                    # Transition back to the home screen only when the left button is pressed
                    print(f"Reaction result: {states.housing_state['reaction_result']}")
                    states.transition_to_screen("home_screen")
                    states.housing_state = None

        elif states.current_screen in states.point_screens:
            graphics.clear_screen()
            graphics.render_individual_screen(states.current_screen)

            if controls.left_button:
                states.transition_to_screen("home_screen")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
