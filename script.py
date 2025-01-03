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
    # Initialize Pygame
    pygame.init()
    screen_width = MATRIX_WIDTH * PIXEL_SIZE
    screen_height = MATRIX_HEIGHT * PIXEL_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tamagotchi Movement")

    # Initialize modules
    controls = Controls()
    stats = Stats()
    states = States()
    graphics = Graphics(screen, MATRIX_WIDTH, MATRIX_HEIGHT, PIXEL_SIZE)

    # Load initial sprites
    graphics.set_sprites(graphics.load_sprites(states.get_sprite_folder()))

    # Game loop
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle inputs
        controls.handle_input()

        # Clear the screen
        graphics.clear_screen()

        # Update life stage
        states.update_life_stage()

        # Reload sprites if life stage changes
        new_sprites = graphics.load_sprites(states.get_sprite_folder())
        if new_sprites != graphics.sprites:
            graphics.set_sprites(new_sprites)

        # Decay stats
        stats.decay_stats()

        # Handle screens
        if states.current_screen == "home_screen":
            graphics.switch_sprite()
            graphics.move_sprite()
            graphics.draw_sprite()

            # Transition to stats screen
            if controls.left_button:
                states.transition_to_screen("stats_screen")

        elif states.current_screen == "stats_screen":
            stats.render_stats_screen(graphics)

            # Return to home screen
            if controls.left_button:
                states.transition_to_screen("home_screen")

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()