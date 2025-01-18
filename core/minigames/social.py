import random
from utils.color_utils import calculate_average_color


def initialize_socializing(graphics):
    calculated_color = calculate_average_color(graphics.sprites[0])  # Calculate average color of player's sprite
    other_bubble_color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255)])  # Random choice for the other Tama

    return {
        "current_round": 1,  # Track the number of rounds
        "max_rounds": 3,  # Total rounds
        "interaction_done": False,
        "other_tama_sprite": f"assets/sprites/otherTama/tama{random.randint(1, 3)}.png",
        "player_feedback_sprite": None,  # Feedback sprite for the player Tama
        "other_feedback_sprite": None,  # Feedback sprite for the other Tama
        "player_bubble_color": calculated_color,  # Initial bubble color for the player
        "other_bubble_color": other_bubble_color,
        "player_options": [calculated_color, other_bubble_color],  # Choices for player bubble color
        "current_choice": 0,  # Start with the calculated color
        "animation_frames": 0,  # Tracks animation cycles
        "tama_animation_offset": 0,  # Up/down offset for Tamas
    }



def handle_social_input(social_state, controls, stats):
    """
    Handle user input for the socializing game.
    """
    if not social_state["interaction_done"]:
        # Cycle through player options
        if controls.right_button:
            social_state["current_choice"] = (social_state["current_choice"] + 1) % len(social_state["player_options"])
            social_state["player_bubble_color"] = social_state["player_options"][social_state["current_choice"]]

        # Make a choice
        if controls.center_button:
            player_choice = social_state["player_options"][social_state["current_choice"]]
            if player_choice == social_state["other_bubble_color"]:
                stats.stats["social"] = min(stats.stats["social"] + 10, 100)
                social_state["other_feedback_sprite"] = ["assets/sprites/heart1.png", "assets/sprites/heart2.png"]
                social_state["player_feedback_sprite"] = None  # No feedback for player
            else:
                stats.stats["esteem"] = min(stats.stats["esteem"] + 10, 100)
                social_state["player_feedback_sprite"] = ["assets/sprites/heart1.png", "assets/sprites/heart2.png"]
                social_state["other_feedback_sprite"] = None  # No feedback for other Tama

            # Handle decreases
            if player_choice != social_state["other_bubble_color"]:
                stats.stats["social"] = max(stats.stats["social"] - 5, 0)
                social_state["other_feedback_sprite"] = ["assets/sprites/anger1.png", "assets/sprites/anger2.png"]
            else:
                stats.stats["esteem"] = max(stats.stats["esteem"] - 5, 0)
                social_state["player_feedback_sprite"] = ["assets/sprites/anger1.png", "assets/sprites/anger2.png"]

            social_state["interaction_done"] = True
            social_state["animation_frames"] = 0

    else:
        # End round after animation
        if social_state["animation_frames"] >= 40:  # Adjust for two cycles
            social_state["current_round"] += 1
            social_state["interaction_done"] = False
            social_state["player_feedback_sprite"] = None
            social_state["other_feedback_sprite"] = None
            social_state["tama_animation_offset"] = 0

            if social_state["current_round"] > social_state["max_rounds"]:
                social_state["interaction_done"] = True  # End the minigame
