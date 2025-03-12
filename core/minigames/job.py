import random
import time

# Mapping for education levels: starting sequence length and desk item sprites.
EDUCATION_CONFIG = {
    "HS": {
        "base_length": 3,
        "items": [
            "assets/sprites/job/hs_item1.png",
            "assets/sprites/job/hs_item2.png",
            "assets/sprites/job/hs_item3.png"
        ]
    },
    "BSc": {
        "base_length": 4,
        "items": [
            "assets/sprites/job/bsc_item1.png",
            "assets/sprites/job/bsc_item2.png",
            "assets/sprites/job/bsc_item3.png"
        ]
    },
    "MSc": {
        "base_length": 5,
        "items": [
            "assets/sprites/job/msc_item1.png",
            "assets/sprites/job/msc_item2.png",
            "assets/sprites/job/msc_item3.png"
        ]
    },
    "PhD": {
        "base_length": 6,
        "items": [
            "assets/sprites/job/phd_item1.png",
            "assets/sprites/job/phd_item2.png",
            "assets/sprites/job/phd_item3.png"
        ]
    },
}

# Time between each task in the sequence display (in seconds)
SEQUENCE_DELAY = 1.0  
# How much work drains energy (rest)
REST_DECREASE = 10  

def generate_initial_sequence(length):
    """
    Generate a random sequence of tasks.
    Each task is represented as an integer: 0 for left, 1 for center, 2 for right.
    """
    return [random.choice([0, 1, 2]) for _ in range(length)]

def initialize_job(education_level):
    """
    Initialize the job minigame state.
    The education level determines the starting sequence length and the desk items.
    """
    config = EDUCATION_CONFIG.get(education_level, EDUCATION_CONFIG["HS"])
    base_length = config["base_length"]
    return {
        "items": config["items"],         # List of sprite paths for desk items
        "sequence": generate_initial_sequence(base_length),
        "current_round": 1,
        "max_rounds": 8,                  # When the workday is over
        "input_sequence": [],
        "score": 0,
        "completed": False,
        "high_score": 0,
        "task_count": base_length        # Current sequence length
    }

def handle_job_input(job_state, controls):
    """
    Process the player's input to reproduce the sequence.
    The controls are mapped as follows: left_button → 0, center_button → 1, right_button → 2.
    """
    # Only register one input per frame for simplicity
    if controls.left_button:
        job_state["input_sequence"].append(0)
    elif controls.center_button:
        job_state["input_sequence"].append(1)
    elif controls.right_button:
        job_state["input_sequence"].append(2)
    
    # Check the current input against the expected sequence so far
    current_len = len(job_state["input_sequence"])
    if job_state["input_sequence"] != job_state["sequence"][:current_len]:
        # Incorrect input: penalize score and reset the input for this round
        job_state["score"] = max(0, job_state["score"] - 1)
        job_state["input_sequence"] = []
    elif current_len == len(job_state["sequence"]):
        # Correct full sequence: increment score and advance the round
        job_state["score"] += 1
        job_state["current_round"] += 1
        job_state["task_count"] += 1
        # Increase sequence length for the next round if not at maximum difficulty
        if job_state["task_count"] < job_state["max_rounds"]:
            job_state["sequence"].append(random.choice([0, 1, 2]))
        else:
            job_state["completed"] = True  # Workday complete
        job_state["input_sequence"] = []

def update_job(job_state, controls):
    """
    Update the job minigame state by processing player input.
    """
    handle_job_input(job_state, controls)

def apply_job_rewards(job_state, stats):
    """
    Adjust player stats based on performance in the job minigame.
    Rewards and penalties affect money, rest, and self-esteem.
    """
    current_score = job_state["score"]
    
    # Update high score if the current score beats it
    if current_score > job_state.get("high_score", 0):
        job_state["high_score"] = current_score
    high_score = job_state.get("high_score", 1)  # Avoid division by zero
    
    performance = (current_score / high_score) * 100

    # Apply rewards/penalties based on performance percentage
    if performance < 25:
        stats.modify_stat("money", -2)
        stats.modify_stat("rest", -2)
        stats.modify_stat("esteem", -3)
    elif performance < 50:
        stats.modify_stat("money", 0)
        stats.modify_stat("rest", -1)
        # No change in esteem
    elif performance < 75:
        stats.modify_stat("money", 2)
        stats.modify_stat("rest", 0)
        stats.modify_stat("esteem", 2)
    elif performance < 100:
        stats.modify_stat("money", 4)
        stats.modify_stat("rest", 1)
        stats.modify_stat("esteem", 3)
    else:
        stats.modify_stat("money", 6)
        stats.modify_stat("rest", 2)
        stats.modify_stat("esteem", 5)

    print(f"Job Complete! Score: {current_score}, High Score: {high_score}, Performance: {performance:.1f}%")
