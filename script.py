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
            if controls.center_button:
                states.transition_to_screen(states.get_current_screen_from_point())
            if controls.left_button:
                states.transition_to_screen("stats_screen")

        elif states.current_screen == "stats_screen":
            graphics.clear_screen()
            stats.render_stats_screen(graphics)
            if controls.left_button:
                states.transition_to_screen("home_screen")

        elif states.current_screen.startswith("game_"):
            graphics.clear_screen()
            graphics.draw_game_screen(states.selected_point_index)

            if controls.left_button:
                states.transition_to_screen("home_screen")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()