import time
from core.minigames.platformer import initialize_platformer

class States:
    def __init__(self):
        self.stage_of_life = "egg"  # Default stage
        self.character = "whore1"  # Default character
        self.current_screen = "home_screen"  # Default screen
        self.social_state = None  # Socializing game state
        self.selected_point_index = 0  # Default point selection
        self.animation_frame = None
        self.selected_level = None
        self.student_loan = None
        self.point_screens = [
            "food_screen", "housing_screen", "socialize_screen", 
            "education_screen", "job_screen", "hobby_screen"
        ]
        self.platformer_state = None  # Holds platformer game state

        # Age-related properties
        self.age = 0
        self.start_time = time.time()
        self.life_stages = {"egg": 10, "small": 30, "adult": 60}  # Age thresholds

    def update_life_stage(self):
        """
        Update the life stage based on the elapsed time.
        """
        elapsed_time = time.time() - self.start_time
        if self.stage_of_life == "egg" and elapsed_time > self.life_stages["egg"]:
            self.transition_to_life_stage("small")
        elif self.stage_of_life == "small" and elapsed_time > self.life_stages["small"]:
            self.transition_to_life_stage("adult")
        elif self.stage_of_life == "adult" and elapsed_time > self.life_stages["adult"]:
            self.transition_to_life_stage("dead")

    def update_education(self, level, loan):
        """
        Update education level and associated student loan.
        """
        self.education_level = level
        self.student_loan = loan
        print(f"Education Level: {level}, Student Loan: ${loan}")

    def transition_to_life_stage(self, new_stage):
        """
        Transition to a new life stage.
        """
        print(f"Transitioning from {self.stage_of_life} to {new_stage}")
        self.stage_of_life = new_stage
        self.start_time = time.time()  # Reset timer for the new stage

    def transition_to_screen(self, new_screen):
        """
        Transition to a new screen.
        """
        print(f"Transitioning to {new_screen}")
        self.current_screen = new_screen

    def cycle_point(self):
        """
        Cycle through the points on the home screen.
        """
        self.selected_point_index = (self.selected_point_index + 1) % len(self.point_screens)

    def get_current_screen_from_point(self):
        """
        Get the screen associated with the currently selected point.
        """
        return self.point_screens[self.selected_point_index]
    
    def get_sprite_folder(self):
        """
        Get the sprite folder path based on the current life stage and character.
        """
        return f"assets/sprites/{self.character}/{self.stage_of_life}"
    
    def start_platformer(self, money_stats):
        """
        Initialize the platformer minigame state.
        """
        self.platformer_state = initialize_platformer(money_stats)

    def reset_platformer(self):
        """
        Reset the platformer minigame.
        """
        self.platformer_state = None
