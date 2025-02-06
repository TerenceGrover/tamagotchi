import time
import random
from utils.housing_utlis import calculate_housing_acceptance

def initialize_housing():
    return {
        "housing_options": [
            {"name": "Crack House", "sprite": "assets/sprites/housing/crack_house.png", "comfort": 10, "cost": 100},
            {"name": "Apartment", "sprite": "assets/sprites/housing/apartment.png", "comfort": 30, "cost": 500},
            {"name": "House", "sprite": "assets/sprites/housing/house.png", "comfort": 80, "cost": 2000},
        ],
        "current_choice": 0,
        "house_selected": False,
        "countdown_active": False,
        "reaction_active": False,
        "reaction_start_time": None,
        "reaction_threshold": None,
        "reaction_result": None,  # Pass or fail
        "reaction_result_display_time": None,  # Timestamp for when to remove result
        "countdown_timer": 3,  # Start with a 3-second countdown
        "random_timeout_active": False,  # Tracks random timeout
        "random_timeout_duration": None,  # Duration of the random timeout
        "random_timeout_start": None,  # When the random timeout began
        "pending": False,  # Tracks if a housing application is pending
        "pending_start_time": None,  # When the pending state began
        "pending_wait_time": random.randint(15, 30),  # Time to wait before accepting or denying the application
    }



def reset_housing_state(housing_state):
    """
    Reset all the dynamic states in the housing_state to their initial values.
    """
    keys_to_reset = [
        "house_selected",
        "countdown_active",
        "reaction_active",
        "reaction_start_time",
        "reaction_threshold",
        "reaction_result",
        "countdown_timer",
        "random_timeout_active",
        "random_timeout_duration",
        "random_timeout_start",
    ]
    for key in keys_to_reset:
        housing_state[key] = None if (key.endswith("_start") or key.endswith('_result')) else False

    # Reset countdown and timer-specific values explicitly
    housing_state["countdown_timer"] = 3  # Reset countdown to initial value


def handle_housing_input(housing_state, stats, controls, fps, states):
    """
    Handle the housing state input and update game logic.
    """
    
    if housing_state["pending"]:
        # If in a pending state, pressing the left button resets the state
        if controls.left_button or controls.center_button or controls.right_button:
            states.transition_to_screen("home_screen")
            return
        
        if time.time() - housing_state["pending_start_time"] > housing_state["pending_wait_time"]:
            # Calculate housing acceptance based on probability
            probability = calculate_housing_acceptance(housing_state, stats)
            if random.random() < probability:
                housing_state["pending"] = False
                housing_state["reaction_result"] = None
                housing_state["application_result"] = "Accepted"
            else:
                housing_state["pending"] = False
                housing_state["reaction_result"] = None
                housing_state["application_result"] = "Denied"
        return  # Prevent further interactions while pending
        
    else: 
        if controls.left_button:
            states.transition_to_screen("home_screen")
            reset_housing_state(housing_state)  # Use the helper function to reset the state
            return

    # Handle reaction result display duration
    if housing_state["reaction_result"] is not None:
        if time.time() - housing_state["reaction_result_display_time"] > 2:  # Show animation for 2 seconds
            housing_state["reaction_result"] = None
            housing_state["pending"] = True  # Move to pending state
            housing_state["pending_start_time"] = time.time()
        return  # Prevent further interactions while animation is playing

    if not housing_state["house_selected"]:
        # Cycle through housing options
        if controls.right_button:
            housing_state["current_choice"] = (housing_state["current_choice"] + 1) % len(housing_state["housing_options"])

        # Select the current house
        if controls.center_button:
            housing_state["house_selected"] = True
            housing_state["countdown_active"] = True
            housing_state["countdown_timer"] = 3  # Reset countdown timer
            print(f"Selected house: {housing_state['housing_options'][housing_state['current_choice']]['name']}")

    elif housing_state["countdown_active"]:
        # Handle countdown logic
        if housing_state["countdown_timer"] > 0:
            housing_state["countdown_timer"] -= 1 / fps  # Decrement countdown timer
        else:
            housing_state["countdown_active"] = False
            housing_state["random_timeout_active"] = True
            housing_state["random_timeout_duration"] = random.uniform(0.1, 6.0)  # Random timeout duration
            housing_state["random_timeout_start"] = time.time()

    elif housing_state["random_timeout_active"]:
        # Handle random timeout logic
        elapsed_time = time.time() - housing_state["random_timeout_start"]
        if elapsed_time >= housing_state["random_timeout_duration"]:
            housing_state["random_timeout_active"] = False
            housing_state["reaction_active"] = True
            housing_state["reaction_start_time"] = time.time()

            # Set reaction threshold based on house comfort
            selected_house = housing_state["housing_options"][housing_state["current_choice"]]
            comfort = selected_house["comfort"]
            housing_state["reaction_threshold"] = max(1.0, 3.0 - (comfort / 20))  # Example formula

    elif housing_state["reaction_active"]:
        # Handle reaction timing
        reaction_time = time.time() - housing_state["reaction_start_time"]
        if controls.center_button:  # Player reacts
            if reaction_time <= housing_state["reaction_threshold"]:
                housing_state["reaction_result"] = "pass"
                print("Reaction success!")
            else:
                housing_state["reaction_result"] = "fail"
                print("Reaction too slow!")

            housing_state["reaction_active"] = False
            housing_state["reaction_result_display_time"] = time.time()  # Set time to delay clearing the result

        elif reaction_time > housing_state["reaction_threshold"] + 1.0:  # 1-second grace period
            housing_state["reaction_result"] = "fail"
            print("Reaction failed (timeout)!")
            housing_state["reaction_active"] = False
            housing_state["reaction_result_display_time"] = time.time()  # Set time to delay clearing the result

