import pygame
from core.graphics import Graphics
from core.controls import Controls
from core.states import States
from core.stats import Stats
import random

# Constants
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32
PIXEL_SIZE = 20
FPS = 30

import pygame
from core.graphics import Graphics
from core.controls import Controls
from core.states import States
from core.stats import Stats

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
            if states.animation_frame is None:
                # Render the mini-game screen
                graphics.draw_education_screen(states.selected_point_index)

                # Navigate between suitcases
                if controls.right_button:
                    states.selected_point_index = (states.selected_point_index + 1) % 2

                # Select a suitcase to start the animation
                if controls.center_button:
                    states.animation_frame = 0
                    states.selected_level = random.choice(["HS", "BSc", "MSc", "PhD"])
                    states.student_loan = random.choice([5000, 20000, 50000, 100000])
            else:
                # Handle animation frames
                graphics.draw_education_animation(states.selected_point_index, states.animation_frame, 
                                                states.selected_level, states.student_loan)

                # Advance animation frame
                pygame.time.delay(500)  # Adjust delay as needed
                states.animation_frame += 1

                # Reset after animation
                if states.animation_frame > 2:
                    # change only on button press
                    if controls.left_button:
                        states.update_education(states.selected_level, states.student_loan)
                        states.animation_frame = None
                        states.transition_to_screen("home_screen")



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