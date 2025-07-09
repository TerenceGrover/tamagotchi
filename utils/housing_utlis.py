import random

def calculate_housing_acceptance(housing_state, stats):
    """
    Calculates the probability of housing acceptance based on various factors.
    """
    selected_house = housing_state["housing_options"][housing_state["current_choice"]]
    base_probability = {
        "Crack House": 0.99,
        "Apartment": 0.7, 
        "House": 0.5,
        "Sex Dungeon": 0.35
    }[selected_house["name"]]

    probability = base_probability

    # Positive Factors
    # probability += stats.stats["income"] / 2000  # Higher income, better chance

    education_num = {
        "DropOut": 0.0,
        "HighSchool": 0.05,
        "College": 0.1,
        "MSc": 0.15,
        "PhD": 0.2
    }

    probability += education_num.get(stats.stats["education"], 0.0)  # Higher education, better chance
    probability += stats.stats["social"] / 150  # Being more sociable helps


    if "skin_color" in stats.stats and housing_state["real_estate_agent"] and "skin_color" in housing_state["real_estate_agent"]:
        if stats.stats["skin_color"] != housing_state["real_estate_agent"]["skin_color"]:
            probability -= 0.05

    # Random Landlord Mood
    probability += random.uniform(-0.10, 0.10)
    probability = max(0.05, min(1, probability))

    return probability
