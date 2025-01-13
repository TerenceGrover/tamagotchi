import random
import pygame
import math

def initialize_platformer():
    """
    Initialize platformer game variables.
    """
    return {
        "tama_position": [3, 10],  # Initial Tamagotchi position
        "platforms": [
            [12, 30, 25],  # Platform at x=8, y=30, width=25
            [50, 16, 10],
            [25, 24, 30],
            [20, 25, 10],
        ],
        "goal_position": (62, 12),  # Goal position
        "platform_speed": 1,
        "minigame_ended": False,
        "jumping": False,
        "jump_counter": 0,  # Timer for the jump animation
        "jump_duration": 20,  # Duration of the jump (frames)
        "on_platform": False,
    }


def calculate_jump_curve(duration, peak_height):
    """
    Generate a smooth jump curve for the given duration and peak height.
    """
    return [
        -4 * peak_height * ((t / duration) - 0.5) ** 2 + peak_height
        for t in range(duration + 1)
    ]


def update_platforms(game_state, jump_curve):
    """
    Move platforms, reset positions when they leave the screen,
    and check for collisions with the Tamagotchi.
    """
    tama_x, tama_y = game_state["tama_position"]

    # Move platforms and reset if out of bounds
    for platform in game_state["platforms"]:
        platform[0] -= game_state["platform_speed"]
        if platform[0] + platform[2] < 0:  # Reset platform position
            platform[0] = 64
            platform[1] = random.randint(10, 33)

    # Check collisions with platforms
    game_state["on_platform"] = False
    for platform_x, platform_y, platform_width in game_state["platforms"]:
        if platform_x <= tama_x <= platform_x + platform_width and tama_y == platform_y - 5:
            game_state["on_platform"] = True
            break

    # Gravity
    if not game_state["on_platform"] and not game_state["jumping"]:
        game_state["tama_position"][1] += 1  # Apply gravity

    # Jumping logic
    if game_state["jumping"]:
        if game_state["jump_counter"] < len(jump_curve):
            game_state["tama_position"][1] -= jump_curve[game_state["jump_counter"]]
            game_state["jump_counter"] += 1
        else:
            game_state["jumping"] = False
            game_state["jump_counter"] = 0

    # Prevent falling through the floor
    game_state["tama_position"][1] = min(max(game_state["tama_position"][1], 0), 40)


def check_goal_reached(game_state):
    """
    Check if the Tamagotchi has reached the goal.
    """
    tama_x, tama_y = game_state["tama_position"]
    goal_x, goal_y = game_state["goal_position"]
    if tama_x == goal_x and tama_y == goal_y:
        game_state["minigame_ended"] = True


def handle_input(game_state, controls, states, jump_curve):
    """
    Handle Tamagotchi movement based on user input.
    """
    # Cancel the mini-game when the left button is pressed
    if controls.left_button:
        game_state["minigame_ended"] = True
        states.transition_to_screen("home_screen")
        return

    # Movement
    if controls.right_button and game_state["tama_position"][0] < 63:
        game_state["tama_position"][0] += 1

    # Jump
    if controls.center_button and not game_state["jumping"] and game_state["on_platform"]:
        game_state["jumping"] = True
        game_state["jump_counter"] = 0

    # Prevent going out of bounds
    game_state["tama_position"][1] = min(max(game_state["tama_position"][1], 0), 30)


def draw_platformer(graphics, game_state, sprite_folder):
    """
    Render the platformer mini-game screen.
    """
    tama_position = game_state["tama_position"]
    platforms = game_state["platforms"]
    goal_position = game_state["goal_position"]

    graphics.clear_screen()

    # Draw platforms
    for platform_x, platform_y, platform_width in platforms:
        pygame.draw.rect(
            graphics.screen,
            (255, 255, 255),  # White platform
            (
                platform_x * graphics.pixel_size,
                platform_y * graphics.pixel_size,
                platform_width * graphics.pixel_size,
                graphics.pixel_size,
            ),
        )

    # Draw the goal
    goal_x, goal_y = goal_position
    pygame.draw.rect(
        graphics.screen,
        (0, 255, 0),  # Green goal
        (
            goal_x * graphics.pixel_size,
            goal_y * graphics.pixel_size,
            graphics.pixel_size,
            graphics.pixel_size,
        ),
    )

    # Draw Tamagotchi sprite
    tama_x, tama_y = tama_position
    graphics.draw_sprite_at(
        tama_x,
        tama_y,
        f"{sprite_folder}/sprite0.png",
        sprite_width=7,  # Scaled-down sprite
        sprite_height=7,
    )
