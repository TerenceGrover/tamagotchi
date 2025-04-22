import time
import random

# Define the keys where beats will fall
BEAT_POSITIONS = [24, 32, 40]  # Left, Center, Right - Centered at 32
DROP_SPEED = 1  # Slower movement
INITIAL_BEAT_INTERVAL = 0.8  # Base frequency for beats
MIN_BEAT_INTERVAL = 0.3  # Minimum time between notes (prevents excessive difficulty)
HIT_ZONE_Y = 28  # Y coordinate of hit zone
NOTE_WIDTH = 4  # Notes are 3 pixels wide
MATRIX_HEIGHT = 32  # Height of the matrix

def initialize_hobby():
    """
    Initializes the hobby minigame state.
    """
    return {
        "beats": [],  # List of falling beats (each is a dict with x, y)
        "last_beat_time": time.time(),
        "score": 0,
        "missed": 0,
        "game_over": False,
        "high_score": 0,
        "game_start_time": time.time(),  # 🔥 Track game duration
    }

def update_hobby(hobby_state, controls, stats, audio):
    """
    Updates the rhythm game state and applies stat changes at the end.
    """
    current_time = time.time()
    elapsed_time = current_time - hobby_state["game_start_time"]

    # 🔥 Reduce beat interval over time (more notes appear as game progresses)
    beat_interval = max(INITIAL_BEAT_INTERVAL - (elapsed_time / 60), MIN_BEAT_INTERVAL)

    # Generate a new beat at regular intervals
    if current_time - hobby_state["last_beat_time"] >= beat_interval:
        x_position = random.choice(BEAT_POSITIONS)  # Pick from 3 zones
        hobby_state["beats"].append({"x": x_position, "y": 0, "hit": False})  # Spawn new beat with hit status
        hobby_state["last_beat_time"] = current_time

    # Move beats down
    for beat in hobby_state["beats"]:
        beat["y"] += DROP_SPEED

    # Check for hits
    for beat in hobby_state["beats"][:]:  # Iterate over a copy to allow modification
        if HIT_ZONE_Y - 1 <= beat["y"] <= HIT_ZONE_Y + 1:  # Allow a small grace period
            if (
                (beat["x"] == BEAT_POSITIONS[0] and controls.left_button) or
                (beat["x"] == BEAT_POSITIONS[1] and controls.center_button) or
                (beat["x"] == BEAT_POSITIONS[2] and controls.right_button)
            ):
                hobby_state["score"] += 1
                beat["hit"] = True  # Mark note as successfully hit
                audio.play_sound("noteHit")  # Play sound for hit

    # Count missed notes
    for beat in hobby_state["beats"][:]:  # Iterate over a copy
        if beat["y"] >= MATRIX_HEIGHT:  # If it falls past the bottom
            if not beat["hit"]:  # If it wasn't hit, count as a miss
                hobby_state["missed"] += 1
                audio.play_sound("noteMiss")  # Play sound for miss
            hobby_state["beats"].remove(beat)  # Remove note after it fully leaves the screen

    # End game if too many missed
    if hobby_state["missed"] >= 5:  # Increased leniency
        hobby_state["game_over"] = True
        apply_hobby_rewards(hobby_state, stats, audio)  # Apply stats after game over


def apply_hobby_rewards(hobby_state, stats, audio):
    """
    Adjusts player stats based on their performance in the hobby mini-game.
    """
    current_score = hobby_state["score"]

    # 🔥 **Update high score before calculating performance**
    if current_score > hobby_state["high_score"]:
        hobby_state["high_score"] = current_score

    high_score = hobby_state["high_score"]
    
    # 🔥 **Fix performance calculation to avoid division by zero**
    if high_score == 0:
        performance = 0  # If no previous high score, treat it as 0%
    else:
        performance = (current_score / high_score) * 100

    # Apply stat changes based on performance
    if performance < 25:  # Bad performance
        stats.modify_stat("rest", 2)
        stats.modify_stat("esteem", -2)
        audio.play_sound("failure")
    elif 25 <= performance < 50:  # Neutral
        pass  # No change
        audio.play_sound("failure")
    elif 50 <= performance < 75:  # Good
        stats.modify_stat("rest", 2)
        stats.modify_stat("esteem", 2)
        audio.play_sound("success")
    elif 75 <= performance < 100:  # Great
        stats.modify_stat("rest", 2)
        stats.modify_stat("esteem", 5)
        audio.play_sound("success")
    else:  # New high score!
        stats.modify_stat("rest", 3)
        stats.modify_stat("esteem", 8)
        audio.play_sound("success")

    print(f"🎵 Hobby Complete! Score: {current_score}, High Score: {high_score}")
