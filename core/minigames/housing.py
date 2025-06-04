import time
import random
from utils.housing_utlis import calculate_housing_acceptance

# Define thresholds for each house option (by index)
HOUSE_MONEY_THRESHOLDS = [10, 25, 50, 75]

def initialize_housing():
    return {
        "housing_options": [
            {"name": "Crack House", "sprite": "assets/sprites/housing/crack_house.png", "comfort": 20, "cost": 5},
            {"name": "Apartment", "sprite": "assets/sprites/housing/apartment.png", "comfort": 50, "cost": 10},
            {"name": "House", "sprite": "assets/sprites/housing/house.png", "comfort": 100, "cost": 15},
            {"name": "Sex Dungeon", "sprite": "assets/sprites/housing/castle.png", "comfort": 200, "cost": 20},
        ],
        "current_choice": 0,
        "house_selected": False,
        "countdown_active": False,
        "reaction_active": False,
        "reaction_start_time": None,
        "reaction_threshold": None,
        "reaction_result": None,
        "reaction_result_display_time": 0, 
        "countdown_timer": 3,
        "random_timeout_active": False, 
        "random_timeout_duration": None, 
        "random_timeout_start": None, 
        "pending": False,
        "pending_start_time": None,
        "current_home": None,
        "pending_wait_time": random.randint(15, 30),
        "real_estate_agent": None,
    }

def reset_housing_state(housing_state):
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
    housing_state["countdown_timer"] = 3

def assign_real_estate_agent(housing_state):
    agent_skins = ["yellow", "orange", "green"]
    agent_table = {"green": 1, "orange": 2, "yellow": 3}
    chosen_skin = random.choice(agent_skins)
    housing_state["real_estate_agent"] = {
        "skin_color": chosen_skin,
        "sprite": f"assets/sprites/otherTama/tama{agent_table[chosen_skin]}.png",
    }

def handle_housing_input(housing_state, stats, controls, fps, states, audio):
    """
    Update housing state.
    Only allow selecting a house if stats.money meets the threshold for that option.
    """
    current_threshold = HOUSE_MONEY_THRESHOLDS[housing_state["current_choice"]]

    if controls.left_button:
        states.transition_to_screen("home_screen")
        audio.play_sound("click")
        return
    
    if housing_state["pending"]:
        if controls.left_button or controls.center_button or controls.right_button:
            states.transition_to_screen("home_screen")
            return
        elif (time.time() - housing_state["pending_start_time"] > housing_state["pending_wait_time"] 
              and housing_state["current_home"] is None):
            probability = calculate_housing_acceptance(housing_state, stats)
            if random.random() < probability:
                selected_house = housing_state["housing_options"][housing_state["current_choice"]]
                housing_state["current_home"] = selected_house
                housing_state["pending"] = False
                housing_state["reaction_result"] = None
                housing_state["application_result"] = "Accepted"
                stats.modify_stat("rest", selected_house["comfort"] // 2)
                stats.modify_stat("safe", selected_house["comfort"] // 2)
                stats.modify_stat("money", -selected_house["cost"])
                audio.play_sound("success")
                print(f"✅ Moved into {selected_house['name']}.")
            else:
                housing_state["pending"] = False
                housing_state["reaction_result"] = None
                housing_state["application_result"] = "Denied"
                audio.play_sound("failure")
                
        if controls.left_button:
            states.transition_to_screen("home_screen")
            reset_housing_state(housing_state)
            audio.play_sound("click")
            return

    # Prevent further interactions if we are showing feedback
    if housing_state["reaction_result"] is not None:
        if housing_state["reaction_result_display_time"] is None:
            housing_state["reaction_result_display_time"] = time.time()
        if time.time() - housing_state["reaction_result_display_time"] > 2:
            if housing_state["reaction_result"] == "pass":
                housing_state["pending"] = True
                housing_state["pending_start_time"] = time.time()
            elif housing_state["reaction_result"] == "fail":
                if controls.left_button or controls.center_button or controls.right_button:
                    reset_housing_state(housing_state)
            housing_state["reaction_result"] = None
            housing_state["reaction_result_display_time"] = None
        return

    if not housing_state["house_selected"]:
        # Cycle through options
        if controls.right_button:
            housing_state["current_choice"] = (housing_state["current_choice"] + 1) % len(housing_state["housing_options"])
            audio.play_sound("click")
        # When selecting a house, only allow it if money is high enough.
        if controls.center_button:
            if stats.stats["money"] >= current_threshold:
                audio.play_sound("suitcaseOpen")
                housing_state["house_selected"] = True
                housing_state["countdown_active"] = True
                housing_state["countdown_timer"] = 3
                print(f"Selected house: {housing_state['housing_options'][housing_state['current_choice']]['name']}")
            else:
                print("Not enough money for this house!")
                # Optionally, you can add a visual lock/flash here.
    elif housing_state["countdown_active"]:
        if housing_state["countdown_timer"] > 0:
            housing_state["countdown_timer"] -= 1 / fps
        else:
            housing_state["countdown_active"] = False
            housing_state["random_timeout_active"] = True
            housing_state["random_timeout_duration"] = random.uniform(0.1, 6.0)
            housing_state["random_timeout_start"] = time.time()
    elif housing_state["random_timeout_active"]:
        elapsed_time = time.time() - housing_state["random_timeout_start"]
        if elapsed_time >= housing_state["random_timeout_duration"]:
            audio.play_sound("jump")
            housing_state["random_timeout_active"] = False
            housing_state["reaction_active"] = True
            housing_state["reaction_start_time"] = time.time()
            selected_house = housing_state["housing_options"][housing_state["current_choice"]]
            comfort = selected_house["comfort"]
            housing_state["reaction_threshold"] = max(1.0, 3.0 - (comfort / 20))
            if housing_state["real_estate_agent"] is None:
                assign_real_estate_agent(housing_state)
    elif housing_state["reaction_active"]:
        reaction_time = time.time() - housing_state["reaction_start_time"]
        if controls.center_button:
            if reaction_time <= housing_state["reaction_threshold"]:
                housing_state["reaction_result"] = "pass"
                audio.play_sound("success")
                print("Reaction success!")
            else:
                housing_state["reaction_result"] = "fail"
                audio.play_sound("failure")
                print("Reaction too slow!")
            housing_state["reaction_active"] = False
            housing_state["reaction_result_display_time"] = time.time()
        elif reaction_time > housing_state["reaction_threshold"] + 0.5:
            if housing_state["reaction_result"] is None:
                housing_state["reaction_result"] = "fail"
                print("Reaction failed (timeout)!")
                housing_state["reaction_active"] = False
                housing_state["reaction_result_display_time"] = time.time()
