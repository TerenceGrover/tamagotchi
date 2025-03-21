import random
import pygame

def initialize_platformer(money_stats):
    """
    Initialize platformer game variables.
    """
    return {
        "tama_position": [3, 10], 
        "platforms": generate_platforms(5, 64, -10),
        "goal_position": (60, 10),
        "goal_area": (58, 8, 3, 3),  # x, y, width, height
        "platform_speed": .5,
        "minigame_ended": False,
        "jumping": False,
        "jump_counter": 0,
        "jump_duration": 20,  # frames
        "on_platform": False,
    }


def generate_platforms(num_platforms, screen_width, money_stat):
    """
    Generate platforms dynamically based on the money stat, ensuring valid ranges.

    Args:
        num_platforms (int): Base number of platforms.
        screen_width (int): Width of the screen in matrix units.
        money_stat (int): Money stat affecting the platform difficulty.

    Returns:
        list: List of platforms [x, y, width].
    """
    # Cap the number of platforms to fit within the screen
    max_platforms = screen_width // 10
    num_platforms = min(num_platforms + money_stat // 50, max_platforms)

    platforms = []
    for i in range(num_platforms):
        start_x = i * (screen_width // num_platforms)
        end_x = (i + 1) * (screen_width // num_platforms) - 10
        if start_x >= end_x:
            end_x = start_x + 5  # Ensure a minimum range for platform x

        x = random.randint(start_x, end_x)
        y = random.randint(15, 30)
        width = random.randint(8, 25 + money_stat // 10)
        platforms.append([x, y, width])

    return platforms


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
    tama_feet_y = tama_y + 5  # Feet position for collision

    # Move platforms and reset if out of bounds
    for platform in game_state["platforms"]:
        platform[0] -= game_state["platform_speed"]
        if platform[0] + platform[2] < 0:  # Reset platform position
            platform[0] = 64
            platform[1] = random.randint(15, 30)

    # Collision logic
    game_state["on_platform"] = False
    for platform_x, platform_y, platform_width in game_state["platforms"]:
        if (
            platform_x - 2 <= tama_x <= platform_x + platform_width + 2 and
            platform_y - 1 <= tama_feet_y <= platform_y + 1
        ):
            game_state["on_platform"] = True
            if not game_state["jumping"]:
                # Snapping logic to make it smoother baby
                game_state["tama_position"][1] = platform_y - 5
            break

    # Gravity
    if not game_state["on_platform"] and not game_state["jumping"]:
        game_state["tama_position"][1] += 1

    # Jumping logic
    if game_state["jumping"]:
        if game_state["jump_counter"] < len(jump_curve):
            game_state["tama_position"][1] -= jump_curve[game_state["jump_counter"]]
            game_state["jump_counter"] += 1
        else:
            game_state["jumping"] = False
            game_state["jump_counter"] = 0

    # Prevent falling through the floor
    game_state["tama_position"][1] = min(max(game_state["tama_position"][1], 0), 34)

    if game_state["tama_position"][1] == 34:
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
        game_state["on_platform"] = False


def check_goal_reached(game_state, stats):
    """
    Check if the Tamagotchi has reached the goal.
    """
    tama_x, tama_y = game_state["tama_position"]
    tama_feet_y = tama_y + 5
    goal_x, goal_y, goal_width, goal_height = game_state["goal_area"]

    if goal_x - goal_width <= tama_x <= goal_x + goal_width and goal_y - goal_height <= tama_y <= goal_y + goal_height:
        game_state["minigame_ended"] = True
        stats.stats["food"] = min(stats.stats["food"] + 20, 100)  # Cap food at 100


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