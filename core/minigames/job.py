import random
import time

# --- Configuration based on education level ---
EDUCATION_CONFIG = {
    "HS": {
        "base_length": 4,
        "max_rounds": 6,
        "reward_multiplier": 1.0,
        "items": [
            "assets/sprites/job/hs_item1.png",
            "assets/sprites/job/hs_item2.png",
            "assets/sprites/job/hs_item3.png"
        ]
        
    },
    "BSc": {
        "base_length": 5,
        "max_rounds": 7,
        "reward_multiplier": 1.5,
        "items": [
            "assets/sprites/job/bsc_item1.png",
            "assets/sprites/job/bsc_item2.png",
            "assets/sprites/job/bsc_item3.png"
        ]
    },
    "MSc": {
        "base_length": 6,
        "max_rounds": 8,
        "reward_multiplier": 2.0,
        "items": [
            "assets/sprites/job/msc_item1.png",
            "assets/sprites/job/msc_item2.png",
            "assets/sprites/job/msc_item3.png"
        ]
    },
    "PhD": {
        "base_length": 7,
        "max_rounds": 9,
        "reward_multiplier": 2.5,
        "items": [
            "assets/sprites/job/phd_item1.png",
            "assets/sprites/job/phd_item2.png",
            "assets/sprites/job/phd_item3.png"
        ]
    },
}

# Timing constants
ITEM_DISPLAY_DURATION = 0.5  # seconds to show each item during sequence display
FEEDBACK_DURATION = 2.0      # seconds for green (success) or red (fail) flash
REST_DECREASE = 20            # decrease in rest after completing a job
PRE_ANIMATION_DELAY = 0.5

def generate_task_sequence(task_count):
    """Generate a random sequence of tasks (each a number: 0, 1, or 2)."""
    sequence = [random.choice([0, 1, 2]) for _ in range(task_count)]
    print("Generated sequence:", sequence)
    return sequence

def initialize_job(education_level):
    """
    Initialize the job minigame state.
    The education level influences the starting sequence length, available desk item sprites,
    and the maximum rounds (i.e. workday length).
    """
    config = EDUCATION_CONFIG.get(education_level, EDUCATION_CONFIG["HS"])
    base_length = config["base_length"]
    max_rounds = config.get("max_rounds", 8)  # Default to 8 if not provided
    return {
        "items": config["items"],
        "sequence": generate_task_sequence(base_length),
        "input_sequence": [],
        "phase": "idle",               # "idle", "display", "input", "feedback_success", "feedback_failure"
        "phase_start_time": time.time(),
        "current_animation_index": 0,
        "mistake_count": 0,
        "score": 0,
        "current_round": 1,
        "task_count": base_length,
        "max_rounds": max_rounds,
        "completed": False,
        "high_score": 0,
        "reward_multiplier": config.get("reward_multiplier", 1.0),
    }


