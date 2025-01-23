import time
import pygame

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
        "countdown_timer": 3,  # Start with a 5-second countdown
    }


import time
import random
import pygame

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
        "countdown_timer": 3,  # Start with a 3-second countdown
        "random_timeout_active": False,  # Tracks random timeout
        "random_timeout_duration": None,  # Duration of the random timeout
        "random_timeout_start": None,  # When the random timeout began
    }


def handle_housing_input(housing_state, controls, fps):
    """
    Handle the housing state input and update game logic.
    """
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
            housing_state["random_timeout_duration"] = random.uniform(0.5, 10.0)  # Random timeout duration
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

        elif reaction_time > housing_state["reaction_threshold"] + 1.0:  # 1-second grace period
            housing_state["reaction_result"] = "fail"
            print("Reaction failed (timeout)!")
            housing_state["reaction_active"] = False


