from core.controls import Controls
from core.graphics import Graphics
from core.stats import Stats
from core.states import States
import pygame

def game_loop(screen, screen_width, screen_height, pixel_size, fps):
    # Initialize modules
    controls = Controls()
    stats = Stats()
    states = States()
    graphics = Graphics(screen, screen_width // pixel_size, screen_height // pixel_size, pixel_size)
    sprites = graphics.load_sprites(states.get_sprite_folder())

    # Game loop variables
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

        # Determine the current screen to render
        current_state = states.current_state
        if current_state == "home_screen":
            # Render home screen (Tamagotchi sprite)
            graphics.draw_sprite(sprites[0])

            # Transition to stats screen on button press
            if controls.left_button:
                states.transition_to_state("stats_screen")
                sprites = graphics.load_sprites(states.get_sprite_folder())

        elif current_state == "stats_screen":
            # Render stats screen
            stats.render_stats_screen(graphics)

            # Return to home screen on button press
            if controls.left_button:
                states.transition_to_state("home_screen")
                sprites = graphics.load_sprites(states.get_sprite_folder())

        # Update the display
        pygame.display.flip()
        clock.tick(fps)