def update_job(job_state, controls, audio):
    """
    Update the job minigame state.
    This function implements a simple state machine with phases:
      - "display": Show sequence items one at a time.
      - "input": Accept player's input.
      - "feedback_success": Flash green when the sequence is correctly reproduced.
      - "feedback_failure": Flash red on a mistake.
    """
    current_time = time.time()

    if job_state["phase"] == "idle":
        if current_time - job_state["phase_start_time"] >= PRE_ANIMATION_DELAY:
            job_state["phase"] = "display"
            job_state["phase_start_time"] = current_time

    # Phase: Display Sequence
    elif job_state["phase"] == "display":
        if current_time - job_state["phase_start_time"] >= (PRE_ANIMATION_DELAY + ITEM_DISPLAY_DURATION):
            if job_state["current_animation_index"] < len(job_state["sequence"]) - 1:
                audio.play_sound("workElement")  # Play sound for item display
                job_state["current_animation_index"] += 1
                job_state["phase_start_time"] = current_time
            else:
                # All items have been shown; transition to input phase
                job_state["phase"] = "input"
                job_state["phase_start_time"] = current_time
                job_state["input_sequence"] = []
    
    # Phase: Input
    elif job_state["phase"] == "input":
        print(job_state['phase'])
        # Map controls to a number if a button is pressed
        input_value = None
        if controls.left_button:
            input_value = 0
        elif controls.center_button:
            input_value = 1
        elif controls.right_button:
            input_value = 2

        if input_value is not None:
            audio.play_sound("workElement")  # Play sound for item display
            job_state["last_input"] = input_value
            job_state["phase"] = "input_animation"
            job_state["phase_start_time"] = current_time
    
    elif job_state["phase"] == "input_animation":
        print(job_state['phase'])
        if current_time - job_state["phase_start_time"] >= (PRE_ANIMATION_DELAY + ITEM_DISPLAY_DURATION - 0.5):
            # Commit the input after animation
            input_value = job_state["last_input"]
            job_state["input_sequence"].append(input_value)
            index = len(job_state["input_sequence"]) - 1
            if job_state["input_sequence"][index] != job_state["sequence"][index]:
                job_state["phase"] = "feedback_failure"
                job_state["phase_start_time"] = current_time
                job_state["mistake_count"] += 1
            else:
                if len(job_state["input_sequence"]) == len(job_state["sequence"]):
                    job_state["score"] += 1
                    job_state["phase"] = "feedback_success"
                    job_state["phase_start_time"] = current_time
                else:
                    job_state["phase"] = "input"
                    job_state["phase_start_time"] = current_time
    # Phase: Feedback Success (flash green)
    elif job_state["phase"] == "feedback_success":
        audio.play_sound("success")  # Play success sound
        print(job_state['phase'])
        # In your drawing routine, you can flash green when this phase is active.
        if current_time - job_state["phase_start_time"] >= FEEDBACK_DURATION:
            # Increase difficulty for next round
            job_state["current_round"] += 1
            job_state["task_count"] += 1
            if job_state["task_count"] >= job_state["max_rounds"]:
                job_state["completed"] = True  # Workday finished
            else:
                # Generate a new sequence with increased length
                job_state["sequence"] = generate_task_sequence(job_state["task_count"])
                job_state["current_animation_index"] = 0
                job_state["phase"] = "display"
                job_state["phase_start_time"] = current_time

    # Phase: Feedback Failure (flash red)
    elif job_state["phase"] == "feedback_failure":
        audio.play_sound("failure")  # Play failure sound
        print(job_state['phase'])
        # Flash red for FEEDBACK_DURATION seconds before resetting the sequence
        if current_time - job_state["phase_start_time"] >= FEEDBACK_DURATION:
            if job_state["mistake_count"] >= 3:
                # Too many mistakes: end the job minigame
                job_state["completed"] = True
            else:
                # Replay the same sequence (reset input) after failure
                job_state["input_sequence"] = []
                job_state["phase"] = "display"
                job_state["current_animation_index"] = 0
                job_state["phase_start_time"] = current_time

def apply_job_rewards(job_state, stats):
    """
    Apply rewards (or penalties) to player stats based on job performance.
    The rewards affect money, rest, and self-esteem.
    """
    current_score = job_state["score"]
    if current_score > job_state.get("high_score", 0):
        job_state["high_score"] = current_score
    high_score = job_state.get("high_score", 1)  # Prevent division by zero

    performance = (current_score / high_score) * 100 if high_score > 0 else 0

    # Always decrease rest due to work fatigue
    stats.modify_stat("rest", -REST_DECREASE)
    # Increase safety as a benefit of having a job
    stats.modify_stat("safe", 5)

    multiplier = job_state.get("reward_multiplier", 1.0)

    # Rewards babyyyyy we ain't working that ass for free fr fr
    # proportional to education level obviouslyyyyyy
    if performance < 25:
        stats.modify_stat("money", 0)
        stats.modify_stat("esteem", -int(3 * multiplier))
    elif performance < 50:
        stats.modify_stat("money", int(2 * multiplier))
    elif performance < 75:
        stats.modify_stat("money", int(5 * multiplier))
        stats.modify_stat("esteem", int(2 * multiplier))
    elif performance < 100:
        stats.modify_stat("money", int(6 * multiplier))
        stats.modify_stat("esteem", int(3 * multiplier))
    else:
        stats.modify_stat("money", int(7 * multiplier))
        stats.modify_stat("esteem", int(5 * multiplier))

    print(f"Job Complete! Score: {current_score}, High Score: {high_score}, Performance: {performance:.1f}%")

