import random
import pygame

def handle_education_input(stats, states, controls):
    """
    Handle input and navigation logic for the education mini-game.
    """

    if controls.left_button:
        stats.update_education_stats(states.selected_level, states.student_loan)
        states.transition_to_screen("home_screen")
        return

    if states.animation_frame is None:
        # Navigate between suitcases
        if controls.right_button:
            states.selected_point_index = (states.selected_point_index + 1) % 2

        # Select a suitcase to start the animation
        if controls.center_button:
            states.animation_frame = 0
            education_options = {
                0: {"level": "HS", "loan": 5000},    # Suitcase 0
                1: {"level": "BSc", "loan": 20000}, # Suitcase 1
                2: {"level": "MSc", "loan": 50000}, # Suitcase 2
                3: {"level": "PhD", "loan": 100000} # Suitcase 3
            }
            selected = education_options.get(random.choice([0, 1, 2, 3]), {})
            states.selected_level = selected.get("level", "DropOut")
            states.student_loan = selected.get("loan", random.choice([0, 1000, 2000]))

    elif states.animation_frame <= 2:
        # Advance animation frames
        pygame.time.delay(500)
        states.animation_frame += 1

    else:
        # Wait for button press to return home
        if controls.left_button:
            stats.update_education_stats(states.selected_level, states.student_loan)
            states.animation_frame = None
            states.transition_to_screen("home_screen")


def render_education_screen(graphics, states):
    """
    Render the education mini-game, including animations.
    """
    if states.animation_frame is None:
        # Render the mini-game screen
        graphics.draw_education_screen(states.selected_point_index)
    elif states.animation_frame <= 2:
        # Handle animation frames
        graphics.draw_education_animation(
            states.selected_point_index,
            states.animation_frame,
            states.selected_level,
            states.student_loan
        )
