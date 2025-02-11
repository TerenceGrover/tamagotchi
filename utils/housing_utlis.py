import random

def calculate_housing_acceptance(housing_state, stats):
    """
    Calculates the probability of housing acceptance based on various factors.
    """
    selected_house = housing_state["housing_options"][housing_state["current_choice"]]
    base_probability = {
        "Crack House": 0.95,  # Almost always accepted
        "Apartment": 0.65,  # Decent odds
        "House": 0.30,  # More difficult
    }[selected_house["name"]]

    probability = base_probability

    # Positive Factors
    # probability += stats.stats["income"] / 2000  # Higher income, better chance
    probability += stats.stats["education"] / 100  # Higher education = slight boost
    probability += stats.stats["social"] / 150  # Being more sociable helps
    # probability += 0.05 if stats.stats["job_stability"] else -0.10  # Stable job helps


    # Racial Bias Simulation (Purely for satirical effect)
    # if "skin_color" in stats.stats and "landlord_skin_color" in housing_state:
    #     if stats.stats["skin_color"] != housing_state["landlord_skin_color"]:
    #         probability -= 0.10  # Discrimination factor (sadly, a real thing)

    # Random Landlord Mood
    probability += random.uniform(-0.10, 0.10)  # Landlord might just be feeling different today

    # Ensure probability stays between 0 and 1
    probability = max(0, min(1, probability))

    return probability
